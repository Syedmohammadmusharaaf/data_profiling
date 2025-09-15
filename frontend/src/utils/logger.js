/**
 * Enhanced Logging System for PII Scanner Frontend
 * ==============================================
 * 
 * Comprehensive logging utility with error tracking,
 * performance monitoring, and user action logging
 */

const LOG_LEVELS = {
  ERROR: 'ERROR',
  WARN: 'WARN',
  INFO: 'INFO',
  DEBUG: 'DEBUG'
}

const LOG_COLORS = {
  ERROR: '#dc2626',   // red-600
  WARN: '#d97706',    // yellow-600
  INFO: '#2563eb',    // blue-600
  DEBUG: '#059669',   // green-600
}

class FrontendLogger {
  constructor(context = 'APP') {
    this.context = context
    this.logBuffer = []
    this.maxBufferSize = 1000
    this.sessionId = this.generateSessionId()
    this.startTime = Date.now()
    
    // Circuit breaker for backend reporting
    this.backendReportingFailures = 0
    this.maxBackendFailures = 2
    this.backendReportingDisabledUntil = 0
    
    // Deduplication and rate limiting
    this.recentMessages = new Map()
    this.messageTimeout = 5000 // 5 seconds
    this.maxLogsPerSecond = 10
    this.logTimestamps = []
    
    // Initialize logger
    this.info('🚀 Frontend logger initialized', { 
      context: this.context,
      sessionId: this.sessionId,
      timestamp: new Date().toISOString()
    })
    
    // Setup error capture
    this.setupGlobalErrorHandling()
  }
  
