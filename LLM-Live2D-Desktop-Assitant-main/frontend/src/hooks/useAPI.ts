import { useState, useCallback } from 'react'
import { API_CONFIG, getEndpointURL } from '../config/api'

export interface APIResponse<T = any> {
  data: T | null
  error: string | null
  loading: boolean
}

export interface UseAPIOptions {
  onSuccess?: (data: any) => void
  onError?: (error: string) => void
}

export const useAPI = <T = any>(options: UseAPIOptions = {}) => {
  const [state, setState] = useState<APIResponse<T>>({
    data: null,
    error: null,
    loading: false
  })

  const request = useCallback(async (
    endpoint: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
    body?: any,
    headers?: Record<string, string>
  ): Promise<T | null> => {
    setState(prev => ({ ...prev, loading: true, error: null }))

    try {
      const url = endpoint.startsWith('http') ? endpoint : getEndpointURL(endpoint)
      
      const requestOptions: RequestInit = {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...headers
        }
      }

      if (body && method !== 'GET') {
        requestOptions.body = JSON.stringify(body)
      }

      console.log(`[useAPI] ${method} ${url}`)
      
      const response = await fetch(url, requestOptions)
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      
      setState({
        data,
        error: null,
        loading: false
      })

      options.onSuccess?.(data)
      return data

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      console.error('[useAPI] Request failed:', errorMessage)
      
      setState({
        data: null,
        error: errorMessage,
        loading: false
      })

      options.onError?.(errorMessage)
      return null
    }
  }, [options])

  const get = useCallback((endpoint: string, headers?: Record<string, string>) => {
    return request(endpoint, 'GET', undefined, headers)
  }, [request])

  const post = useCallback((endpoint: string, body?: any, headers?: Record<string, string>) => {
    return request(endpoint, 'POST', body, headers)
  }, [request])

  const put = useCallback((endpoint: string, body?: any, headers?: Record<string, string>) => {
    return request(endpoint, 'PUT', body, headers)
  }, [request])

  const del = useCallback((endpoint: string, headers?: Record<string, string>) => {
    return request(endpoint, 'DELETE', undefined, headers)
  }, [request])

  const reset = useCallback(() => {
    setState({
      data: null,
      error: null,
      loading: false
    })
  }, [])

  return {
    ...state,
    request,
    get,
    post,
    put,
    delete: del,
    reset
  }
}

// Convenience hooks for specific endpoints
export const useHealthCheck = () => {
  return useAPI({
    onSuccess: (data) => console.log('[useHealthCheck] Health check passed:', data),
    onError: (error) => console.error('[useHealthCheck] Health check failed:', error)
  })
}

export const useMockTTS = () => {
  return useAPI({
    onSuccess: (data) => console.log('[useMockTTS] TTS request successful:', data),
    onError: (error) => console.error('[useMockTTS] TTS request failed:', error)
  })
}

export const useMockSTT = () => {
  return useAPI({
    onSuccess: (data) => console.log('[useMockSTT] STT request successful:', data),
    onError: (error) => console.error('[useMockSTT] STT request failed:', error)
  })
}