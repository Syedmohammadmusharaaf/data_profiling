/**
 * PII Scanner Enterprise - Main Application Component
 * ==================================================
 * 
 * This is the root component of the React frontend application for the PII Scanner
 * Enterprise system. It provides the main application structure, routing, and
 * global styling framework.
 * 
 * Key Features:
 * - Multi-page application with React Router navigation
 * - Responsive design with Tailwind CSS styling
 * - Motion animations for smooth user experience
 * - Header navigation component integration
 * 
 * Application Routes:
 * - / : Main PII scanning workflow (4-step process)
 * - /dashboard : System overview and recent scan results
 * - /reports : Historical scan reports and export functionality
 * 
 * Architecture:
 * - Uses React Router for client-side routing
 * - Framer Motion for smooth page transitions
 * - Tailwind CSS for responsive, utility-first styling
 * - Component-based architecture for maintainability
 * 
 * @author PII Scanner Team
 * @version 2.0.0
 * @since 2024-12-29
 */

// React core imports
import React, { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'

// Application component imports
import Header from './components/Layout/Header'
import WorkflowManager from './components/Workflow/WorkflowManager'
import Dashboard from './components/Dashboard/Dashboard'
import Reports from './components/Reports/Reports'

// Enhanced logging
import { logger, useLogger } from './utils/logger'

/**
 * Main Application Component
 * 
 * Renders the complete PII Scanner Enterprise application with:
 * - Global layout structure and styling
 * - Header navigation component
 * - Main content area with routing
 * - Smooth animations and transitions
 * - Enhanced logging for debugging
 * 
 * @returns {JSX.Element} Complete application UI
 */
function App() {
  const appLogger = useLogger('App')
  
  useEffect(() => {
    // Initialize application logging
    appLogger.logMount()
    appLogger.info('PII Scanner Enterprise application initialized', {
      version: '2.0.0',
      environment: process.env.NODE_ENV,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      }
    })
    
    // Log page visibility changes for debugging
    const handleVisibilityChange = () => {
      appLogger.info(`Page visibility changed`, { 
        hidden: document.hidden,
        visibilityState: document.visibilityState 
      })
    }
    
    // Log errors that bubble up to the app level
    const handleError = (event) => {
      appLogger.error('Unhandled application error', event.error, {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      })
    }
    
    // Log unhandled promise rejections
    const handleUnhandledRejection = (event) => {
      appLogger.error('Unhandled promise rejection', event.reason)
    }
    
    document.addEventListener('visibilitychange', handleVisibilityChange)
    window.addEventListener('error', handleError)
    window.addEventListener('unhandledrejection', handleUnhandledRejection)
    
    // Cleanup
    return () => {
      appLogger.logUnmount()
      document.removeEventListener('visibilitychange', handleVisibilityChange)
      window.removeEventListener('error', handleError)
      window.removeEventListener('unhandledrejection', handleUnhandledRejection)
    }
  }, [appLogger])
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Application Header - Navigation and Branding */}
      <Header />
      
      {/* Main Content Area - Animated container for all pages */}
      <motion.main 
        className="container mx-auto px-4 py-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {/* Application Routes - Client-side routing configuration */}
        <Routes>
          {/* Default Route: Main PII Scanning Workflow */}
          <Route path="/" element={<WorkflowManager />} />
          
          {/* Dashboard Route: System overview and metrics */}
          <Route path="/dashboard" element={<Dashboard />} />
          
          {/* Reports Route: Historical data and export tools */}
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </motion.main>
    </div>
  )
}

export default App