  generateSessionId() {
    return `frontend_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  formatMessage(level, message, data = null, error = null) {
    const timestamp = new Date().toISOString()
    const logEntry = {
      timestamp,
      level,
      context: this.context,
      sessionId: this.sessionId,
      message,
      data: data || {},
      error: error ? {
        name: error.name,
        message: error.message,
        stack: error.stack
      } : null,
      url: window.location.href,
      userAgent: navigator.userAgent
    }
    
    // Add to buffer
    this.addToBuffer(logEntry)
    
    return logEntry
  }
  
  addToBuffer(logEntry) {
    this.logBuffer.push(logEntry)
    
    // Maintain buffer size
    if (this.logBuffer.length > this.maxBufferSize) {
      this.logBuffer = this.logBuffer.slice(-this.maxBufferSize)
    }
  }
  
  // Rate limiting check
  isRateLimited() {
    const now = Date.now()
    // Remove timestamps older than 1 second
    this.logTimestamps = this.logTimestamps.filter(t => now - t < 1000)
    
    if (this.logTimestamps.length >= this.maxLogsPerSecond) {
      return true
    }
    
    this.logTimestamps.push(now)
    return false
  }

  // Deduplication check
  isDuplicate(level, message) {
    const key = `${level}:${message}`
    const now = Date.now()
    
    if (this.recentMessages.has(key)) {
      const lastSeen = this.recentMessages.get(key)
      if (now - lastSeen < this.messageTimeout) {
        return true // Duplicate within timeout period
      }
    }
    
    this.recentMessages.set(key, now)
    return false
  }
  
  log(level, message, data = null, error = null) {
    try {
      // Rate limiting check
      if (this.isRateLimited()) {
        return // Silently drop if rate limited
      }

      // Deduplication check
      if (this.isDuplicate(level, message)) {
        return // Silently drop duplicates
      }

      const logEntry = this.formatMessage(level, message, data, error)
      
      // Console output (safe)
      try {
        const color = LOG_COLORS[level] || '#666666'
        const prefix = `[${this.context}]`
        
        if (error) {
          console.groupCollapsed(`%c${prefix} ${level}: ${message}`, `color: ${color}; font-weight: bold`)
          console.error('Error:', error)
          if (data) console.log('Data:', data)
          console.log('Full log entry:', logEntry)
          console.groupEnd()
        } else {
          console.log(`%c${prefix} ${level}: ${message}`, `color: ${color}; font-weight: bold`, data || '')
        }
      } catch (e) {
        // Ignore console errors
      }
      
      // Backend reporting (only for errors and warnings, with additional safety)
      if ((level === LOG_LEVELS.ERROR || level === LOG_LEVELS.WARN) && 
          !message.includes('Failed to report error') && 
          this.shouldReportError(error)) {
        this.safeReportToBackend(logEntry)
      }
      
    } catch (e) {
      // Never let logging crash the app
      console.warn('Logger internal error:', e.message)
    }
  }
  
  debug(message, data = null) {
    this.log(LOG_LEVELS.DEBUG, message, data)
  }
  
  info(message, data = null) {
    this.log(LOG_LEVELS.INFO, message, data)
  }
  
  warn(message, data = null, error = null) {
    this.log(LOG_LEVELS.WARN, message, data, error)
  }
  
  error(message, error = null, data = null) {
    this.log(LOG_LEVELS.ERROR, message, data, error)
  }
  
  shouldReportError(error) {
    if (!error) return false
    
    // Don't report certain types of errors
    const ignoredErrors = [
      'ResizeObserver loop limit exceeded',
      'Script error.',
      'Non-Error promise rejection captured'
    ]
    
    return !ignoredErrors.some(ignored => 
      error.message && error.message.includes(ignored)
    )
  }
  
  // Safe wrapper for backend reporting
  safeReportToBackend(logEntry) {
    try {
      this.reportErrorToBackend(logEntry)
    } catch (e) {
      // Never let backend reporting crash the app
      console.warn('Safe backend reporting failed:', e.message)
    }
  }
  
  // Safe wrapper for backend reporting
  safeReportToBackend(logEntry) {
    try {
      this.reportErrorToBackend(logEntry)
    } catch (e) {
      // Never let backend reporting crash the app
    }
  }

  async reportErrorToBackend(logEntry) {
    // Circuit breaker - don't try if we've failed too many times recently
    const now = Date.now()
    if (this.backendReportingFailures >= this.maxBackendFailures && 
        now < this.backendReportingDisabledUntil) {
      return // Silently fail
    }
    
    try {
      // Always use same origin for preview environment - no localhost:8001
      const backendUrl = window.location.origin
      
      const errorReport = {
        timestamp: logEntry.timestamp,
        level: logEntry.level,
        message: logEntry.message,
        error: logEntry.error,
        sessionId: this.sessionId
      }
      
      const response = await fetch(`${backendUrl}/api/log-frontend-error`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(errorReport)
      })
      
      if (response.ok) {
        // Reset circuit breaker on success
        this.backendReportingFailures = 0
        this.backendReportingDisabledUntil = 0
      } else {
        throw new Error(`Status: ${response.status}`)
      }
      
    } catch (e) {
      // Increment failure counter and set circuit breaker
      this.backendReportingFailures++
      if (this.backendReportingFailures >= this.maxBackendFailures) {
        // Disable for 30 seconds only
        this.backendReportingDisabledUntil = now + 30000
      }
    }
  }
  
  setupGlobalErrorHandling() {
    // Capture unhandled JavaScript errors
    window.addEventListener('error', (event) => {
      this.error('Unhandled JavaScript error', event.error, {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        message: event.message
      })
    })
    
    // Capture unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.error('Unhandled promise rejection', event.reason, {
        promise: event.promise
      })
    })
    
    // Capture React errors (if using error boundary)
    window.addEventListener('react-error', (event) => {
      this.error('React error boundary triggered', event.detail.error, {
        errorInfo: event.detail.errorInfo
      })
    })
  }
  
  // Performance monitoring
  startTimer(name) {
    const timerId = `${name}_${Date.now()}`
    console.time(timerId)
    return {
      end: () => {
        console.timeEnd(timerId)
        const duration = performance.now() - performance.mark(timerId).startTime
        this.debug(`Performance: ${name} completed`, { duration: `${duration.toFixed(2)}ms` })
        return duration
      }
    }
  }
  
  // API call logging
  logApiCall(method, url, requestData = null) {
    const apiTimer = this.startTimer(`API_${method}_${url}`)
    
    this.info(`🌐 API Call: ${method} ${url}`, { 
      method, 
      url, 
      hasRequestData: !!requestData,
      requestSize: requestData ? JSON.stringify(requestData).length : 0
    })
    
    return {
      logResponse: (status, responseData = null, error = null) => {
        const duration = apiTimer.end()
        
        if (error) {
          this.error(`❌ API Call Failed: ${method} ${url}`, error, {
            status,
            duration: `${duration.toFixed(2)}ms`,
            hasResponseData: !!responseData
          })
        } else {
          const level = status >= 400 ? 'error' : status >= 300 ? 'warn' : 'info'
          const emoji = status >= 400 ? '❌' : status >= 300 ? '⚠️' : '✅'
          
          this[level](`${emoji} API Call: ${method} ${url} [${status}]`, {
            status,
            duration: `${duration.toFixed(2)}ms`,
            hasResponseData: !!responseData,
            responseSize: responseData ? JSON.stringify(responseData).length : 0
          })
        }
      }
    }
  }
  
  // User action logging
  logUserAction(action, details = {}) {
    this.info(`👤 User Action: ${action}`, {
      action,
      ...details,
      timestamp: new Date().toISOString(),
      page: window.location.pathname
    })
  }
  
  // Component lifecycle logging
  logComponentEvent(componentName, event, data = null) {
    this.debug(`🔄 Component ${componentName}: ${event}`, data)
  }
  
  // Workflow step logging
  logWorkflowStep(step, action, data = null) {
    this.info(`📋 Workflow [${step}]: ${action}`, data)
  }
  
  // Data flow logging
  logDataFlow(stage, description, dataSize = null) {
    this.info(`📊 Data Flow [${stage}]: ${description}`, { 
      dataSize: dataSize ? `${dataSize} items` : 'unknown'
    })
  }
  
  // Get logs for debugging
  getLogs(level = null, limit = 100) {
    let logs = this.logBuffer
    
    if (level) {
      logs = logs.filter(log => log.level === level)
    }
    
    return logs.slice(-limit)
  }
  
  // Export logs
  exportLogs() {
    const exportData = {
      sessionId: this.sessionId,
      exportTime: new Date().toISOString(),
      sessionDuration: Date.now() - this.startTime,
      userAgent: navigator.userAgent,
      url: window.location.href,
      logs: this.logBuffer
    }
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
      type: 'application/json' 
    })
    
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `pii-scanner-logs-${this.sessionId}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    this.info('📥 Logs exported', { filename: a.download })
  }
  
