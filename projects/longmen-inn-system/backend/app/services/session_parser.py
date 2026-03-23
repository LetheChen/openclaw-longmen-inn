"""
龙门客栈业务管理系统 - 会话解析服务
=====================================
作者: 老板娘 (凤老板)

解析OpenClaw Agent会话JSONL文件，提取活动记录
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import os


class SessionParser:
    """OpenClaw会话JSONL解析器"""

    def __init__(self, base_path: str = None):
        """
        初始化解析器
        
        Args:
            base_path: OpenClaw agents目录路径，默认为 ~/.openclaw/agents
        """
        if base_path:
            self.base_path = Path(base_path)
        else:
            self.base_path = Path.home() / ".openclaw" / "agents"

    def get_session_files(self, agent_id: str) -> List[Path]:
        """
        获取Agent所有会话文件
        
        Args:
            agent_id: Agent ID (如 chef, main, innkeeper)
            
        Returns:
            会话文件列表，按时间倒序排列
        """
        sessions_dir = self.base_path / agent_id / "sessions"
        if not sessions_dir.exists():
            return []
        
        # 获取所有.jsonl文件（排除reset文件）
        session_files = [
            f for f in sessions_dir.glob("*.jsonl")
            if ".reset." not in f.name
        ]
        
        # 按修改时间倒序排列
        return sorted(
            session_files,
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        解析单行JSONL记录
        
        Args:
            line: JSONL文件中的一行
            
        Returns:
            解析后的活动记录字典，解析失败返回None
        """
        try:
            data = json.loads(line.strip())
            event_type = data.get("type")
            
            if event_type == "message":
                return self._parse_message(data)
            elif event_type == "tool_use":
                return self._parse_tool_use(data)
            elif event_type == "tool_result":
                return self._parse_tool_result(data)
            else:
                # 其他事件类型暂时忽略
                return None
                
        except json.JSONDecodeError:
            return None
        except Exception as e:
            print(f"解析行失败: {e}")
            return None

    def _parse_message(self, data: Dict) -> Dict[str, Any]:
        """解析消息事件"""
        message = data.get("message", {})
        role = message.get("role", "unknown")
        content = message.get("content", [])
        
        # 提取文本内容
        text_content = ""
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_content += item.get("text", "")
            elif isinstance(item, str):
                text_content += item
        
        return {
            "type": "activity",
            "action_type": "message",
            "timestamp": self._parse_timestamp(data.get("timestamp")),
            "role": role,
            "action_detail": f"{role}消息",
            "output_preview": text_content[:200] if text_content else None,
            "is_error": False,
            "raw": {
                "content_preview": text_content[:500] if text_content else None
            }
        }

    def _parse_tool_use(self, data: Dict) -> Dict[str, Any]:
        """解析工具调用事件"""
        tool_name = data.get("name", "unknown")
        tool_input = data.get("input", {})
        
        # 生成预览
        input_preview = json.dumps(tool_input, ensure_ascii=False)[:200]
        
        return {
            "type": "activity",
            "action_type": "tool_use",
            "timestamp": self._parse_timestamp(data.get("timestamp")),
            "tool_name": tool_name,
            "action_detail": f"调用工具: {tool_name}",
            "output_preview": input_preview,
            "is_error": False,
            "raw": {
                "input": tool_input
            }
        }

    def _parse_tool_result(self, data: Dict) -> Dict[str, Any]:
        """解析工具返回事件"""
        tool_use_id = data.get("tool_use_id", "unknown")
        content = data.get("content", "")
        is_error = data.get("is_error", False)
        
        # 截取预览
        if isinstance(content, str):
            preview = content[:200]
        elif isinstance(content, list):
            # 可能是content块列表
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_parts.append(item)
            preview = "".join(text_parts)[:200]
        else:
            preview = str(content)[:200]
        
        return {
            "type": "activity",
            "action_type": "tool_result",
            "timestamp": self._parse_timestamp(data.get("timestamp")),
            "tool_name": None,
            "action_detail": "工具返回" + (" (错误)" if is_error else ""),
            "output_preview": preview,
            "is_error": is_error,
            "raw": {
                "tool_use_id": tool_use_id
            }
        }

    def _parse_timestamp(self, ts: Any) -> Optional[datetime]:
        """解析时间戳"""
        if ts is None:
            return None
        
        if isinstance(ts, datetime):
            return ts
        
        if isinstance(ts, str):
            try:
                # ISO格式
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except:
                pass
        
        if isinstance(ts, (int, float)):
            # Unix时间戳（毫秒或秒）
            if ts > 1e12:  # 毫秒
                ts = ts / 1000
            try:
                return datetime.fromtimestamp(ts)
            except:
                pass
        
        return None

    def get_recent_activities(
        self,
        agent_id: str,
        limit: int = 50,
        action_type: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取Agent最近活动记录
        
        Args:
            agent_id: Agent ID
            limit: 返回数量限制
            action_type: 动作类型过滤 (message, tool_use, tool_result)
            session_id: 指定会话ID
            
        Returns:
            活动记录列表
        """
        activities = []
        
        # 获取会话文件
        if session_id:
            # 指定会话
            session_file = self.base_path / agent_id / "sessions" / f"{session_id}.jsonl"
            if session_file.exists():
                files = [session_file]
            else:
                files = []
        else:
            # 所有会话
            files = self.get_session_files(agent_id)
        
        for file_path in files:
            if len(activities) >= limit:
                break
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if len(activities) >= limit:
                            break
                        
                        activity = self.parse_line(line)
                        if activity:
                            # 类型过滤
                            if action_type and activity.get("action_type") != action_type:
                                continue
                            activities.append(activity)
            except Exception as e:
                print(f"读取会话文件失败 {file_path}: {e}")
                continue
        
        return activities

    def get_agent_status(self, agent_id: str) -> str:
        """
        根据最近活动推断Agent状态
        
        Args:
            agent_id: Agent ID
            
        Returns:
            状态字符串: idle, busy, offline
        """
        sessions = self.get_session_files(agent_id)
        
        if not sessions:
            return "offline"
        
        # 检查最近一个会话文件的最后修改时间
        latest_file = sessions[0]
        try:
            mtime = datetime.fromtimestamp(latest_file.stat().st_mtime)
            now = datetime.now()
            delta_seconds = (now - mtime).total_seconds()
            
            if delta_seconds < 300:  # 5分钟内
                return "busy"
            elif delta_seconds < 3600:  # 1小时内
                return "idle"
            else:
                return "offline"
        except:
            return "offline"

    def scan_workspace(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        扫描Agent工作空间文件
        
        Args:
            agent_id: Agent ID
            
        Returns:
            文件列表
        """
        workspace_dir = self.base_path / agent_id / "workspace"
        
        if not workspace_dir.exists():
            return []
        
        files = []
        for path in workspace_dir.rglob("*"):
            if path.is_file():
                try:
                    stat = path.stat()
                    rel_path = path.relative_to(workspace_dir)
                    
                    # 判断文件类型
                    ext = path.suffix.lower()
                    if ext in [".py", ".js", ".ts", ".tsx", ".java", ".go", ".rs"]:
                        file_type = "code"
                    elif ext in [".md", ".txt", ".rst", ".doc", ".docx"]:
                        file_type = "doc"
                    elif ext in [".png", ".jpg", ".svg", ".fig"]:
                        file_type = "design"
                    elif ext in [".json", ".yaml", ".yml", ".toml", ".ini"]:
                        file_type = "config"
                    else:
                        file_type = "file"
                    
                    files.append({
                        "path": str(rel_path),
                        "type": "file",
                        "file_type": file_type,
                        "last_modified": datetime.fromtimestamp(stat.st_mtime),
                        "size": stat.st_size
                    })
                except Exception as e:
                    continue
        
        return files


# 创建全局实例
session_parser = SessionParser()