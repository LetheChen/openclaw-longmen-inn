#!/usr/bin/env python3
"""
Agent 活动记录 API 测试脚本
测试 T-20260324-001 任务：Agent活动记录API开发
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def test_create_activity():
    """测试创建活动记录"""
    print("\n=== 测试创建活动记录 ===")
    
    # 测试1: 创建任务完成活动
    data = {
        "agent_id": "chef",
        "activity_type": "task_completed",
        "title": "完成了任务 T-20260324-001",
        "description": "Agent活动记录API开发完成",
        "related_task_id": 1,
        "related_task_title": "Agent活动记录API开发",
        "metadata": {"task_key": "T-20260324-001", "hours_spent": 2}
    }
    
    response = requests.post(f"{BASE_URL}/agents/activities", json=data)
    print(f"创建任务完成活动: {response.status_code}")
    if response.status_code == 201:
        print(f"  响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.json()
    else:
        print(f"  错误: {response.text}")
        return None


def test_create_login_activity():
    """测试创建登录活动"""
    print("\n=== 测试创建登录活动 ===")
    
    data = {
        "agent_id": "painter",
        "activity_type": "login",
        "title": "伙计登录系统",
        "description": "画师登录龙门客栈",
        "metadata": {"ip": "192.168.1.100"}
    }
    
    response = requests.post(f"{BASE_URL}/agents/activities", json=data)
    print(f"创建登录活动: {response.status_code}")
    if response.status_code == 201:
        print(f"  响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.json()
    else:
        print(f"  错误: {response.text}")
        return None


def test_create_longmenling_activity():
    """测试创建龙门令发放活动"""
    print("\n=== 测试创建龙门令发放活动 ===")
    
    data = {
        "agent_id": "chef",
        "activity_type": "longmenling_issued",
        "title": "获得龙门令奖励",
        "description": "完成T-20260324-001任务，获得50龙门令",
        "metadata": {"amount": 50, "reason": "任务完成奖励"}
    }
    
    response = requests.post(f"{BASE_URL}/agents/activities", json=data)
    print(f"创建龙门令发放活动: {response.status_code}")
    if response.status_code == 201:
        print(f"  响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.json()
    else:
        print(f"  错误: {response.text}")
        return None


def test_query_activities():
    """测试查询活动记录"""
    print("\n=== 测试查询所有活动记录 ===")
    
    response = requests.get(f"{BASE_URL}/agents/activities?limit=10")
    print(f"查询所有活动: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"  总数: {result['total']}")
        print(f"  返回: {len(result['items'])} 条")
        for item in result['items'][:3]:
            print(f"    - [{item['activity_type']}] {item['title']} ({item['agent_name']})")
        return result
    else:
        print(f"  错误: {response.text}")
        return None


def test_query_by_agent():
    """测试按Agent过滤"""
    print("\n=== 测试按Agent过滤 ===")
    
    response = requests.get(f"{BASE_URL}/agents/activities?agent_id=chef&limit=10")
    print(f"按agent_id=chef过滤: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"  总数: {result['total']}")
        return result
    else:
        print(f"  错误: {response.text}")
        return None


def test_query_by_type():
    """测试按类型过滤"""
    print("\n=== 测试按类型过滤 ===")
    
    response = requests.get(f"{BASE_URL}/agents/activities?activity_type=task_completed&limit=10")
    print(f"按activity_type=task_completed过滤: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"  总数: {result['total']}")
        return result
    else:
        print(f"  错误: {response.text}")
        return None


def test_query_by_timerange():
    """测试按时间范围过滤"""
    print("\n=== 测试按时间范围过滤 ===")
    
    # 获取最近24小时的活动
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    
    response = requests.get(
        f"{BASE_URL}/agents/activities",
        params={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "limit": 10
        }
    )
    print(f"按时间范围过滤 (最近24小时): {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"  总数: {result['total']}")
        return result
    else:
        print(f"  错误: {response.text}")
        return None


def test_invalid_activity_type():
    """测试无效活动类型"""
    print("\n=== 测试无效活动类型 ===")
    
    data = {
        "agent_id": "chef",
        "activity_type": "invalid_type",
        "title": "测试无效类型"
    }
    
    response = requests.post(f"{BASE_URL}/agents/activities", json=data)
    print(f"无效活动类型: {response.status_code}")
    if response.status_code == 400:
        print(f"  正确拒绝: {response.json()['detail']}")
    else:
        print(f"  意外响应: {response.text}")


def test_nonexistent_agent():
    """测试不存在的Agent"""
    print("\n=== 测试不存在的Agent ===")
    
    data = {
        "agent_id": "nonexistent",
        "activity_type": "login",
        "title": "测试不存在Agent"
    }
    
    response = requests.post(f"{BASE_URL}/agents/activities", json=data)
    print(f"不存在的Agent: {response.status_code}")
    if response.status_code == 404:
        print(f"  正确返回404: {response.json()['detail']}")
    else:
        print(f"  意外响应: {response.text}")


if __name__ == "__main__":
    print("=" * 60)
    print("Agent 活动记录 API 测试")
    print("=" * 60)
    
    # 首先确保服务器正在运行
    try:
        response = requests.get("http://localhost:8000/docs")
        print(f"服务器状态: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请先启动服务器")
        print("运行: uvicorn app.main:app --reload")
        exit(1)
    
    # 运行测试
    test_create_activity()
    test_create_login_activity()
    test_create_longmenling_activity()
    test_query_activities()
    test_query_by_agent()
    test_query_by_type()
    test_query_by_timerange()
    test_invalid_activity_type()
    test_nonexistent_agent()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
