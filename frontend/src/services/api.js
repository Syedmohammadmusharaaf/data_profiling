/**
 * API Service for PII Scanner Enterprise with Enhanced Logging
 * ===========================================================
 * 
 * Centralized API client for all backend communication.
 * Handles authentication, error handling, and request/response formatting.
 * Enhanced with comprehensive logging for debugging and monitoring.
 * 
 * @author PII Scanner Team
 * @version 2.1.0
 */

import axios from 'axios'
import toast from 'react-hot-toast'
import { apiLogger, logger, workflowLogger } from '../utils/logger'

// =============================================================================
// CONFIGURATION AND SETUP
// =============================================================================

/**
 * Dynamically detect backend URL based on environment
 */
const getBackendURL = () => {
  // Priority 1: For preview environment (when accessed via preview URL)
  if (window.location.hostname.includes('emergentagent.com')) {
    const previewUrl = window.location.origin.replace(':3000', ':8001').replace(':3001', ':8001').replace(':3002', ':8001').replace(':3003', ':8001')
    logger.info('Using preview backend URL', { url: previewUrl })
    return previewUrl
  }
  
  // Priority 2: Check environment variables for local development
  const envUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL
  if (envUrl) {
    logger.info('Using backend URL from environment', { url: envUrl })
    return envUrl
  }
  
  // Priority 3: Default local development
  logger.info('Using default backend URL', { url: 'http://localhost:8001' })
  return 'http://localhost:8001'
}

const API_BASE_URL = getBackendURL()
logger.info('🔗 API Base URL configured', { baseUrl: API_BASE_URL })

// Create axios instance with enhanced logging capabilities
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // 3 minutes for classification operations (increased from 60s)
  headers: {
    'Content-Type': 'application/json',
  },
})

// =============================================================================
// REQUEST/RESPONSE INTERCEPTORS WITH ENHANCED LOGGING
// =============================================================================

