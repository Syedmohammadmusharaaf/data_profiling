import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  FileText, 
  Download, 
  Calendar, 
  Filter, 
  Eye,
  Share2,
  Search,
  AlertTriangle,
  Shield,
  CheckCircle,
  Clock,
  BarChart3
} from 'lucide-react'

const Reports = () => {
  const [reports, setReports] = useState([])
  const [filteredReports, setFilteredReports] = useState([])
  const [filters, setFilters] = useState({
    dateRange: 'last_30_days',
    reportType: 'all',
    status: 'all',
    riskLevel: 'all'
  })
  const [searchTerm, setSearchTerm] = useState('')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadReports()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [reports, filters, searchTerm])

  const loadReports = async () => {
    setIsLoading(true)
    try {
      // Import the API service
      const { workflowApi } = await import('../../services/api')
      
      // Fetch real reports from backend
      const response = await workflowApi.getReports()
      
      if (response.status === 'success') {
        setReports(response.reports || [])
        // Successfully loaded reports from backend
      } else {
        throw new Error('Failed to load reports')
      }
      
    } catch (error) {
      console.error('Error loading reports:', error)
      
      // Fallback to mock data if API fails
      const mockReports = [
        {
          id: 1,
          session_id: 'mock-session-1',
          name: 'Sample Customer Database HIPAA Scan',
          fileName: 'customer_database.sql',
          type: 'HIPAA',
          status: 'completed',
          createdDate: '2025-01-30',
          riskLevel: 'HIGH',
          piiFields: 23,
          totalFields: 87,
          complianceScore: 87,
          scanDuration: '2.3s',
          regulations: ['HIPAA', 'GDPR']
        },
        {
          id: 2,
          session_id: 'mock-session-2',
          name: 'Sample Employee Records GDPR Analysis',
          fileName: 'employee_records.ddl',
          type: 'GDPR',
          status: 'completed',
          createdDate: '2025-01-29',
          riskLevel: 'MEDIUM',
          piiFields: 15,
          totalFields: 45,
          complianceScore: 94,
          scanDuration: '1.8s',
          regulations: ['GDPR', 'CCPA']
        }
      ]
      
      setReports(mockReports)
      // Using fallback mock data due to API error
      
    } finally {
      setIsLoading(false)
    }
  }

  const applyFilters = () => {
    let filtered = reports.filter(report => {
      // Search term filter
      const matchesSearch = !searchTerm || 
        report.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        report.fileName.toLowerCase().includes(searchTerm.toLowerCase())

      // Date range filter (simplified)
      const matchesDate = filters.dateRange === 'all' || 
        (filters.dateRange === 'last_7_days' && isWithinDays(report.createdDate, 7)) ||
        (filters.dateRange === 'last_30_days' && isWithinDays(report.createdDate, 30)) ||
        (filters.dateRange === 'last_90_days' && isWithinDays(report.createdDate, 90))

      // Report type filter
      const matchesType = filters.reportType === 'all' || report.type === filters.reportType

      // Status filter
      const matchesStatus = filters.status === 'all' || report.status === filters.status

      // Risk level filter
      const matchesRisk = filters.riskLevel === 'all' || report.riskLevel === filters.riskLevel

      return matchesSearch && matchesDate && matchesType && matchesStatus && matchesRisk
    })

    setFilteredReports(filtered)
  }

  const isWithinDays = (dateString, days) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now - date)
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays <= days
  }

  const getRiskLevelColor = (riskLevel) => {
    switch (riskLevel) {
      case 'HIGH': return 'text-red-600 bg-red-100'
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-100'
      case 'LOW': return 'text-green-600 bg-green-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'in_progress': return <Clock className="w-4 h-4 text-yellow-500" />
      case 'failed': return <AlertTriangle className="w-4 h-4 text-red-500" />
      default: return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const downloadReport = (reportId) => {
    // Simulate download
    // Generate download for the report
    // Implementation would handle report download
    // In real implementation, this would trigger a download
  }

  const viewReport = async (reportId) => {
    try {
      // Import the API service
      const { workflowApi } = await import('../../services/api')
      
      console.log(`Viewing report ${reportId}`)
      
      // Fetch detailed report data
      const response = await workflowApi.getReportDetails(reportId)
      
      if (response.status === 'success') {
        // Create a new window/tab to show the report
        const reportWindow = window.open('', '_blank')
        const reportData = response.report_data
        const metadata = response.metadata
        
        // Create a formatted report view
        const reportHtml = `
          <!DOCTYPE html>
          <html>
          <head>
            <title>PII Scan Report - ${reportId}</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              .header { border-bottom: 2px solid #ddd; padding-bottom: 10px; margin-bottom: 20px; }
              .summary { background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
              .fields { margin-top: 20px; }
              .field { border: 1px solid #ddd; margin: 10px 0; padding: 10px; border-radius: 4px; }
              .pii-field { background-color: #fee; border-color: #fcc; }
              .non-pii-field { background-color: #efe; border-color: #cfc; }
              .risk-high { border-left: 4px solid #dc3545; }
              .risk-medium { border-left: 4px solid #ffc107; }
              .risk-low { border-left: 4px solid #28a745; }
            </style>
          </head>
          <body>
            <div class="header">
              <h1>PII/PHI Scan Report</h1>
              <p><strong>Report ID:</strong> ${reportId}</p>
              <p><strong>File:</strong> ${metadata?.original_filename || 'Unknown'}</p>
              <p><strong>Scan Type:</strong> ${metadata?.scan_type || 'Comprehensive'}</p>
              <p><strong>Generated:</strong> ${new Date(metadata?.created_at || Date.now()).toLocaleString()}</p>
            </div>
            
            <div class="summary">
              <h2>Summary</h2>
              <p><strong>Total Fields:</strong> ${reportData?.summary?.total_fields || 0}</p>
              <p><strong>PII Fields:</strong> ${reportData?.summary?.pii_fields || 0}</p>
              <p><strong>High Risk Fields:</strong> ${reportData?.summary?.high_risk || 0}</p>
              <p><strong>Status:</strong> ${reportData?.status || 'Unknown'}</p>
            </div>
            
            <div class="fields">
              <h2>Field Analysis</h2>
              ${Object.entries(reportData?.field_analyses || {}).map(([fieldKey, fieldData]) => `
                <div class="field ${fieldData.is_sensitive ? 'pii-field' : 'non-pii-field'} risk-${(fieldData.risk_level || 'low').toLowerCase()}">
                  <h3>${fieldData.field_name || fieldKey}</h3>
                  <p><strong>Classification:</strong> ${fieldData.pii_type || 'Unknown'}</p>
                  <p><strong>Risk Level:</strong> ${fieldData.risk_level || 'Unknown'}</p>
                  <p><strong>Confidence:</strong> ${Math.round((fieldData.confidence_score || 0) * 100)}%</p>
                  <p><strong>Source:</strong> ${fieldData.source || 'Unknown'}</p>
                  <p><strong>Rationale:</strong> ${fieldData.rationale || 'No rationale provided'}</p>
                </div>
              `).join('')}
            </div>
          </body>
          </html>
        `
        
        reportWindow.document.write(reportHtml)
        reportWindow.document.close()
        
      } else {
        alert('Failed to load report details')
      }
      
    } catch (error) {
      console.error('Error viewing report:', error)
      alert('Failed to open report. Please try again.')
    }
  }

  const shareReport = async (reportId) => {
    try {
      // Create shareable link or copy report URL
      const shareUrl = `${window.location.origin}/reports/${reportId}`
      
      if (navigator.share) {
        // Use native sharing if available
        await navigator.share({
          title: `PII Scan Report - ${reportId}`,
          text: 'Check out this PII scan report',
          url: shareUrl
        })
      } else if (navigator.clipboard) {
        // Fallback to clipboard
        await navigator.clipboard.writeText(shareUrl)
        alert('Report link copied to clipboard!')
      } else {
        // Final fallback
        prompt('Copy this link to share the report:', shareUrl)
      }
      
      // Report sharing completed successfully
      
    } catch (error) {
      console.error('Error sharing report:', error)
      alert('Failed to share report')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Compliance Reports</h1>
        <p className="text-gray-600">Access and manage your PII/PHI scanning reports and compliance documentation</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Reports</p>
              <p className="text-2xl font-bold text-gray-900">{reports.length}</p>
            </div>
            <FileText className="w-8 h-8 text-blue-500" />
          </div>
        </motion.div>

        <motion.div
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Compliance Score</p>
              <p className="text-2xl font-bold text-gray-900">
                {Math.round(reports.reduce((acc, r) => acc + r.complianceScore, 0) / reports.length) || 0}%
              </p>
            </div>
            <BarChart3 className="w-8 h-8 text-green-500" />
          </div>
        </motion.div>

        <motion.div
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">High Risk Reports</p>
              <p className="text-2xl font-bold text-gray-900">
                {reports.filter(r => r.riskLevel === 'HIGH').length}
              </p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
        </motion.div>

        <motion.div
          className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total PII Fields</p>
              <p className="text-2xl font-bold text-gray-900">
                {reports.reduce((acc, r) => acc + r.piiFields, 0)}
              </p>
            </div>
            <Shield className="w-8 h-8 text-purple-500" />
          </div>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-6">
            <div className="flex items-center space-x-2 mb-4">
              <Filter className="w-5 h-5 text-gray-500" />
              <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
            </div>
            
            {/* Search */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  className="form-input pl-10"
                  placeholder="Search reports..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
                <select 
                  className="form-select"
                  value={filters.dateRange}
                  onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                >
                  <option value="all">All time</option>
                  <option value="last_7_days">Last 7 days</option>
                  <option value="last_30_days">Last 30 days</option>
                  <option value="last_90_days">Last 90 days</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Report Type</label>
                <select 
                  className="form-select"
                  value={filters.reportType}
                  onChange={(e) => handleFilterChange('reportType', e.target.value)}
                >
                  <option value="all">All Types</option>
                  <option value="HIPAA">HIPAA Reports</option>
                  <option value="GDPR">GDPR Reports</option>
                  <option value="CCPA">CCPA Reports</option>
                  <option value="ALL">Comprehensive</option>
                  <option value="Basic">Basic Scan</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select 
                  className="form-select"
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                >
                  <option value="all">All Status</option>
                  <option value="completed">Completed</option>
                  <option value="in_progress">In Progress</option>
                  <option value="failed">Failed</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Risk Level</label>
                <select 
                  className="form-select"
                  value={filters.riskLevel}
                  onChange={(e) => handleFilterChange('riskLevel', e.target.value)}
                >
                  <option value="all">All Risk Levels</option>
                  <option value="HIGH">High Risk</option>
                  <option value="MEDIUM">Medium Risk</option>
                  <option value="LOW">Low Risk</option>
                </select>
              </div>
              
              <button 
                className="btn-primary w-full flex items-center justify-center space-x-2"
                onClick={() => setFilters({
                  dateRange: 'last_30_days',
                  reportType: 'all',
                  status: 'all',
                  riskLevel: 'all'
                })}
              >
                <Filter className="w-4 h-4" />
                <span>Reset Filters</span>
              </button>
            </div>
          </div>
        </div>

        {/* Reports List */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  Reports ({filteredReports.length})
                </h3>
                <div className="flex items-center space-x-2">
                  <button className="btn-secondary text-sm">
                    Export All
                  </button>
                </div>
              </div>
            </div>
            
            <div className="divide-y divide-gray-200">
              {filteredReports.length > 0 ? (
                filteredReports.map((report, index) => (
                  <motion.div
                    key={report.id}
                    className="p-6 hover:bg-gray-50 transition-colors"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-3 mb-2">
                          <h4 className="text-lg font-medium text-gray-900 truncate">
                            {report.name}
                          </h4>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskLevelColor(report.riskLevel)}`}>
                            {report.riskLevel}
                          </span>
                        </div>
                        
                        <p className="text-sm text-gray-600 mb-3">
                          File: {report.fileName}
                        </p>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">PII Fields:</span>
                            <span className="ml-1 font-medium">{report.piiFields}/{report.totalFields}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Compliance:</span>
                            <span className="ml-1 font-medium">{report.complianceScore}%</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Duration:</span>
                            <span className="ml-1 font-medium">{report.scanDuration}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Date:</span>
                            <span className="ml-1 font-medium">{report.createdDate}</span>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2 mt-3">
                          <span className="text-xs text-gray-500">Regulations:</span>
                          {report.regulations.map((reg, idx) => (
                            <span 
                              key={idx} 
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                            >
                              {reg}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-4 ml-6">
                        <div className="flex items-center space-x-1">
                          {getStatusIcon(report.status)}
                          <span className="text-sm text-gray-600 capitalize">
                            {report.status.replace('_', ' ')}
                          </span>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => viewReport(report.id)}
                            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                            title="View Report"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          
                          <button
                            onClick={() => downloadReport(report.id)}
                            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                            title="Download Report"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          
                          <button
                            onClick={() => shareReport(report.id)}
                            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                            title="Share Report"
                          >
                            <Share2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-12">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 text-lg">No reports match your current filters.</p>
                  <p className="text-sm text-gray-400 mt-2">
                    Try adjusting your search criteria or create a new scan.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Reports