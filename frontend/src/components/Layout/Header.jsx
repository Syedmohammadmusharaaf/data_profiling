import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Shield, Activity, FileText, Home } from 'lucide-react'
import { motion } from 'framer-motion'

const Header = () => {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: 'Scanner', icon: Home, id: 'nav-scanner' },
    { path: '/dashboard', label: 'Dashboard', icon: Activity, id: 'nav-dashboard' },
    { path: '/reports', label: 'Reports', icon: FileText, id: 'nav-reports' }
  ]
  
  return (
    <motion.header 
      id="main-header"
      className="bg-white shadow-sm border-b border-gray-200"
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div id="header-logo" className="flex items-center space-x-3">
            <div id="logo-icon" className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-lg">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <div id="logo-text">
              <h1 className="text-xl font-bold text-gray-900">PII Scanner Enterprise</h1>
              <p className="text-xs text-gray-500">Data Privacy & Compliance</p>
            </div>
          </div>
          
          {/* Navigation */}
          <nav id="main-navigation" className="flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              
              return (
                <Link
                  key={item.path}
                  id={item.id}
                  to={item.path}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors duration-200 ${
                    isActive 
                      ? 'bg-blue-100 text-blue-700 font-medium' 
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span className="text-sm">{item.label}</span>
                </Link>
              )
            })}
          </nav>
          
          {/* Status Indicator */}
          <div id="system-status" className="flex items-center space-x-2">
            <div className="flex items-center space-x-1">
              <div id="status-indicator" className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span id="status-text" className="text-sm text-gray-600">System Online</span>
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  )
}

export default Header