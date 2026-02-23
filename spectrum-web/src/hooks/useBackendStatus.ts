import { useState, useEffect, useCallback } from 'react'
import { apiClient } from '@/lib/api/client'

export type BackendStatus = 'checking' | 'awake' | 'waking' | 'error'

interface UseBackendStatusReturn {
  status: BackendStatus
  checkStatus: () => Promise<void>
  elapsedSeconds: number
}

const HEALTH_TIMEOUT = 5000 // 5 seconds for initial check
const WAKING_TIMEOUT = 60000 // 60 seconds max wait for cold start

export function useBackendStatus(): UseBackendStatusReturn {
  const [status, setStatus] = useState<BackendStatus>('checking')
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [startTime, setStartTime] = useState<number | null>(null)

  const checkStatus = useCallback(async () => {
    setStatus('checking')
    setStartTime(Date.now())
    setElapsedSeconds(0)

    try {
      // Quick check with short timeout
      await apiClient.get('/health', { timeout: HEALTH_TIMEOUT })
      setStatus('awake')
      setStartTime(null)
    } catch {
      // Backend didn't respond quickly - it's probably waking up
      setStatus('waking')

      // Keep trying with longer timeout
      try {
        await apiClient.get('/health', { timeout: WAKING_TIMEOUT })
        setStatus('awake')
        setStartTime(null)
      } catch {
        setStatus('error')
        setStartTime(null)
      }
    }
  }, [])

  // Update elapsed time while waking
  useEffect(() => {
    if (status !== 'waking' || !startTime) return

    const interval = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startTime) / 1000))
    }, 1000)

    return () => clearInterval(interval)
  }, [status, startTime])

  // Check status on mount
  useEffect(() => {
    checkStatus()
  }, [checkStatus])

  return { status, checkStatus, elapsedSeconds }
}
