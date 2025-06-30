import React from 'react'
import { Menu, Button, Typography } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import { 
  HomeOutlined, 
  HistoryOutlined, 
  RobotOutlined 
} from '@ant-design/icons'

const { Title } = Typography

const Navigation = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '案例改编',
    },
    {
      key: '/history',
      icon: <HistoryOutlined />,
      label: '历史记录',
    },
  ]

  const handleMenuClick = ({ key }) => {
    navigate(key)
  }

  return (
    <div style={{ 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'space-between',
      padding: '0 24px',
      height: '64px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <RobotOutlined style={{ fontSize: '24px', color: 'white', marginRight: '12px' }} />
        <Title level={3} style={{ color: 'white', margin: 0 }}>
          案例改编专家
        </Title>
      </div>
      
      <Menu
        mode="horizontal"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{ 
          backgroundColor: 'transparent',
          borderBottom: 'none',
          flex: 1,
          justifyContent: 'center'
        }}
        theme="dark"
      />
      
      <div>
        <Button type="text" style={{ color: 'white' }}>
          欢迎使用
        </Button>
      </div>
    </div>
  )
}

export default Navigation 