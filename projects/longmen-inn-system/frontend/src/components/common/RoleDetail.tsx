import React, { useState, useEffect } from 'react';
import { Modal, Spin, Empty, Avatar, Typography, List, Tag } from 'antd';
import { UserOutlined, FileTextOutlined, FileOutlined, FolderOutlined } from '@ant-design/icons';
import { getRoleFile, listAgentRoleFiles, type RoleFile } from '../../services/fileService';
import type { Agent } from '../../types/agent';

const { Title, Text } = Typography;

interface RoleDetailProps {
  visible: boolean;
  agent: Agent | null;
  onClose: () => void;
}

const RoleDetail: React.FC<RoleDetailProps> = ({ visible, agent, onClose }) => {
  const [files, setFiles] = useState<RoleFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<string>('IDENTITY.md');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [filesLoading, setFilesLoading] = useState(false);

  useEffect(() => {
    if (visible && agent) {
      loadFiles();
      loadFileContent('IDENTITY.md');
    }
  }, [visible, agent]);

  const loadFiles = async () => {
    if (!agent) return;
    
    setFilesLoading(true);
    try {
      const result = await listAgentRoleFiles(agent.agent_id);
      setFiles(result.files);
    } catch (error) {
      setFiles([]);
    } finally {
      setFilesLoading(false);
    }
  };

  const loadFileContent = async (filePath: string) => {
    if (!agent) return;
    
    setLoading(true);
    try {
      const result = await getRoleFile(agent.agent_id, filePath);
      setContent(result.content);
      setSelectedFile(filePath);
    } catch (error) {
      setContent('');
    } finally {
      setLoading(false);
    }
  };

  const renderMarkdown = (text: string) => {
    return text.split('\n').map((line, index) => {
      if (line.startsWith('# ')) {
        return <h1 key={index} style={{ fontSize: 22, color: '#B22222', borderBottom: '2px solid #B22222', paddingBottom: 8, marginBottom: 16 }}>{line.slice(2)}</h1>;
      }
      if (line.startsWith('## ')) {
        return <h2 key={index} style={{ fontSize: 18, color: '#8B4513', marginTop: 16, marginBottom: 8 }}>{line.slice(3)}</h2>;
      }
      if (line.startsWith('### ')) {
        return <h3 key={index} style={{ fontSize: 15, color: '#654321', marginTop: 12, marginBottom: 6 }}>{line.slice(4)}</h3>;
      }
      if (line.startsWith('- ') || line.startsWith('* ')) {
        return <li key={index} style={{ marginLeft: 20, color: '#333', marginBottom: 4 }}>{line.slice(2)}</li>;
      }
      if (line.trim() === '---') {
        return <hr key={index} style={{ border: 'none', borderTop: '1px solid #ddd', margin: '16px 0' }} />;
      }
      if (line.trim() === '') {
        return <br key={index} />;
      }
      return <p key={index} style={{ margin: '4px 0', color: '#333', lineHeight: 1.8 }}>{line}</p>;
    });
  };

  const getFileIcon = (file: RoleFile) => {
    if (file.type === 'md') {
      return <FileTextOutlined style={{ color: '#B22222' }} />;
    }
    if (file.type === 'json') {
      return <FileOutlined style={{ color: '#1890ff' }} />;
    }
    return <FileOutlined />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  };

  return (
    <Modal
      title={null}
      open={visible}
      onCancel={onClose}
      footer={null}
      width={900}
      bodyStyle={{ padding: 0 }}
    >
      {agent && (
        <div style={{ display: 'flex', minHeight: 500 }}>
          {/* 左侧文件列表 */}
          <div style={{ 
            width: 240, 
            borderRight: '1px solid #E8DCC8', 
            background: '#FFFAF0',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <div style={{ 
              padding: 16, 
              borderBottom: '1px solid #E8DCC8',
              display: 'flex',
              alignItems: 'center',
              gap: 12
            }}>
              <Avatar
                size={40}
                icon={<UserOutlined />}
                style={{ backgroundColor: '#B22222' }}
              >
                {agent.name?.[0]}
              </Avatar>
              <div>
                <Title level={5} style={{ margin: 0, color: '#B22222' }}>
                  {agent.name}
                </Title>
                <Text type="secondary" style={{ fontSize: 12 }}>{agent.agent_id}</Text>
              </div>
            </div>
            
            <Spin spinning={filesLoading}>
              <List
                dataSource={files}
                style={{ flex: 1, overflow: 'auto' }}
                renderItem={(file) => (
                  <List.Item
                    onClick={() => loadFileContent(file.path)}
                    style={{
                      padding: '8px 16px',
                      cursor: 'pointer',
                      background: selectedFile === file.path ? '#F5E6D3' : 'transparent',
                      borderLeft: selectedFile === file.path ? '3px solid #B22222' : '3px solid transparent',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, width: '100%' }}>
                      {getFileIcon(file)}
                      <div style={{ flex: 1, overflow: 'hidden' }}>
                        <div style={{ 
                          fontSize: 13, 
                          color: '#333',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}>
                          {file.name}
                        </div>
                        <Text type="secondary" style={{ fontSize: 11 }}>
                          {formatFileSize(file.size)}
                        </Text>
                      </div>
                    </div>
                  </List.Item>
                )}
              />
            </Spin>
          </div>

          {/* 右侧内容预览 */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <div style={{ 
              padding: '12px 16px', 
              borderBottom: '1px solid #E8DCC8',
              background: '#F5F0E8',
              display: 'flex',
              alignItems: 'center',
              gap: 8
            }}>
              <FileTextOutlined style={{ color: '#B22222' }} />
              <Text strong style={{ color: '#5D4037' }}>{selectedFile}</Text>
              <Tag color={selectedFile.endsWith('.md') ? 'red' : 'blue'} style={{ marginLeft: 'auto' }}>
                {selectedFile.endsWith('.md') ? 'Markdown' : 'JSON'}
              </Tag>
            </div>
            
            <Spin spinning={loading}>
              <div style={{ 
                flex: 1, 
                overflow: 'auto', 
                padding: 16,
                background: '#fff'
              }}>
                {content ? (
                  <div style={{ lineHeight: 1.8 }}>
                    {renderMarkdown(content)}
                  </div>
                ) : (
                  <Empty description="暂无内容" style={{ marginTop: 60 }} />
                )}
              </div>
            </Spin>
          </div>
        </div>
      )}
    </Modal>
  );
};

export default RoleDetail;
