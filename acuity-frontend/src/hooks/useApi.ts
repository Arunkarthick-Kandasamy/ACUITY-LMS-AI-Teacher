import { useState, useEffect, useCallback } from 'react'
import { apiRequest, ApiError, getAccessToken } from '@/services/api'
import type { ApiResponse } from '@/services/types'

interface UseApiResult<T> {
  data: T | null
  loading: boolean
  error: string | null
  refetch: () => void
}

export function useApi<T>(
  fetcher: () => Promise<ApiResponse<T>>,
  deps: unknown[] = [],
): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const json = await fetcher()
      setData(json.data)
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('An unexpected error occurred')
      }
    } finally {
      setLoading(false)
    }
  }, deps)

  useEffect(() => {
    fetch()
  }, [fetch])

  return { data, loading, error, refetch: fetch }
}

export function useAuthApi<T>(
  fetcher: () => Promise<ApiResponse<T>>,
  deps: unknown[] = [],
): UseApiResult<T> {
  const token = getAccessToken()
  return useApi(fetcher, [token, ...deps])
}

export function useAuthMutation<TData, TArgs extends unknown[]>(
  mutator: (...args: TArgs) => Promise<ApiResponse<TData>>,
) {
  const [isPending, setIsPending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const mutateAsync = useCallback(async (...args: TArgs): Promise<TData> => {
    setIsPending(true)
    setError(null)
    try {
      const res = await mutator(...args)
      return res.data
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'An unexpected error occurred'
      setError(msg)
      throw err
    } finally {
      setIsPending(false)
    }
  }, [mutator])

  return { mutateAsync, isPending, error }
}

export type { UseApiResult }
