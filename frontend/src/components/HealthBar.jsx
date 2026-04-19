import { formatUnixTime } from '../utils'
import styles from './HealthBar.module.css'

export default function HealthBar({ health, loading }) {
  const status = health?.status ?? 'unknown'
  const isHealthy = status === 'healthy'

  return (
    <div className={styles.bar}>
      <div className={styles.left}>
        <div className={`${styles.indicator} ${isHealthy ? styles.online : styles.offline}`} />
        <span className={styles.label}>
          {loading ? 'connecting...' : `system ${status}`}
        </span>
      </div>
      <div className={styles.right}>
        <span className={styles.chip}>mini-soc-lab</span>
        <span className={styles.time}>
          {health?.time
            ? formatUnixTime(health.time)
            : '--:--:--'}
        </span>
      </div>
    </div>
  )
}