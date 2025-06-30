import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import Home from './pages/Home'
import Admin from './pages/Admin'
import History from './pages/History'
import Settings from './pages/Settings'
import Navigation from './components/Navigation'

const { Header, Content } = Layout

function App() {
  return (
    <Layout className="main-layout">
      <Header style={{ padding: 0, background: 'rgba(255, 255, 255, 0.1)' }}>
        <Navigation />
      </Header>
      <Content>
        <div className="content-container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/history" element={<History />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/admin/*" element={<Admin />} />
          </Routes>
        </div>
      </Content>
    </Layout>
  )
}

export default App 