import { useEffect, useRef } from 'react'

export function useAutoRefresh(callback, intervalMs = 10000, enabled = true) {
  const savedCallback = useRef(callback)

  useEffect(() => {
    savedCallback.current = callback
  }, [callback])

  useEffect(() => {
    if (!enabled) return
    const id = setInterval(() => savedCallback.current(), intervalMs)
    return () => clearInterval(id)
  }, [intervalMs, enabled])
}
