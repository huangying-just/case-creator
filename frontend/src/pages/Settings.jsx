import React from 'react'
import { Card, Form, Input, Select, Button, Typography, message } from 'antd'
import { SettingOutlined } from '@ant-design/icons'

const { Title } = Typography
const { Option } = Select

const Settings = () => {
  const [form] = Form.useForm()

  const handleSave = (values) => {
    message.success('设置已保存')
    console.log('设置数据:', values)
  }

  return (
    <Card className="form-card">
      <Title level={2} style={{ textAlign: 'center', marginBottom: '32px' }}>
        <SettingOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
        用户设置
      </Title>
      
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSave}
        initialValues={{
          nickname: '用户_12345678',
          model: 'gpt-4o-mini'
        }}
      >
        <Form.Item
          label="用户ID (UUID)"
          name="uuid"
        >
          <Input placeholder="请输入您的UUID" />
        </Form.Item>

        <Form.Item
          label="用户昵称"
          name="nickname"
        >
          <Input placeholder="请输入昵称" />
        </Form.Item>

        <Form.Item
          label="OpenRouter API密钥"
          name="apiKey"
        >
          <Input.Password placeholder="请输入您的OpenRouter API密钥" />
        </Form.Item>

        <Form.Item
          label="默认AI模型"
          name="model"
        >
          <Select>
            <Option value="gpt-4o">GPT-4o</Option>
            <Option value="gpt-4o-mini">GPT-4o Mini</Option>
            <Option value="claude-3-opus">Claude 3 Opus</Option>
            <Option value="claude-3-sonnet">Claude 3 Sonnet</Option>
            <Option value="claude-3-haiku">Claude 3 Haiku</Option>
          </Select>
        </Form.Item>

        <Form.Item style={{ textAlign: 'center', marginTop: '32px' }}>
          <Button type="primary" htmlType="submit" size="large">
            保存设置
          </Button>
        </Form.Item>
      </Form>
    </Card>
  )
}

export default Settings 