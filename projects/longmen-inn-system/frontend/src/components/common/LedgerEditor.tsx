import React, { useState, useEffect } from 'react';
import { Modal, Button, message, Spin, Alert } from 'antd';
import { ReloadOutlined, SyncOutlined } from '@ant-design/icons';
import { getLedger, generateLedger } from '../../services/fileService';

interface LedgerEditorProps {
  visible: boolean;
  onClose: () => void;
  onRefresh?: () => void; // 保存或重新加载后回调，刷新父组件数据
}

const LedgerEditor: React.FC<LedgerEditorProps> = ({ visible, onClose, onRefresh }) => {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  const loadLedger = async () => {
    setLoading(true);
    try {
      const result = await getLedger();
      setContent(result.content);
      onRefresh?.();
    } catch (error: any) {
      message.error(`加载失败: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (visible) {
      loadLedger();
    }
  }, [visible]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      // 从 DB 重新生成 LEDGER.md
      await generateLedger(true);
      message.success('账本已从数据库重新生成');
      await loadLedger();
      onRefresh?.();
    } catch (error: any) {
      message.error(`生成失败: ${error.message}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <Modal
      title={
        <span style={{ color: '#B22222', fontWeight: 600 }}>
          📜 营业总账
        </span>
      }
      open={visible}
      onCancel={onClose}
      width={1000}
      footer={[
        <Button key="reload" icon={<ReloadOutlined />} onClick={loadLedger} disabled={loading}>
          刷新
        </Button>,
        <Button key="generate" type="primary" icon={<SyncOutlined spin={generating} />} loading={generating} onClick={handleGenerate}>
          从数据库重新生成
        </Button>,
        <Button key="close" type="default" onClick={onClose}>
          关闭
        </Button>,
      ]}
      bodyStyle={{ padding: 0 }}
    >
      <Spin spinning={loading}>
        <Alert
          message="账本说明"
          description={
            <span>
              营业总账现在由数据库实时导出生成。任务操作请使用{' '}
              <strong>任务看板</strong>（增删改查），账本将自动反映最新状态。
              如需手动刷新，请点击「从数据库重新生成」。
            </span>
          }
          type="info"
          showIcon
          style={{ margin: 12 }}
        />
        <pre
          style={{
            margin: 0,
            padding: '12px 16px',
            minHeight: 500,
            maxHeight: 600,
            overflow: 'auto',
            fontFamily: 'Consolas, Monaco, monospace',
            fontSize: 12,
            lineHeight: 1.6,
            background: '#f5f5f5',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}
        >
          {content}
        </pre>
      </Spin>
    </Modal>
  );
};

export default LedgerEditor;
