import { useState } from 'react'
import api from '../api'
import styles from './BlockedIPs.module.css'

export default function BlockedIPs({ ips, loading, onUnblock }) {
  const [unblocking, setUnblocking] = useState(null)
  const [error, setError] = useState('')

  const handleUnblock = async (ip) => {
    setUnblocking(ip)
    setError('')
    try {
      await api.post('/unblock', { ip })
      onUnblock(ip)
    } catch (err) {
      setError(`Failed to unblock ${ip}`)
    } finally {
      setUnblocking(null)
    }
  }

  return (
    <div className={styles.wrap}>
      <div className={styles.heading}>
        <span className={styles.title}>blocked ips</span>
        <span className={styles.count}>{ips.length} active</span>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {loading && ips.length === 0 ? (
        <div className={styles.empty}>fetching...</div>
      ) : ips.length === 0 ? (
        <div className={styles.empty}>no blocked ips</div>
      ) : (
        <ul className={styles.list}>
          {ips.map((ip, i) => (
            <li key={ip} className={styles.item} style={{ animationDelay: `${i * 0.04}s` }}>
              <div className={styles.ipRow}>
                <div className={styles.dot} />
                <span className={styles.ip}>{ip}</span>
              </div>
              <button
                className={styles.unblockBtn}
                onClick={() => handleUnblock(ip)}
                disabled={unblocking === ip}
              >
                {unblocking === ip ? 'removing...' : '[ unblock ]'}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
