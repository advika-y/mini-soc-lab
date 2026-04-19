import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import api from '../api'
import styles from './LoginPage.module.css'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [lines, setLines] = useState([
    '> mini-soc-lab v1.0',
    '> initializing secure channel...',
    '> awaiting credentials',
  ])

  const { login } = useAuth()
  const navigate = useNavigate()

  const pushLine = (line) => setLines((l) => [...l, line])

  const handleSubmit = async (e) => {
  e.preventDefault()
  setError('')
  setLoading(true)
  pushLine(`> authenticating user: ${username}`)

  try {
    const res = await api.post('/login', {
      username,
      password,
    })
    const token = res.data.access_token
    login(token)

    pushLine('> auth token issued')
    pushLine('> access granted — redirecting...')

    setTimeout(() => navigate('/'), 600)

  } 
  catch (err) 
  {
    const msg = err.response?.data?.error || 'Authentication failed'
    pushLine(`> ERROR: ${msg}`)
    setError(msg)
  } finally {
    setLoading(false)
  }
}

  return (
    <div className={styles.root}>
      <div className={styles.grid} aria-hidden="true" />

      <div className={styles.panel}>
        <div className={styles.header}>
          <div className={styles.dot} style={{ background: '#f85149' }} />
          <div className={styles.dot} style={{ background: '#d29922' }} />
          <div className={styles.dot} style={{ background: '#3fb950' }} />
          <span className={styles.title}>soc-auth.sh</span>
        </div>

        <div className={styles.terminal}>
          {lines.map((l, i) => (
            <div key={i} className={styles.line} style={{ animationDelay: `${i * 0.08}s` }}>
              <span className={styles.prompt}>{l.startsWith('> ERROR') ? '!' : '>'}</span>
              <span className={l.startsWith('> ERROR') ? styles.err : styles.lineText}>
                {l.replace(/^> /, '')}
              </span>
            </div>
          ))}
          <div className={styles.cursor} />
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label className={styles.label}>username</label>
            <input
              className={styles.input}
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              autoFocus
              required
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>password</label>
            <input
              className={styles.input}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
            />
          </div>

          {error && <p className={styles.errorMsg}>{error}</p>}

          <button type="submit" className={styles.btn} disabled={loading}>
            {loading ? 'authenticating...' : '[ authenticate ]'}
          </button>
        </form>
      </div>
    </div>
  )
}
