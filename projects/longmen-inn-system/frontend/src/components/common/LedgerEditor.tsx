import React, { useState, useEffect } from 'react';
import { Modal, Input, Button, message, Spin } from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';
import { getLedger, saveLedger } from '../../services/fileService';

const { TextArea } = Input;

interface LedgerEditorProps {
  visible: boolean;
  onClose: () => void;
}

const LedgerEditor: React.FC<LedgerEditorProps> = ({ visible, onClose }) => {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const loadLedger = async () => {
    setLoading(true);
    try {
      const result = await getLedger();
      setContent(result.content);
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

  const handleSave = async () => {
    setSaving(true);
    try {
      const result = await saveLedger(content);
      message.success(result.message);
      onClose();
    } catch (error: any) {
      message.error(`保存失败: ${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal
      title={
        <span style={{ color: '#B22222', fontWeight: 600 }}>
          📜 营业总账编辑器
        </span>
      }
      open={visible}
      onCancel={onClose}
      width={900}
      footer={[
        <Button key="reload" icon={<ReloadOutlined />} onClick={loadLedger} disabled={loading}>
          重新加载
        </Button>,
        <Button key="cancel" onClick={onClose}>
          取消
        </Button>,
        <Button
          key="save"
          type="primary"
          icon={<SaveOutlined />}
          loading={saving}
          onClick={handleSave}
          style={{ background: '#B22222', borderColor: '#B22222' }}
        >
          保存并同步
        </Button>,
      ]}
      bodyStyle={{ padding: 0 }}
    >
      <Spin spinning={loading}>
        <TextArea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="LEDGER.md 内容..."
          style={{
            minHeight: 500,
            fontFamily: 'Consolas, Monaco, monospace',
            fontSize: 13,
            lineHeight: 1.6,
            border: 'none',
            borderRadius: 0,
          }}
        />
      </Spin>
    </Modal>
  );
};

export default LedgerEditor;