  // Clear logs
  clearLogs() {
    const logCount = this.logBuffer.length
    this.logBuffer = []
    this.info('🗑️ Logs cleared', { clearedCount: logCount })
  }
}

// Create context-specific loggers
export const createLogger = (context) => new FrontendLogger(context)

// Default logger instance
export const logger = new FrontendLogger('PII_SCANNER')

// Specialized loggers
export const apiLogger = createLogger('API')
export const workflowLogger = createLogger('WORKFLOW')
export const componentLogger = createLogger('COMPONENT')
export const errorLogger = createLogger('ERROR')

// Utility functions
export const logPerformance = (name, fn) => {
  return async (...args) => {
    const timer = logger.startTimer(name)
    try {
      const result = await fn(...args)
      timer.end()
      return result
    } catch (error) {
      timer.end()
      logger.error(`Performance monitoring failed for ${name}`, error)
      throw error
    }
  }
}

// React hook for component logging
export const useLogger = (componentName) => {
  const componentLog = createLogger(`COMP_${componentName}`)
  
  return {
    debug: (message, data) => componentLog.debug(`[${componentName}] ${message}`, data),
    info: (message, data) => componentLog.info(`[${componentName}] ${message}`, data),
    warn: (message, data, error) => componentLog.warn(`[${componentName}] ${message}`, data, error),
    error: (message, error, data) => componentLog.error(`[${componentName}] ${message}`, error, data),
    logMount: () => componentLog.debug(`[${componentName}] Component mounted`),
    logUnmount: () => componentLog.debug(`[${componentName}] Component unmounted`),
    logRender: (props) => componentLog.debug(`[${componentName}] Component rendered`, { propsCount: props ? Object.keys(props).length : 0 }),
    logEvent: (event, data) => componentLog.info(`[${componentName}] Event: ${event}`, data)
  }
}

// Debug utilities for development
export const debugUtils = {
  showLogs: () => logger.getLogs(),
  exportLogs: () => logger.exportLogs(),
  clearLogs: () => logger.clearLogs(),
  logLevel: (level) => logger.getLogs(level),
  errors: () => logger.getLogs('ERROR'),
  performance: () => {
    const perfEntries = performance.getEntriesByType('measure')
    logger.info('Performance entries', perfEntries)
    return perfEntries
  }
}

// Make debug utils available globally in development
if (process.env.NODE_ENV === 'development') {
  window.debugLogger = debugUtils
}

export default logger