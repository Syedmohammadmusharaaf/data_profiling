/**
 * Schema Visualizer Dashboard - Main Component
 * ============================================
 * 
 * Interactive dashboard for visualizing sensitive data findings from PII Scanner
 * Supports multiple visualization types: heatmaps, treemaps, scatter plots, etc.
 * 
 * @author PII Scanner Team
 * @version 1.0.0
 */

import React, { useState, useEffect, useMemo } from 'react'
import { motion } from 'framer-motion'
import { 
  BarChart3, 
  Grid, 
  PieChart, 
  Target,
  List,
  Download,
  Filter,
  Search,
  Settings,
  Eye,
  AlertTriangle,
  Shield,
  FileText,
  Users,
  X
} from 'lucide-react'
import toast from 'react-hot-toast'

// Import visualization components
import TableHeatmap from './components/TableHeatmap'
import TreemapVisualization from './components/TreemapVisualization'
import ScatterQuadrant from './components/ScatterQuadrant'
import FindingsList from './components/FindingsList'
import TopRiskyColumns from './components/TopRiskyColumns'
import RegulationPieChart from './components/RegulationPieChart'
import SankeyFlow from './components/SankeyFlow'
import MaskingPlanExport from './components/MaskingPlanExport'

// Import utilities
import { convertReportToArray, aggregateByTable, aggregateByRegulation } from './utils/dataProcessor'
import { downloadCSV, downloadSQL } from './utils/exportUtils'

