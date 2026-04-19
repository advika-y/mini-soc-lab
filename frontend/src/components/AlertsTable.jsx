import { formatUnixTime } from '../utils'
import styles from './AlertsTable.module.css'

const ACTION_MAP = {
  BLOCKED: { label: 'BLOCKED', cls: 'red' },
  ALERT: { label: 'ALERT', cls: 'amber' },
  'Repeat Offender Detected': { label: 'REPEAT', cls: 'amber' },
  'Stealthy Attack Detected': { label: 'STEALTH', cls: 'amber' },
  'Distributed Attack Detected': { label: 'DISTRIB', cls: 'red' },
  'Multi-Stage Attack Detected': { label: 'MULTI', cls: 'red' },
  THREAT_INTEL: { label: 'INTEL', cls: 'red' },
}

function Badge({ action }) {
  const map = ACTION_MAP[action] ?? { label: action.slice(0, 8), cls: 'dim' }
  return <span className={`${styles.badge} ${styles[map.cls]}`}>{map.label}</span>
}

export default function AlertsTable({ alerts, loading }) {
  return (
    <div className={styles.wrap}>
      <div className={styles.heading}>
        <span className={styles.title}>alerts</span>
        <span className={styles.count}>{alerts?.length || 0} events</span>
      </div>

      {alerts.length === 0 ? (
        loading ? (
          <div className={styles.empty}>fetching...</div>
        ) : (
          <div className={styles.empty}>no alerts detected</div>
        )
      ) : (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>time</th>
                <th>ip</th>
                <th>type</th>
                <th>score</th>
                <th>country</th>
                <th>action</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((a, i) => (
                <tr key={i} className={styles.row} style={{ animationDelay: `${i * 0.02}s` }}>
                  <td className={styles.mono}>{formatUnixTime(a.timestamp)}</td>
                  <td className={styles.ip}>{a.ip}</td>
                  <td className={styles.type}>{a.type}</td>
                  <td className={styles.score}>{a.score}</td>
                  <td className={styles.country}>{a.country || '—'}</td>
                  <td><Badge action={a.action} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}