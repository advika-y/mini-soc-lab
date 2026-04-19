import styles from './StatCards.module.css'

export default function StatCards({ alerts, blockedIPs }) {
  const ddos = alerts.filter((a) => a.type === 'DDOS').length
  const scans = alerts.filter((a) => a.type === 'PORT_SCAN').length

  return (
    <div className={styles.grid}>
      <div className={styles.card}>
        <span className={styles.label}>total alerts</span>
        <span className={styles.value}>{alerts.length}</span>
      </div>
      <div className={`${styles.card} ${styles.red}`}>
        <span className={styles.label}>ips blocked</span>
        <span className={styles.value}>{blockedIPs.length}</span>
      </div>
      <div className={`${styles.card} ${styles.amber}`}>
        <span className={styles.label}>ddos events</span>
        <span className={styles.value}>{ddos}</span>
      </div>
      <div className={`${styles.card} ${styles.blue}`}>
        <span className={styles.label}>port scans</span>
        <span className={styles.value}>{scans}</span>
      </div>
    </div>
  )
}
