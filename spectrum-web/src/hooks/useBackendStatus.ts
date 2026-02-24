import { useState, useEffect, useCallback, useRef } from 'react'
import { apiClient } from '@/lib/api/client'

export type BackendStatus = 'checking' | 'awake' | 'waking' | 'error'

interface UseBackendStatusReturn {
  status: BackendStatus
  checkStatus: () => void
  elapsedSeconds: number
}

const HEALTH_TIMEOUT = 5000 // 5 seconds per request
const POLL_INTERVAL = 3000 // Poll every 3 seconds while waking
const MAX_WAIT_TIME = 90000 // 90 seconds max wait for cold start

export function useBackendStatus(): UseBackendStatusReturn {
  const [status, setStatus] = useState<BackendStatus>('checking')
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const [startTime, setStartTime] = useState<number | null>(null)
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const isMountedRef = useRef(true)

  const stopPolling = useCallback(() => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current)
      pollIntervalRef.current = null
    }
  }, [])

  const checkHealth = useCallback(async (): Promise<boolean> => {
    try {
      await apiClient.get('/health', { timeout: HEALTH_TIMEOUT })
      return true
    } catch {
      return false
    }
  }, [])

  const checkStatus = useCallback(() => {
    // Reset state
    stopPolling()
    setStatus('checking')
    const now = Date.now()
    setStartTime(now)
    setElapsedSeconds(0)

    // Initial check
    checkHealth().then((isHealthy) => {
      if (!isMountedRef.current) return

      if (isHealthy) {
        setStatus('awake')
        setStartTime(null)
        return
      }

      // Not healthy - start polling
      setStatus('waking')

      pollIntervalRef.current = setInterval(async () => {
        if (!isMountedRef.current) {
          stopPolling()
          return
        }

        const elapsed = Date.now() - now

        // Check if we've exceeded max wait time
        if (elapsed >= MAX_WAIT_TIME) {
          stopPolling()
          setStatus('error')
          setStartTime(null)
          return
        }

        // Try health check
        const isHealthy = await checkHealth()
        if (!isMountedRef.current) return

        if (isHealthy) {
          stopPolling()
          setStatus('awake')
          setStartTime(null)
        }
      }, POLL_INTERVAL)
    })
  }, [checkHealth, stopPolling])

  // Update elapsed time while waking
  useEffect(() => {
    if (status !== 'waking' || !startTime) return

    const interval = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startTime) / 1000))
    }, 1000)

    return () => clearInterval(interval)
  }, [status, startTime])

  // Check status on mount and cleanup on unmount
  useEffect(() => {
    isMountedRef.current = true
    checkStatus()

    return () => {
      isMountedRef.current = false
      stopPolling()
    }
  }, [checkStatus, stopPolling])

  return { status, checkStatus, elapsedSeconds }
}
