import React from 'react'
import { Card, Typography, Empty } from 'antd'
import { UserOutlined } from '@ant-design/icons'

const { Title } = Typography

const Admin = () => {
  return (
    <Card className="form-card">
      <Title level={2} style={{ textAlign: 'center', marginBottom: '32px' }}>
        <UserOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
        管理面板
      </Title>
      
      <Empty
        description="管理功能开发中..."
        style={{ margin: '64px 0' }}
      />
    </Card>
  )
}

export default Admin 