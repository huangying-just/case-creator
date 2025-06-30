import React, { useState, useEffect } from 'react'
import { 
  Card, 
  List, 
  Typography, 
  Empty, 
  Input, 
  Button, 
  Space, 
  Tag, 
  message, 
  Modal, 
  Pagination,
  Spin
} from 'antd'
import { 
  HistoryOutlined, 
  FileTextOutlined, 
  SearchOutlined, 
  EyeOutlined, 
  QuestionCircleOutlined,
  CalendarOutlined,
  TagsOutlined
} from '@ant-design/icons'

const { Title, Paragraph, Text } = Typography
const { Search } = Input

const History = () => {
  const [loading, setLoading] = useState(true)
  const [cases, setCases] = useState([])
  const [total, setTotal] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(10)
  const [searchKeyword, setSearchKeyword] = useState('')
  const [selectedCase, setSelectedCase] = useState(null)
  const [detailModalVisible, setDetailModalVisible] = useState(false)

  // 获取用户UUID
  const userUuid = localStorage.getItem('user_uuid')

  // 加载历史记录
  const loadHistory = async (page = 1, keyword = '') => {
    if (!userUuid) {
      message.error('用户信息无效，请刷新页面重试')
      return
    }

    setLoading(true)
    try {
      const url = new URL(`/api/cases/user/${userUuid}`, window.location.origin)
      url.searchParams.append('page', page)
      url.searchParams.append('per_page', pageSize)
      if (keyword) {
        url.searchParams.append('q', keyword)
      }

      const response = await fetch(url)
      const data = await response.json()

      if (response.ok) {
        setCases(data.cases || [])
        setTotal(data.total || 0)
        setCurrentPage(page)
      } else {
        console.error('获取历史记录失败:', data.error)
        message.error(data.error || '获取历史记录失败')
      }
    } catch (error) {
      console.error('网络错误:', error)
      message.error('网络连接失败，请检查服务器状态')
    } finally {
      setLoading(false)
    }
  }

  // 获取案例详情
  const loadCaseDetail = async (caseId) => {
    try {
      const response = await fetch(`/api/cases/${caseId}`)
      const data = await response.json()

      if (response.ok) {
        setSelectedCase(data.case)
        setDetailModalVisible(true)
      } else {
        message.error(data.error || '获取案例详情失败')
      }
    } catch (error) {
      console.error('获取案例详情失败:', error)
      message.error('网络连接失败')
    }
  }

  // 搜索处理
  const handleSearch = (value) => {
    setSearchKeyword(value)
    setCurrentPage(1)
    loadHistory(1, value)
  }

  // 分页处理
  const handlePageChange = (page) => {
    loadHistory(page, searchKeyword)
  }

  // 格式化时间
  const formatTime = (timeString) => {
    const date = new Date(timeString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // 获取难度等级颜色
  const getDifficultyColor = (level) => {
    switch (level) {
      case '初级': return 'green'
      case '中级': return 'orange'
      case '高级': return 'red'
      default: return 'default'
    }
  }

  useEffect(() => {
    loadHistory()
  }, [])

  return (
    <div>
      <Card className="form-card">
        <Title level={2} style={{ textAlign: 'center', marginBottom: '32px' }}>
          <HistoryOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
          历史记录
        </Title>

        {/* 搜索区域 */}
        <Space direction="vertical" size="middle" style={{ width: '100%', marginBottom: '24px' }}>
          <Search
            placeholder="搜索案例标题、知识点或场景..."
            allowClear
            enterButton={<SearchOutlined />}
            size="large"
            onSearch={handleSearch}
            style={{ maxWidth: '600px' }}
          />
          
          {userUuid && (
            <Text type="secondary">
              当前用户：{userUuid} | 共找到 {total} 个案例
            </Text>
          )}
        </Space>

        {/* 案例列表 */}
        <Spin spinning={loading}>
          {cases.length > 0 ? (
            <>
              <List
                itemLayout="vertical"
                dataSource={cases}
                renderItem={(item) => (
                  <List.Item
                    key={item.id}
                    actions={[
                      <Button 
                        type="link" 
                        icon={<EyeOutlined />}
                        onClick={() => loadCaseDetail(item.id)}
                      >
                        查看详情
                      </Button>,
                      <Text type="secondary">
                        <EyeOutlined /> {item.view_count || 0}
                      </Text>
                    ]}
                  >
                    <List.Item.Meta
                      title={
                        <Space>
                          <FileTextOutlined style={{ color: '#1890ff' }} />
                          <Text strong>{item.title || '未命名案例'}</Text>
                          {item.difficulty_level && (
                            <Tag color={getDifficultyColor(item.difficulty_level)}>
                              {item.difficulty_level}
                            </Tag>
                          )}
                        </Space>
                      }
                      description={
                        <Space direction="vertical" size="small">
                          {item.knowledge_points && (
                            <Text type="secondary">
                              <TagsOutlined /> 知识点：{item.knowledge_points}
                            </Text>
                          )}
                          {item.case_scenario && (
                            <Text type="secondary">
                              案例场景：{item.case_scenario}
                            </Text>
                          )}
                          <Text type="secondary">
                            <CalendarOutlined /> 创建时间：{formatTime(item.created_at)}
                          </Text>
                        </Space>
                      }
                    />
                    
                    {item.learning_objectives && (
                      <Paragraph 
                        ellipsis={{ rows: 2, expandable: false }}
                        style={{ marginTop: '8px' }}
                      >
                        学习目标：{item.learning_objectives}
                      </Paragraph>
                    )}
                  </List.Item>
                )}
              />

              {/* 分页 */}
              {total > pageSize && (
                <div style={{ textAlign: 'center', marginTop: '24px' }}>
                  <Pagination
                    current={currentPage}
                    total={total}
                    pageSize={pageSize}
                    showSizeChanger={false}
                    showQuickJumper
                    showTotal={(total, range) => 
                      `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`
                    }
                    onChange={handlePageChange}
                  />
                </div>
              )}
            </>
          ) : (
            <Empty
              description={
                searchKeyword ? 
                  `未找到包含"${searchKeyword}"的案例` : 
                  "暂无历史记录，去创建您的第一个案例吧！"
              }
              style={{ margin: '64px 0' }}
            >
              {!searchKeyword && (
                <Button type="primary" onClick={() => window.location.href = '/'}>
                  创建案例
                </Button>
              )}
            </Empty>
          )}
        </Spin>
      </Card>

      {/* 案例详情弹窗 */}
      <Modal
        title={
          <Space>
            <FileTextOutlined />
            案例详情
            {selectedCase?.difficulty_level && (
              <Tag color={getDifficultyColor(selectedCase.difficulty_level)}>
                {selectedCase.difficulty_level}
              </Tag>
            )}
          </Space>
        }
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={800}
        style={{ top: 20 }}
      >
        {selectedCase && (
          <div>
            <Title level={4}>{selectedCase.title}</Title>
            
            {/* 基本信息 */}
            <Space direction="vertical" size="middle" style={{ width: '100%', marginBottom: '24px' }}>
              {selectedCase.knowledge_points && (
                <div>
                  <Text strong>知识点：</Text>
                  <Text>{selectedCase.knowledge_points}</Text>
                </div>
              )}
              {selectedCase.learning_objectives && (
                <div>
                  <Text strong>学习目标：</Text>
                  <Text>{selectedCase.learning_objectives}</Text>
                </div>
              )}
              {selectedCase.case_scenario && (
                <div>
                  <Text strong>案例场景：</Text>
                  <Text>{selectedCase.case_scenario}</Text>
                </div>
              )}
              <div>
                <Text strong>创建时间：</Text>
                <Text>{formatTime(selectedCase.created_at)}</Text>
              </div>
            </Space>

            {/* 案例内容 */}
            <Card 
              title={<><FileTextOutlined /> 案例内容</>}
              style={{ marginBottom: '16px' }}
            >
              <div 
                style={{ 
                  whiteSpace: 'pre-wrap',
                  lineHeight: '1.6',
                  fontSize: '14px',
                  maxHeight: '400px',
                  overflowY: 'auto'
                }}
              >
                {selectedCase.content}
              </div>
            </Card>

            {/* 配套题目 */}
            {selectedCase.questions && selectedCase.questions.length > 0 && (
              <Card title={<><QuestionCircleOutlined /> 配套题目</>}>
                <div 
                  style={{ 
                    whiteSpace: 'pre-wrap',
                    lineHeight: '1.6',
                    fontSize: '14px',
                    maxHeight: '400px',
                    overflowY: 'auto'
                  }}
                >
                  {typeof selectedCase.questions === 'string' 
                    ? selectedCase.questions 
                    : JSON.stringify(selectedCase.questions, null, 2)
                  }
                </div>
              </Card>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}

export default History 