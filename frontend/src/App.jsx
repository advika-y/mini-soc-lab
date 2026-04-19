import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './AuthContext'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'

function ProtectedRoute({ children }) {
  const { isAuthed } = useAuth()
  return isAuthed ? children : <Navigate to="/login" replace />
}

function PublicRoute({ children }) {
  const { isAuthed } = useAuth()
  return isAuthed ? <Navigate to="/" replace /> : children
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
