import React from 'react';
import { Card, Statistic, Row, Col } from 'antd';
import type { StatisticProps } from 'antd';
import './StatCard.css';

export interface StatCardProps {
  title: string;
  value: number | string;
  prefix?: React.ReactNode;
  suffix?: React.ReactNode;
  precision?: number;
  valueStyle?: React.CSSProperties;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: string | number;
  icon?: React.ReactNode;
  color?: string;
  backgroundColor?: string;
  loading?: boolean;
  className?: string;
  onClick?: () => void;
  footer?: React.ReactNode;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  prefix,
  suffix,
  precision,
  valueStyle,
  trend,
  trendValue,
  icon,
  color = '#8B0000',
  backgroundColor,
  loading = false,
  className = '',
  onClick,
  footer,
}) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <span style={{ color: '#52c41a' }}>↑ {trendValue}</span>;
      case 'down':
        return <span style={{ color: '#ff4d4f' }}>↓ {trendValue}</span>;
      case 'stable':
        return <span style={{ color: '#faad14' }}>→ {trendValue}</span>;
      default:
        return null;
    }
  };

  const cardStyle: React.CSSProperties = {
    backgroundColor: backgroundColor || '#fff',
    borderRadius: 8,
    borderLeft: `4px solid ${color}`,
  };

  const iconStyle: React.CSSProperties = {
    width: 48,
    height: 48,
    borderRadius: 8,
    backgroundColor: `${color}15`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: color,
    fontSize: 24,
  };

  return (
    <Card
      className={`stat-card ${className} ${onClick ? 'clickable' : ''}`}
      style={cardStyle}
      loading={loading}
      onClick={onClick}
      bodyStyle={{ padding: 20 }}
    >
      <Row align="middle" justify="space-between">
        <Col flex="auto">
          <div style={{ marginBottom: 8, color: '#666', fontSize: 14 }}>{title}</div>
          <Statistic
            value={value}
            prefix={prefix}
            suffix={suffix}
            precision={precision}
            valueStyle={{
              fontSize: 28,
              fontWeight: 'bold',
              color: color,
              ...valueStyle,
            }}
          />
          {(trend || footer) && (
            <div style={{ marginTop: 8, fontSize: 12 }}>
              {getTrendIcon()}
              {footer && <span style={{ marginLeft: trend ? 8 : 0 }}>{footer}</span>}
            </div>
          )}
        </Col>
        {icon && (
          <Col style={{ marginLeft: 16 }}>
            <div style={iconStyle}>{icon}</div>
          </Col>
        )}
      </Row>
    </Card>
  );
};

export default StatCard;