const SchemaVisualizer = ({ reportData, onClose }) => {
  // State management
  const [activeView, setActiveView] = useState('heatmap')
  const [filters, setFilters] = useState({
    regulation: 'all',
    classification: 'all',
    minRisk: 0,
    search: ''
  })
  const [selectedItems, setSelectedItems] = useState([])
  const [maskingPlan, setMaskingPlan] = useState([])
  const [showFilters, setShowFilters] = useState(false)
  const [samplingMode, setSamplingMode] = useState(false)

  // Process and normalize the scanner data
  const normalizedData = useMemo(() => {
    console.log('🔍 DEBUG SchemaVisualizer: Processing reportData:', reportData)
    console.log('🔍 DEBUG SchemaVisualizer: reportData keys:', Object.keys(reportData || {}))
    
    if (!reportData) {
      console.log('❌ DEBUG SchemaVisualizer: No reportData provided')
      return []
    }
    
    const converted = convertReportToArray(reportData)
    console.log('🔍 DEBUG SchemaVisualizer: Converted data:', converted)
    console.log('🔍 DEBUG SchemaVisualizer: Converted data length:', converted.length)
    
    return converted
  }, [reportData])

  // Apply filters
  const filteredData = useMemo(() => {
    return normalizedData.filter(item => {
      if (filters.regulation !== 'all' && !item.regulations.includes(filters.regulation)) {
        return false
      }
      if (filters.classification !== 'all' && item.classification !== filters.classification) {
        return false
      }
      if (item.risk_score < filters.minRisk) {
        return false
      }
      if (filters.search && !item.table.toLowerCase().includes(filters.search.toLowerCase()) && 
          !item.column.toLowerCase().includes(filters.search.toLowerCase())) {
        return false
      }
      return true
    })
  }, [normalizedData, filters])

  // Aggregate data for visualizations
  const aggregatedData = useMemo(() => {
    const tableAgg = aggregateByTable(filteredData)
    const regulationAgg = aggregateByRegulation(filteredData)
    
    // Enable sampling for large datasets
    const shouldSample = tableAgg.length > 500
    setSamplingMode(shouldSample)
    
    return {
      tables: shouldSample ? tableAgg.slice(0, 50) : tableAgg,
      regulations: regulationAgg,
      totalTables: tableAgg.length,
      samplingActive: shouldSample
    }
  }, [filteredData])

  // Statistics
  const stats = useMemo(() => {
    const totalFields = filteredData.length
    const sensitiveFields = filteredData.filter(item => item.classification !== 'Unknown').length
    const highRiskFields = filteredData.filter(item => item.risk_score >= 70).length
    const regulations = [...new Set(filteredData.flatMap(item => item.regulations))]
    
    return {
      totalFields,
      sensitiveFields,
      highRiskFields,
      regulations: regulations.length,
      avgRisk: totalFields > 0 ? Math.round(filteredData.reduce((sum, item) => sum + item.risk_score, 0) / totalFields) : 0
    }
  }, [filteredData])

  // Visualization components map
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
    },
    sankey: {
      component: SankeyFlow,
      title: 'Data Flow Analysis',
      icon: BarChart3,
      description: 'Column → Table → Owner'
    }
  }

  const ActiveVisualization = visualizations[activeView]?.component || TableHeatmap

  return (
    <div className="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full h-full max-w-7xl max-h-[95vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Sensitive Schema Visualizer</h2>
            <p className="text-gray-600 mt-1">
              Interactive analysis of {stats.totalFields} fields across {aggregatedData.totalTables} tables
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`p-2 rounded-lg transition-colors ${showFilters ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
            >
              <Filter className="w-5 h-5" />
            </button>
            <button
              onClick={onClose}
              className="p-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Stats Bar */}
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-8">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{stats.totalFields}</div>
                <div className="text-xs text-gray-600">Total Fields</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{stats.sensitiveFields}</div>
                <div className="text-xs text-gray-600">Sensitive</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{stats.highRiskFields}</div>
                <div className="text-xs text-gray-600">High Risk</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{stats.regulations}</div>
                <div className="text-xs text-gray-600">Regulations</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-600">{stats.avgRisk}</div>
                <div className="text-xs text-gray-600">Avg Risk</div>
              </div>
            </div>
            
            {samplingMode && (
              <div className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">
                Sampling Mode: Showing top 50 of {aggregatedData.totalTables} tables
              </div>
            )}
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <motion.div
            className="px-6 py-4 bg-blue-50 border-b border-blue-200"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-blue-900 mb-1">Regulation</label>
                <select
                  value={filters.regulation}
                  onChange={(e) => setFilters(f => ({ ...f, regulation: e.target.value }))}
                  className="w-full p-2 border border-blue-200 rounded-lg text-sm"
                >
                  <option value="all">All Regulations</option>
                  <option value="HIPAA">HIPAA</option>
                  <option value="GDPR">GDPR</option>
                  <option value="CCPA">CCPA</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-blue-900 mb-1">Classification</label>
                <select
                  value={filters.classification}
                  onChange={(e) => setFilters(f => ({ ...f, classification: e.target.value }))}
                  className="w-full p-2 border border-blue-200 rounded-lg text-sm"
                >
                  <option value="all">All Classifications</option>
                  <option value="PHI">PHI</option>
                  <option value="PII">PII</option>
                  <option value="Unknown">Non-sensitive</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-blue-900 mb-1">Min Risk Score</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={filters.minRisk}
                  onChange={(e) => setFilters(f => ({ ...f, minRisk: parseInt(e.target.value) }))}
                  className="w-full"
                />
                <div className="text-xs text-blue-700 mt-1">{filters.minRisk}+</div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-blue-900 mb-1">Search</label>
                <input
                  type="text"
                  value={filters.search}
                  onChange={(e) => setFilters(f => ({ ...f, search: e.target.value }))}
                  placeholder="Table or column name..."
                  className="w-full p-2 border border-blue-200 rounded-lg text-sm"
                />
              </div>
            </div>
          </motion.div>
        )}

        {/* Main Content */}
        <div className="flex-1 flex min-h-0">
          {/* Sidebar - Visualization Selector */}
          <div className="w-64 bg-gray-50 border-r border-gray-200 p-4 overflow-y-auto">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Visualizations</h3>
            <div className="space-y-2">
              {Object.entries(visualizations).map(([key, viz]) => {
                const Icon = viz.icon
                return (
                  <button
                    key={key}
                    onClick={() => setActiveView(key)}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      activeView === key 
                        ? 'bg-blue-100 text-blue-900 border border-blue-200' 
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <Icon className="w-4 h-4" />
                      <div>
                        <div className="font-medium text-sm">{viz.title}</div>
                        <div className="text-xs text-gray-500">{viz.description}</div>
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>

            {/* Masking Plan Summary */}
            {maskingPlan.length > 0 && (
              <div className="mt-6 p-3 bg-green-50 border border-green-200 rounded-lg">
                <h4 className="text-sm font-semibold text-green-900 mb-2">Masking Plan</h4>
                <div className="text-sm text-green-700">
                  {maskingPlan.length} items selected
                </div>
                <button
                  onClick={() => {/* Open masking plan export */}}
                  className="mt-2 w-full bg-green-600 text-white text-sm py-1 px-2 rounded hover:bg-green-700 transition-colors"
                >
                  Export Plan
                </button>
              </div>
            )}
          </div>

          {/* Main Visualization Area */}
          <div className="flex-1 p-6 overflow-auto">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                {visualizations[activeView]?.title}
              </h3>
              <p className="text-gray-600 text-sm">
                {visualizations[activeView]?.description}
              </p>
            </div>

            <div className="h-full">
              <ActiveVisualization
                data={filteredData}
                aggregatedData={aggregatedData}
                onItemSelect={(item) => {
                  setSelectedItems(prev => [...prev, item])
                }}
                onAddToMaskingPlan={(items) => {
                  setMaskingPlan(prev => [...prev, ...items])
                  toast.success(`Added ${items.length} items to masking plan`)
                }}
                selectedItems={selectedItems}
              />
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Analyzing {reportData?.file_info?.name || 'uploaded schema'} • 
              Generated {reportData?.generated_at ? new Date(reportData.generated_at).toLocaleString() : 'now'}
            </div>
            <div className="flex space-x-3">
              <MaskingPlanExport
                plan={maskingPlan}
                onExport={(format) => {
                  toast.success(`Masking plan exported as ${format.toUpperCase()}`)
                }}
              />
              <button
                onClick={onClose}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SchemaVisualizer