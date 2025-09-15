/**
 * Enhanced Dashboard with Integrated Schema Visualizer
 * ===================================================
 * 
 * Dashboard component that integrates the Schema Visualizer directly
 * instead of using a popup modal. Provides unified experience for
 * viewing scan results and generating masking plans.
 * 
 * @author PII Scanner Team
 * @version 2.0.0
 */

import React, { useState, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Activity, 
  TrendingUp, 
  Shield, 
  Clock, 
  AlertTriangle,
  CheckCircle,
  Database,
  FileText,
  Settings,
  BarChart3,
  PieChart,
  Download,
  Grid,
  Target,
  List,
  Eye,
  Filter,
  Search,
  RefreshCw
} from 'lucide-react'

// Import Schema Visualizer components
import TableHeatmap from '../Visualizer/components/TableHeatmap'
import TreemapVisualization from '../Visualizer/components/TreemapVisualization'
import ScatterQuadrant from '../Visualizer/components/ScatterQuadrant'
import FindingsList from '../Visualizer/components/FindingsList'
import TopRiskyColumns from '../Visualizer/components/TopRiskyColumns'
import RegulationPieChart from '../Visualizer/components/RegulationPieChart'
import SankeyFlow from '../Visualizer/components/SankeyFlow'
import MaskingPlanExport from '../Visualizer/components/MaskingPlanExport'

// Import utilities
import { convertReportToArray, aggregateByTable, aggregateByRegulation } from '../Visualizer/utils/dataProcessor'
import { workflowApi } from '../../services/api'

