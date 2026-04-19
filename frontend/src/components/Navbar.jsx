import { useAuth } from '../AuthContext'
import styles from './Navbar.module.css'

export default function Navbar({ autoRefresh, onToggleRefresh, lastUpdated }) {
  const { logout } = useAuth()

  return (
    <nav className={styles.nav}>
      <div className={styles.left}>
        <span className={styles.logo}>
          <span className={styles.bracket}>[</span>
          SOC
          <span className={styles.bracket}>]</span>
        </span>
        <span className={styles.sub}>security operations center</span>
      </div>

      <div className={styles.right}>
        {lastUpdated && (
          <span className={styles.updated}>
            updated {lastUpdated}
          </span>
        )}

        <button
          className={`${styles.btn} ${autoRefresh ? styles.active : ''}`}
          onClick={onToggleRefresh}
          title="Toggle auto-refresh"
        >
          <span className={styles.refreshDot} style={{ background: autoRefresh ? 'var(--green)' : 'var(--text-dim)' }} />
          {autoRefresh ? 'live' : 'paused'}
        </button>

        <button className={styles.btn} onClick={logout}>
          logout
        </button>
      </div>
    </nav>
  )
}
