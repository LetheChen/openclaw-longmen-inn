import { Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import MainLayout from './components/Layout/MainLayout'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import Tasks from './pages/Tasks'
import Agents from './pages/Agents'
import Ranking from './pages/Ranking'
import OpenClaw from './pages/OpenClaw'
import Settings from './pages/Settings'
import './App.css'

const { Content } = Layout

function App() {
  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/agents" element={<Agents />} />
        <Route path="/ranking" element={<Ranking />} />
        <Route path="/openclaw" element={<OpenClaw />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </MainLayout>
  )
}

export default App