// Request interceptor with comprehensive logging
api.interceptors.request.use(
  (config) => {
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`
    config.metadata = { 
      startTime: Date.now(), 
      requestId,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString()
    }
    
    // Enhanced logging with more context
    apiLogger.info(`🚀 API Request Initiated [${config.method?.toUpperCase()}]`, {
      requestId,
      url: config.url,
      method: config.method,
      hasData: !!config.data,
      dataSize: config.data ? JSON.stringify(config.data).length : 0,
      timeout: config.timeout,
      headers: {
        'Content-Type': config.headers['Content-Type'],
        'User-Agent': config.headers['User-Agent']
      },
      baseURL: config.baseURL
    })
    
    // Log request payload for debugging (but limit size)
    if (config.data) {
      const dataSize = JSON.stringify(config.data).length
      if (dataSize < 2000) {
        apiLogger.debug(`📦 Request Payload [${requestId}]`, config.data)
      } else {
        apiLogger.debug(`📦 Large Request Payload [${requestId}]`, {
          size: `${Math.round(dataSize / 1024)}KB`,
          keys: typeof config.data === 'object' ? Object.keys(config.data) : 'non-object'
        })
      }
    }
    
    return config
  },
  (error) => {
    apiLogger.error('❌ Request interceptor error', error, {
      errorType: error.name,
      message: error.message,
      timestamp: new Date().toISOString()
    })
    return Promise.reject(error)
  }
)

// Response interceptor with enhanced logging
api.interceptors.response.use(
  (response) => {
    const { config } = response
    const duration = Date.now() - config.metadata.startTime
    const responseSize = response.data ? JSON.stringify(response.data).length : 0
    
    apiLogger.info(`✅ API Response Success [${response.status}]`, {
      requestId: config.metadata.requestId,
      url: config.url,
      method: config.method,
      status: response.status,
      statusText: response.statusText,
      duration: `${duration}ms`,
      responseSize: `${Math.round(responseSize / 1024)}KB`,
      hasData: !!response.data,
      contentType: response.headers?.['content-type']
    })
    
    // Log response payload for debugging (but limit size)
    if (response.data && responseSize < 2000) {
      apiLogger.debug(`📥 Response Payload [${config.metadata.requestId}]`, response.data)
    } else if (response.data) {
      apiLogger.debug(`📥 Large Response Payload [${config.metadata.requestId}]`, {
        size: `${Math.round(responseSize / 1024)}KB`,
        keys: typeof response.data === 'object' ? Object.keys(response.data) : 'non-object',
        hasResults: !!response.data.results,
        hasFieldAnalyses: !!(response.data.results?.field_analyses)
      })
    }
    
    // Performance monitoring
    if (duration > 5000) {
      apiLogger.warn(`⚠️ Slow API Response [${config.metadata.requestId}]`, {
        url: config.url,
        duration: `${duration}ms`,
        threshold: '5000ms'
      })
    }
    
    return response
  },
  (error) => {
    const config = error.config
    const duration = config?.metadata ? Date.now() - config.metadata.startTime : 0
    const status = error.response?.status
    const responseData = error.response?.data
    
    // Enhanced error logging with context
    apiLogger.error(`❌ API Request Failed`, error, {
      requestId: config?.metadata?.requestId,
      url: config?.url,
      method: config?.method,
      status: status,
      statusText: error.response?.statusText,
      duration: `${duration}ms`,
      message: error.message,
      errorType: error.name,
      isTimeout: error.code === 'ECONNABORTED' || error.message.includes('timeout'),
      isNetworkError: error.code === 'NETWORK_ERROR' || !error.response,
      responseData: responseData,
      timestamp: new Date().toISOString()
    })
    
    // Special handling for classification errors
    if (config?.url?.includes('/api/classify')) {
      apiLogger.error('🔍 Classification API Error - Critical Issue', null, {
        requestId: config?.metadata?.requestId,
        classification_context: {
          request_data_size: config?.data ? JSON.stringify(config.data).length : 0,
          selected_fields_count: config?.data?.selected_fields?.length,
          regulations: config?.data?.regulations,
          enable_ai: config?.data?.enable_ai,
          session_id: config?.data?.session_id
        },
        error_details: {
          is_timeout: error.code === 'ECONNABORTED',
          status_code: status,
          backend_message: responseData?.detail || responseData?.message
        }
      })
    }
    
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    
    // Don't show toast for cancelled requests
    if (error.code !== 'ERR_CANCELED') {
      toast.error(message)
    }
    
    return Promise.reject(error)
  }
)

// =============================================================================
// WORKFLOW API ENDPOINTS
// =============================================================================

export const workflowApi = {
  
  // ---------------------------------------------------------------------------
  // SYSTEM HEALTH AND STATUS
  // ---------------------------------------------------------------------------
  
  /**
   * Check backend service health and availability
   */
  healthCheck: async () => {
    try {
      const response = await api.get('/api/health')
      return response.data
    } catch (error) {
      throw new Error('Backend service unavailable')
    }
  },

  // ---------------------------------------------------------------------------
  // DATA PREPARATION ENDPOINTS
  // ---------------------------------------------------------------------------
  
  /**
   * Upload schema file for analysis
   */
  uploadSchema: async (file, fileType = 'ddl') => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('file_type', fileType)
    
    const response = await api.post('/api/upload-schema', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return response.data
  },

  // Step 2: Extract Schema
  extractSchema: async (sessionId) => {
    const response = await api.post(`/api/extract-schema/${sessionId}`)
    return response.data
  },

  // Step 3-6: Configure Scan Type
  configureScan: async (scanConfig) => {
    const response = await api.post('/api/configure-scan', scanConfig)
    return response.data
  },

  // Step 7-10: Classify Fields
  classifyFields: async (classificationRequest) => {
    const startTime = Date.now()
    
    // Enhanced pre-request logging for classification
    workflowLogger.info('🧠 Starting field classification', {
      session_id: classificationRequest.session_id,
      field_count: classificationRequest.selected_fields?.length || 0,
      regulations: classificationRequest.regulations,
      enable_ai: classificationRequest.enable_ai,
      timeout_seconds: classificationRequest.timeout_seconds,
      request_size: JSON.stringify(classificationRequest).length
    })
    
    try {
      // Use longer timeout for classification as it can take time with large datasets
      const response = await api.post('/api/classify', classificationRequest, {
        timeout: 240000 // 4 minutes for classification (increased for large datasets)
      })
      
      const processingTime = Date.now() - startTime
      
      // Enhanced post-response logging
      workflowLogger.info('✅ Classification completed successfully', {
        session_id: classificationRequest.session_id,
        processing_time: `${processingTime}ms`,
        response_status: response.status,
        has_results: !!response.data?.results,
        has_field_analyses: !!(response.data?.results?.field_analyses),
        field_analyses_count: response.data?.results?.field_analyses ? 
          Object.keys(response.data.results.field_analyses).length : 0,
        summary_message: response.data?.results?.summary?.message
      })
      
      return response.data
      
    } catch (error) {
      const processingTime = Date.now() - startTime
      
      // Enhanced error logging for classification
      workflowLogger.error('❌ Classification failed', error, {
        session_id: classificationRequest.session_id,
        processing_time: `${processingTime}ms`,
        error_type: error.name,
        is_timeout: error.code === 'ECONNABORTED' || error.message.includes('timeout'),
        status_code: error.response?.status,
        backend_error: error.response?.data?.detail || error.response?.data?.message,
        request_context: {
          field_count: classificationRequest.selected_fields?.length,
          enable_ai: classificationRequest.enable_ai,
          regulations: classificationRequest.regulations
        }
      })
      
      throw error
    }
  },

  // Step 11: Validate Results
  validateResults: async (validationRequest) => {
    const response = await api.post('/api/validate-results', validationRequest)
    return response.data
  },

  // Step 12: Generate Report
  generateReport: async (sessionId, format = 'json') => {
    const response = await api.post(`/api/generate-report/${sessionId}?format=${format}`)
    return response.data
  },

  // Get all reports
  getReports: async () => {
    const response = await api.get('/api/reports')
    return response.data
  },

  // Get specific report details
  getReportDetails: async (sessionId) => {
    const response = await api.get(`/api/reports/${sessionId}`)
    return response.data
  },

  // Get session status
  getSessionStatus: async (sessionId) => {
    const response = await api.get(`/api/session/${sessionId}/status`)
    return response.data
  },

  // Get performance stats
  getPerformanceStats: async () => {
    const response = await api.get('/api/performance/stats')
    return response.data
  },

  /**
   * Connect to database and extract schema
   */
  connectDatabase: async (connectionConfig) => {
    try {
      const response = await api.post('/api/connect-database', connectionConfig)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Database connection failed')
    }
  },

  /**
   * Test database connection without extracting schema
   */
  testDatabaseConnection: async (connectionConfig) => {
    try {
      const response = await api.post('/api/test-database-connection', connectionConfig)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Connection test failed')
    }
  }
}

// Database connectivity API calls
export const connectDatabase = async (connectionConfig) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/connect-database`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(connectionConfig),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || `Database connection failed: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Database connection error:', error)
    throw error
  }
}

export const testDatabaseConnection = async (connectionConfig) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/test-database-connection`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(connectionConfig),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || `Connection test failed: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Database connection test error:', error)
    throw error
  }
}
export const apiUtils = {
  // Format file size
  formatFileSize: (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  },

  // Validate file type
  validateFileType: (file, allowedTypes = ['ddl', 'sql', 'json', 'csv', 'xlsx']) => {
    const extension = file.name.split('.').pop().toLowerCase()
    return allowedTypes.includes(extension)
  },

  // Format date
  formatDate: (dateString) => {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(dateString))
  }
}

export default api