import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const response = await api.get('/api/me')
          setUser(response.data)
        } catch (error) {
          localStorage.removeItem('token')
          setToken(null)
        }
      }
      setLoading(false)
    }
    initAuth()
  }, [token])

  const login = async (email, password) => {
    const response = await api.post('/api/auth/login/json', { email, password })
    const { access_token } = response.data
    localStorage.setItem('token', access_token)
    setToken(access_token)
    
    const userResponse = await api.get('/api/me', {
      headers: { Authorization: `Bearer ${access_token}` }
    })
    setUser(userResponse.data)
    return userResponse.data
  }

  const register = async (email, password, fullName) => {
    await api.post('/api/auth/register', {
      email,
      password,
      full_name: fullName
    })
    return login(email, password)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!token && !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
