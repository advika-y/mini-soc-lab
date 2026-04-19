import api from '../api'
import { useAutoRefresh } from '../hooks/useAutoRefresh'
import Navbar from '../components/Navbar'
import HealthBar from '../components/HealthBar'
import StatCards from '../components/StatCards'
import AlertsTable from '../components/AlertsTable'
import BlockedIPs from '../components/BlockedIPs'
import styles from './DashboardPage.module.css'
import { useState, useEffect } from 'react'

export default function DashboardPage() {
  const [alerts, setAlerts] = useState([])
  const [blockedIPs, setBlockedIPs] = useState([])
  const [health, setHealth] = useState(null)
  const [loadingAlerts, setLoadingAlerts] = useState(true)
  const [loadingBlocked, setLoadingBlocked] = useState(true)
  const [loadingHealth, setLoadingHealth] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [lastUpdated, setLastUpdated] = useState('')
  const [error, setError] = useState('')

  const fetchAll = async () => {
    setError('')
    try {
      const [alertsRes, blockedRes, healthRes] = await Promise.all([
        api.get('/alerts'),
        api.get('/blocked'),
        api.get('/health'),
      ])
      setAlerts(alertsRes.data)
      setBlockedIPs(blockedRes.data)
      setHealth(healthRes.data)
      setLastUpdated(new Date().toLocaleTimeString([], { hour12: false }))
    } catch (err) {
      if (err.response?.status !== 401) {
        setError('Failed to fetch data from SOC backend. Is api.py running?')
      }
    } finally {
      setLoadingAlerts(false)
      setLoadingBlocked(false)
      setLoadingHealth(false)
    }
  }

  useEffect(() => {
    fetchAll()
  }, [])

  useAutoRefresh(() => {
    fetchAll()
  }, 3000, autoRefresh)

  const handleUnblock = (ip) => {
    setBlockedIPs((prev) => prev.filter((b) => b !== ip))
    setTimeout(() => fetchAll(), 1000)
  }

  

  return (
    <div className={styles.layout}>
      <Navbar
        autoRefresh={autoRefresh}
        onToggleRefresh={() => setAutoRefresh((v) => !v)}
        lastUpdated={lastUpdated}
      />

      <HealthBar health={health} loading={loadingHealth} />

      <main className={styles.main}>
        {error && (
          <div className={styles.errorBanner}>
            <span className={styles.errorIcon}>!</span>
            {error}
          </div>
        )}

        <StatCards alerts={alerts} blockedIPs={blockedIPs} />

        <div className={styles.grid}>
          <div className={styles.alertsCol}>
            <AlertsTable alerts={alerts} loading={loadingAlerts} />
          </div>

          <div className={styles.blockedCol}>
            <BlockedIPs
              ips={blockedIPs}
              loading={loadingBlocked}
              onUnblock={handleUnblock}
            />
          </div>
        </div>
      </main>
    </div>
  )
}