const Dashboard = () => {
  // Generate mock data for demonstration
  const generateMockData = () => {
    return [
      { table: 'patient_records', column: 'patient_id', classification: 'PHI', regulations: ['HIPAA'], risk_score: 85, justification: 'Patient identifier' },
      { table: 'patient_records', column: 'medical_record_number', classification: 'PHI', regulations: ['HIPAA'], risk_score: 95, justification: 'Medical record identifier' },
      { table: 'patient_records', column: 'first_name', classification: 'PHI', regulations: ['HIPAA'], risk_score: 70, justification: 'Personal identifier' },
      { table: 'customer_accounts', column: 'email_address', classification: 'PII', regulations: ['GDPR'], risk_score: 80, justification: 'Personal contact information' },
      { table: 'customer_accounts', column: 'credit_card_number', classification: 'PII', regulations: ['PCI-DSS'], risk_score: 95, justification: 'Financial information' },
      { table: 'employee_directory', column: 'social_security_number', classification: 'PII', regulations: ['GDPR'], risk_score: 90, justification: 'Government identifier' }
    ]
  }

  // State management
  const [activeTab, setActiveTab] = useState('overview')
  const [dashboardData, setDashboardData] = useState({
    recentScans: [],
    latestScanResults: null,
    systemStats: {},
    complianceOverview: {},
    riskMetrics: {}
  })
  const [isLoading, setIsLoading] = useState(true)
  const [showExportPlan, setShowExportPlan] = useState(false)
  
  // Schema Visualizer state
  const [activeView, setActiveView] = useState('heatmap')
  const [filters, setFilters] = useState({
    regulation: 'all',
    classification: 'all',
    minRisk: 0,
    search: ''
  })

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    setIsLoading(true)
    try {
      // Try to load the latest scan results from localStorage or API
      const latestScan = localStorage.getItem('latestScanResults')
      const latestScanResults = latestScan ? JSON.parse(latestScan) : null
      
      setDashboardData({
        recentScans: [
          {
            id: 1,
            fileName: 'simple_test_ddl.sql',
            scanDate: new Date().toISOString().split('T')[0],
            status: 'completed',
            piiFields: 18,
            riskLevel: 'MEDIUM',
            sessionId: '1b569579-672c-4bb8-8866-25317aa31b86'
          },
          {
            id: 2,
            fileName: 'employee_records.ddl',
            scanDate: '2025-01-29',
            status: 'completed',
            piiFields: 12,
            riskLevel: 'LOW'
          },
          {
            id: 3,
            fileName: 'customer_database.sql',
            scanDate: '2025-01-28',
            status: 'completed',
            piiFields: 34,
            riskLevel: 'HIGH'
          }
        ],
        latestScanResults,
        systemStats: {
          totalScans: 156,
          sensitiveFieldsFound: 2847,
          complianceViolations: 23,
          avgProcessingTime: '2.3s'
        },
        complianceOverview: {
          hipaa: { compliant: 78, violations: 5 },
          gdpr: { compliant: 145, violations: 12 },
          ccpa: { compliant: 92, violations: 3 }
        },
        riskMetrics: {
          critical: 8,
          high: 34,
          medium: 127,
          low: 89
        }
      })
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Process visualization data
  const normalizedData = useMemo(() => {
    try {
      if (!dashboardData.latestScanResults) {
        // Return mock data if no real scan results
        return generateMockData()
      }
      return convertReportToArray(dashboardData.latestScanResults)
    } catch (error) {
      console.error('Error processing visualization data:', error)
      return generateMockData() // Fallback to mock data
    }
  }, [dashboardData.latestScanResults])

  // Apply filters to the data
  const filteredData = useMemo(() => {
    if (!Array.isArray(normalizedData)) {
      return []
    }
    return normalizedData.filter(item => {
      if (!item) return false // Safety check
      if (filters.regulation !== 'all' && !item.regulations?.includes(filters.regulation)) {
        return false
      }
      if (filters.classification !== 'all' && item.classification !== filters.classification) {
        return false
      }
      if (item.risk_score < filters.minRisk) {
        return false
      }
      if (filters.search && !item.table?.toLowerCase().includes(filters.search.toLowerCase()) && 
          !item.column?.toLowerCase().includes(filters.search.toLowerCase())) {
        return false
      }
      return true
    })
  }, [normalizedData, filters])

  // Statistics for display
  const stats = useMemo(() => {
    if (!Array.isArray(filteredData)) {
      return {
        totalFields: 0,
        sensitiveFields: 0,
        highRiskFields: 0,
        regulations: 0,
        avgRisk: 0
      }
    }
    
    const totalFields = filteredData.length
    const sensitiveFields = filteredData.filter(item => 
      item && item.classification !== 'Unknown' && item.classification !== 'NON_SENSITIVE'
    ).length
    const highRiskFields = filteredData.filter(item => item && item.risk_score >= 70).length
    const regulations = [...new Set(filteredData.flatMap(item => item?.regulations || []))]
    
    return {
      totalFields,
      sensitiveFields,
      highRiskFields,
      regulations: regulations.length,
      avgRisk: totalFields > 0 ? Math.round(filteredData.reduce((sum, item) => sum + (item?.risk_score || 0), 0) / totalFields) : 0
    }
  }, [filteredData])

  // Tab navigation
  const tabs = [
    { id: 'overview', label: 'System Overview', icon: Activity },
    { id: 'visualizer', label: 'Schema Visualizer', icon: BarChart3 },
  ]

  // Visualization components map (reduced set)
  const visualizations = {
    heatmap: {
      component: TableHeatmap,
      title: 'Table Heatmap',
      icon: Grid,
      description: 'View exposure per table'
    },
    treemap: {
      component: TreemapVisualization,
      title: 'Treemap Analysis',
      icon: BarChart3,
      description: 'Grouped exposure analysis'
    },
    scatter: {
      component: ScatterQuadrant,
      title: 'Priority Quadrant',
      icon: Target,
      description: 'Risk vs exposure scatter'
    },
    list: {
      component: FindingsList,
      title: 'Findings List',
      icon: List,
      description: 'Detailed tabular view'
    },
    top_risk: {
      component: TopRiskyColumns,
      title: 'Top Risk Columns',
      icon: AlertTriangle,
      description: 'Highest risk fields'
    },
    regulations: {
      component: RegulationPieChart,
      title: 'Regulation Distribution',
      icon: PieChart,
      description: 'Compliance breakdown'
    }
  }

  const ActiveVisualization = visualizations[activeView]?.component || TableHeatmap

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* System Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Scans</p>
              <p className="text-2xl font-bold text-gray-900">{dashboardData.systemStats.totalScans}</p>
            </div>
            <Database className="w-8 h-8 text-blue-500" />
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Sensitive Fields</p>
              <p className="text-2xl font-bold text-orange-600">{dashboardData.systemStats.sensitiveFieldsFound}</p>
            </div>
            <Shield className="w-8 h-8 text-orange-500" />
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Violations</p>
              <p className="text-2xl font-bold text-red-600">{dashboardData.systemStats.complianceViolations}</p>
            </div>
            <AlertTriangle className="w-8 h-8 text-red-500" />
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white p-6 rounded-lg shadow-sm border border-gray-200"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Processing</p>
              <p className="text-2xl font-bold text-green-600">{dashboardData.systemStats.avgProcessingTime}</p>
            </div>
            <Clock className="w-8 h-8 text-green-500" />
          </div>
        </motion.div>
      </div>

      {/* Recent Scans */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Scans</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">PII Fields</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Level</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {dashboardData.recentScans.map((scan) => (
                <tr key={scan.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {scan.fileName}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {scan.scanDate}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                      {scan.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {scan.piiFields}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      scan.riskLevel === 'HIGH' ? 'bg-red-100 text-red-800' :
                      scan.riskLevel === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {scan.riskLevel}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )

  const renderVisualizerTab = () => (
    <div className="space-y-6">
      {/* Statistics Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-semibold text-gray-900">Sensitive Schema Analysis</h3>
            <p className="text-sm text-gray-600 mt-1">Interactive analysis of sensitive fields across database schema</p>
          </div>
          <button
            onClick={() => setShowExportPlan(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export Plan</span>
          </button>
        </div>
        
        {/* Key Statistics */}
        <div className="grid grid-cols-5 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900">{stats.totalFields}</div>
            <div className="text-sm text-gray-600">Total Fields</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-red-600">{stats.sensitiveFields}</div>
            <div className="text-sm text-gray-600">Sensitive</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">{stats.highRiskFields}</div>
            <div className="text-sm text-gray-600">High Risk</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">{stats.regulations}</div>
            <div className="text-sm text-gray-600">Regulations</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{stats.avgRisk}</div>
            <div className="text-sm text-gray-600">Avg Risk</div>
          </div>
        </div>
      </div>

      {/* Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Visualization Navigation */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h4 className="font-medium text-gray-900 mb-4">Visualizations</h4>
          <div className="space-y-2">
            {Object.entries(visualizations).map(([key, viz]) => (
              <button
                key={key}
                onClick={() => setActiveView(key)}
                className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
                  activeView === key
                    ? 'bg-blue-50 text-blue-700 border border-blue-200'
                    : 'hover:bg-gray-50 text-gray-700'
                }`}
              >
                <viz.icon className="w-4 h-4" />
                <div>
                  <div className="text-sm font-medium">{viz.title}</div>
                  <div className="text-xs text-gray-500">{viz.description}</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Active Visualization */}
        <div className="lg:col-span-3 bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <h4 className="font-medium text-gray-900">{visualizations[activeView]?.title}</h4>
            <p className="text-sm text-gray-600">{visualizations[activeView]?.description}</p>
          </div>
          <div className="p-6">
            {filteredData && filteredData.length > 0 ? (
              <ActiveVisualization 
                data={filteredData}
                aggregatedData={aggregateByTable(filteredData)}
                onFilterChange={setFilters}
              />
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-500 text-lg mb-2">No Data Available</div>
                <div className="text-gray-400 text-sm">
                  Complete a PII scan to view visualizations
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <RefreshCw className="w-6 h-6 text-blue-600 animate-spin" />
          <span className="text-gray-600">Loading dashboard...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
              <p className="text-sm text-gray-600">Monitor system performance and analyze scan results</p>
            </div>
            
            {/* Tab Navigation */}
            <div className="flex space-x-4">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-blue-100 text-blue-700 border border-blue-200'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.2 }}
          >
            {activeTab === 'overview' && renderOverviewTab()}
            {activeTab === 'visualizer' && renderVisualizerTab()}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Export Plan Modal */}
      <AnimatePresence>
        {showExportPlan && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50 p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-auto"
            >
              <MaskingPlanExport 
                data={filteredData}
                onClose={() => setShowExportPlan(false)}
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default Dashboard