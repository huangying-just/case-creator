import React, { useState, useEffect } from 'react'
import { 
  Card, 
  Form, 
  Input, 
  Select, 
  Button, 
  Alert, 
  Typography, 
  Space,
  message
} from 'antd'
import { RobotOutlined, FileTextOutlined, QuestionCircleOutlined } from '@ant-design/icons'

const { TextArea } = Input
const { Option } = Select
const { Title, Paragraph } = Typography

const Home = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [userUuid] = useState(() => {
    // 从localStorage获取或生成新的UUID
    let uuid = localStorage.getItem('user_uuid')
    if (!uuid) {
      uuid = 'user_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now().toString(36)
      localStorage.setItem('user_uuid', uuid)
    }
    return uuid
  })

  const handleSubmit = async (values) => {
    setLoading(true)
    setResult(null)
    
    try {
      // 准备API请求数据
      const requestData = {
        user_uuid: userUuid,
        knowledgePoints: values.knowledgePoints,
        learningObjectives: values.learningObjectives,
        caseScenario: values.caseScenario,
        caseMaterials: values.caseMaterials || '',
        yes_or_no: values.generateQuestions || '是',
        questionType: values.questionType || '单选题2道 判断题2道',
        difficultyLevel: values.difficultyLevel || '中级'
      }

      console.log('发送请求数据:', requestData)

      // 调用后端API
      const response = await fetch('/api/workflow/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      })

      const data = await response.json()
      console.log('API响应:', data)

      if (response.ok && data.success) {
        setResult({
          case_content: data.case_content,
          questions: data.questions,
          session_id: data.session_id,
          tokens_used: data.tokens_used
        })
        message.success('案例改编完成！')
        
        // 显示API使用统计
        if (data.tokens_used) {
          message.info(`本次使用了 ${data.tokens_used} 个tokens`)
        }
      } else {
        // 处理错误情况
        const errorMessage = data.error || '生成失败，请重试'
        console.error('API错误:', errorMessage)
        message.error(errorMessage)
      }
    } catch (error) {
      console.error('网络错误:', error)
      message.error('网络连接失败，请检查服务器是否启动')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <Card className="form-card">
        <Title level={2} style={{ textAlign: 'center', marginBottom: '32px' }}>
          <RobotOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
          AI案例改编专家
        </Title>
        
        <Paragraph style={{ textAlign: 'center', fontSize: '16px', marginBottom: '32px' }}>
          基于您的教学需求，智能生成个性化案例和配套题目
        </Paragraph>

        {/* 显示用户ID */}
        <Alert
          message={`当前用户ID: ${userUuid}`}
          type="info"
          style={{ marginBottom: '24px' }}
          showIcon
        />

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          autoComplete="off"
          initialValues={{
            generateQuestions: '是',
            difficultyLevel: '中级',
            questionType: '单选题2道 判断题2道'
          }}
        >
          <Form.Item
            label="案例关联知识内容"
            name="knowledgePoints"
            rules={[{ required: true, message: '请输入知识点内容' }]}
          >
            <TextArea
              rows={4}
              placeholder="请详细描述要改编案例涉及的知识点，例如：数字化转型、供应链管理、人工智能应用等"
            />
          </Form.Item>

          <Form.Item
            label="学习目标"
            name="learningObjectives"
            rules={[{ required: true, message: '请输入学习目标' }]}
          >
            <Input
              placeholder="请输入学习目标，例如：掌握数字化转型的基本策略和实施路径"
            />
          </Form.Item>

          <Form.Item
            label="案例场景"
            name="caseScenario"
            rules={[{ required: true, message: '请输入案例场景' }]}
          >
            <Input
              placeholder="请输入案例应用场景，例如：制造业、金融业、教育行业等"
            />
          </Form.Item>

          <Form.Item
            label="案例参考材料（可选）"
            name="caseMaterials"
          >
            <TextArea
              rows={6}
              placeholder="如果有现成的案例材料，请粘贴在这里。如果没有，系统将自动生成相关案例。"
            />
          </Form.Item>

          <Space size="large" style={{ width: '100%' }}>
            <Form.Item
              label="是否生成题目"
              name="generateQuestions"
              style={{ flex: 1 }}
            >
              <Select>
                <Option value="是">是，生成配套题目</Option>
                <Option value="否">否，只需要案例</Option>
              </Select>
            </Form.Item>

            <Form.Item
              label="题目难度等级"
              name="difficultyLevel"
              style={{ flex: 1 }}
            >
              <Select>
                <Option value="初级">初级</Option>
                <Option value="中级">中级</Option>
                <Option value="高级">高级</Option>
              </Select>
            </Form.Item>
          </Space>

          <Form.Item
            label="题目类型及数量"
            name="questionType"
          >
            <Input
              placeholder="例如：单选题3道、多选题2道、判断题4道、思考题1道"
            />
          </Form.Item>

          <Form.Item style={{ textAlign: 'center', marginTop: '32px' }}>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              loading={loading}
              style={{ minWidth: '200px', height: '48px', fontSize: '16px' }}
            >
              {loading ? '正在生成中...' : '开始改编案例'}
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {result && (
        <div style={{ marginTop: '24px' }}>
          <Card 
            title={
              <Space>
                <FileTextOutlined />
                改编后的案例
                {result.session_id && (
                  <span style={{ fontSize: '12px', color: '#666' }}>
                    (会话ID: {result.session_id})
                  </span>
                )}
              </Space>
            }
            className="case-card"
          >
            <div 
              style={{ 
                whiteSpace: 'pre-wrap',
                lineHeight: '1.6',
                fontSize: '14px'
              }}
            >
              {result.case_content}
            </div>
          </Card>

          {result.questions && (
            <Card 
              title={
                <Space>
                  <QuestionCircleOutlined />
                  配套题目
                </Space>
              }
              className="case-card"
            >
              <div 
                style={{ 
                  whiteSpace: 'pre-wrap',
                  lineHeight: '1.6',
                  fontSize: '14px'
                }}
              >
                {result.questions}
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

export default Home 