import { Routes, Route, Outlet } from 'react-router-dom'
import MainLayout from './components/Layout/MainLayout'
import ProtectedRoute, { PublicRoute } from './components/auth/ProtectedRoute'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import Tasks from './pages/Tasks'
import Agents from './pages/Agents'
import AgentWorkspace from './pages/AgentWorkspace'
import Ranking from './pages/Ranking'
import OpenClaw from './pages/OpenClaw'
import Settings from './pages/Settings'
import Login from './pages/Login'
import './App.css'

function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      
      <Route
        element={
          <ProtectedRoute>
            <MainLayout>
              <Outlet />
            </MainLayout>
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/agents" element={<Agents />} />
        <Route path="/agents/:agentId" element={<AgentWorkspace />} />
        <Route path="/ranking" element={<Ranking />} />
        <Route path="/openclaw" element={<OpenClaw />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      
      <Route path="*" element={<Dashboard />} />
    </Routes>
  )
}

export default App
