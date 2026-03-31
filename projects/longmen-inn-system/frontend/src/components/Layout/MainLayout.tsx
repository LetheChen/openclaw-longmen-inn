import React, { useState, useRef, useEffect } from 'react'
import { Layout, Menu, Badge, Avatar, Dropdown } from 'antd'
import {
  DashboardOutlined,
  ProjectOutlined,
  CheckSquareOutlined,
  RobotOutlined,
  TrophyOutlined,
  CloudOutlined,
  SettingOutlined,
  BellOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  FireOutlined,
  HomeOutlined,
  BookOutlined,
  IdcardOutlined,
  FlagOutlined,
  ShopOutlined,
  ToolOutlined,
  AuditOutlined,
} from '@ant-design/icons'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import './MainLayout.css'

const { Sider, Content } = Layout

interface MainLayoutProps {
  children: React.ReactNode
}

const BrandLogo: React.FC<{ collapsed: boolean; onToggle: () => void }> = ({ collapsed, onToggle }) => {
  return (
    <div className={`brand-logo ${collapsed ? 'collapsed' : ''}`} onClick={onToggle}>
      <div className="brand-icon">
        <FireOutlined />
      </div>
      {!collapsed && (
        <div className="brand-text">
          <span className="brand-name">龙门客栈</span>
          <span className="brand-tagline">江湖令 · Multi-Agent</span>
        </div>
      )}
      <button className="collapse-toggle">
        {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
      </button>
    </div>
  )
}

const NotificationFloat: React.FC = () => {
  const [position, setPosition] = useState({ x: window.innerWidth - 80, y: window.innerHeight - 120 })
  const [isDragging, setIsDragging] = useState(false)
  const [hasMoved, setHasMoved] = useState(false)
  const dragRef = useRef<{ startX: number; startY: number; startPosX: number; startPosY: number } | null>(null)

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault()
    setIsDragging(true)
    setHasMoved(false)
    dragRef.current = {
      startX: e.clientX,
      startY: e.clientY,
      startPosX: position.x,
      startPosY: position.y,
    }
  }

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || !dragRef.current) return
      
      const deltaX = e.clientX - dragRef.current.startX
      const deltaY = e.clientY - dragRef.current.startY
      
      if (Math.abs(deltaX) > 5 || Math.abs(deltaY) > 5) {
        setHasMoved(true)
      }
      
      const newX = Math.max(20, Math.min(window.innerWidth - 60, dragRef.current.startPosX + deltaX))
      const newY = Math.max(80, Math.min(window.innerHeight - 80, dragRef.current.startPosY + deltaY))
      
      setPosition({ x: newX, y: newY })
    }

    const handleMouseUp = () => {
      setIsDragging(false)
      dragRef.current = null
    }

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging])

  const handleClick = () => {
    if (!hasMoved) {
      console.log('打开消息中心')
    }
  }

  return (
    <div
      className={`notification-float ${isDragging ? 'dragging' : ''}`}
      style={{ left: position.x, top: position.y }}
      onMouseDown={handleMouseDown}
      onClick={handleClick}
    >
      <Badge count={5} size="small" offset={[-2, 2]}>
        <div className="float-icon">
          <BellOutlined />
        </div>
      </Badge>
    </div>
  )
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()

  // 用户下拉菜单点击处理
  const handleUserMenuClick = ({ key }: { key: string }) => {
    switch (key) {
      case 'profile':
        navigate('/profile')
        break
      case 'settings':
        navigate('/settings')
        break
      case 'logout':
        // 登出逻辑由 authStore 处理
        window.location.href = '/login'
        break
    }
  }

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: <Link to="/dashboard">总舵看板</Link>,
    },
    {
      key: '/projects',
      icon: <ProjectOutlined />,
      label: <Link to="/projects">项目堂</Link>,
    },
    {
      key: '/tasks',
      icon: <BookOutlined />,
      label: <Link to="/tasks">任务榜</Link>,
    },
    {
      key: '/agents',
      icon: <IdcardOutlined />,
      label: <Link to="/agents">伙计堂</Link>,
    },
    {
      key: '/ranking',
      icon: <FlagOutlined />,
      label: <Link to="/ranking">英雄榜</Link>,
    },
    {
      key: '/intelligence',
      icon: <AuditOutlined />,
      label: <Link to="/intelligence/ai-news">客栈情报</Link>,
      children: [
        {
          key: '/intelligence/ai-news',
          icon: <RobotOutlined />,
          label: <Link to="/intelligence/ai-news">AI资讯</Link>,
        },
        {
          key: '/intelligence/news',
          icon: <BookOutlined />,
          label: <Link to="/intelligence/news">时事要闻</Link>,
        },
        {
          key: '/intelligence/red-news',
          icon: <FlagOutlined />,
          label: <Link to="/intelligence/red-news">红色印记</Link>,
        },
      ],
    },
    {
      key: '/openclaw',
      icon: <CloudOutlined />,
      label: <Link to="/openclaw">OpenClaw</Link>,
    },
    {
      key: '/settings',
      icon: <ToolOutlined />,
      label: <Link to="/settings">设置</Link>,
    },
  ]

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人中心',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '账号设置',
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ]

  // 渲染用户下拉菜单
  const userMenu = (
    <Menu
      items={userMenuItems}
      onClick={handleUserMenuClick}
    />
  )

  return (
    <Layout className="main-layout">
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        className="sider"
        width={240}
        collapsedWidth={72}
      >
        <BrandLogo collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
        
        <div className="nav-section">
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            className="nav-menu"
          />
        </div>

        <div className="sider-footer">
          <Dropdown overlay={userMenu} placement="topLeft" trigger={['click']}>
            <div className="user-card">
              <Avatar 
                size={36} 
                icon={<UserOutlined />} 
                className="user-avatar"
              />
              {!collapsed && (
                <div className="user-info">
                  <span className="user-name">掌柜</span>
                  <span className="user-role">大当家</span>
                </div>
              )}
            </div>
          </Dropdown>
        </div>
      </Sider>

      <Layout className={`main-content-layout ${collapsed ? 'collapsed' : ''}`}>
        <Content className="content">{children}</Content>
      </Layout>

      <NotificationFloat />
    </Layout>
  )
}

export default MainLayout
