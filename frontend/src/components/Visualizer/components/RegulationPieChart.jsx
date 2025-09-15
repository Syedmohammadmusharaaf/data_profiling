/**
 * Regulation Distribution Pie Chart Component
 * ==========================================
 * 
 * Shows the distribution of findings across different regulations
 * Allows filtering of the entire dashboard by regulation
 * 
 * @author PII Scanner Team
 * @version 1.0.0
 */

import React, { useMemo } from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { Shield, AlertTriangle, FileText, Filter } from 'lucide-react'
import { motion } from 'framer-motion'

const RegulationPieChart = ({ data, onFilterChange }) => {
  // Process data for pie chart
  const chartData = useMemo(() => {
    const regulationCounts = {}
    const regulationRisks = {}
    
    data.forEach(field => {
      if (field.regulations && field.regulations.length > 0) {
        field.regulations.forEach(regulation => {
          if (!regulationCounts[regulation]) {
            regulationCounts[regulation] = 0
            regulationRisks[regulation] = []
          }
          regulationCounts[regulation]++
          regulationRisks[regulation].push(field.risk_score)
        })
      } else if (field.classification !== 'Unknown') {
        // Handle fields with no specific regulation but are classified as sensitive
        const regulation = 'Other'
        if (!regulationCounts[regulation]) {
          regulationCounts[regulation] = 0
          regulationRisks[regulation] = []
        }
        regulationCounts[regulation]++
        regulationRisks[regulation].push(field.risk_score)
      }
    })

    // Convert to chart format with colors and additional metrics
    const colors = {
      'HIPAA': '#ef4444', // red
      'GDPR': '#3b82f6',  // blue
      'CCPA': '#10b981',  // green
      'PCI-DSS': '#f59e0b', // yellow
      'SOX': '#8b5cf6',   // purple
      'Other': '#6b7280'  // gray
    }

    return Object.entries(regulationCounts).map(([regulation, count]) => {
      const risks = regulationRisks[regulation]
      const avgRisk = risks.length > 0 ? Math.round(risks.reduce((sum, risk) => sum + risk, 0) / risks.length) : 0
      const highRiskCount = risks.filter(risk => risk >= 70).length
      
      return {
        name: regulation,
        value: count,
        avgRisk,
        highRiskCount,
        color: colors[regulation] || '#6b7280',
        percentage: 0 // Will be calculated after sorting
      }
    }).sort((a, b) => b.value - a.value)
  }, [data])

  // Calculate percentages
  const total = chartData.reduce((sum, item) => sum + item.value, 0)
  chartData.forEach(item => {
    item.percentage = total > 0 ? Math.round((item.value / total) * 100) : 0
  })

  const handleSliceClick = (data) => {
    if (onFilterChange) {
      onFilterChange({ regulation: data.name })
    }
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold text-gray-900">{data.name}</p>
          <p className="text-sm text-gray-600">Fields: {data.value}</p>
          <p className="text-sm text-gray-600">Percentage: {data.percentage}%</p>
          <p className="text-sm text-gray-600">Avg Risk: {data.avgRisk}</p>
          <p className="text-sm text-gray-600">High Risk: {data.highRiskCount}</p>
        </div>
      )
    }
    return null
  }

  const CustomLegend = ({ payload }) => (
    <div className="mt-4 space-y-2">
      {payload.map((entry, index) => (
        <motion.div
          key={`legend-${index}`}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
          className="flex items-center justify-between p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
          onClick={() => handleSliceClick(entry.payload)}
        >
          <div className="flex items-center space-x-3">
            <div 
              className="w-4 h-4 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="font-medium text-gray-900">{entry.payload.name}</span>
          </div>
          
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <div className="text-center">
              <div className="font-semibold text-gray-900">{entry.payload.value}</div>
              <div className="text-xs">Fields</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-gray-900">{entry.payload.percentage}%</div>
              <div className="text-xs">Share</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-gray-900">{entry.payload.avgRisk}</div>
              <div className="text-xs">Avg Risk</div>
            </div>
            <div className="text-center">
              <div className="font-semibold text-orange-600">{entry.payload.highRiskCount}</div>
              <div className="text-xs">High Risk</div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  )

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No regulation data available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Regulation Distribution</h3>
          <p className="text-sm text-gray-600">
            Click on segments to filter the dashboard by regulation
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{total}</div>
            <div className="text-xs text-gray-600">Total Fields</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{chartData.length}</div>
            <div className="text-xs text-gray-600">Regulations</div>
          </div>
        </div>
      </div>

      {/* Pie Chart */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                innerRadius={40}
                paddingAngle={2}
                dataKey="value"
                onClick={handleSliceClick}
                className="cursor-pointer"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Center Label */}
        <div className="relative -mt-32 flex items-center justify-center pointer-events-none">
          <div className="text-center">
            <div className="text-3xl font-bold text-gray-900">{total}</div>
            <div className="text-sm text-gray-600">Total Fields</div>
          </div>
        </div>
      </div>

      {/* Custom Legend with Detailed Info */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Regulation Breakdown</h4>
        <CustomLegend payload={chartData.map(item => ({ ...item, color: item.color, payload: item }))} />
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <h5 className="font-semibold text-red-900">High Risk Fields</h5>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-red-600">
              {chartData.reduce((sum, item) => sum + item.highRiskCount, 0)}
            </div>
            <div className="text-sm text-red-700">
              Across {chartData.length} regulations
            </div>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <Shield className="w-5 h-5 text-blue-600" />
            <h5 className="font-semibold text-blue-900">Most Common</h5>
          </div>
          <div className="mt-2">
            <div className="text-lg font-bold text-blue-600">
              {chartData[0]?.name || 'N/A'}
            </div>
            <div className="text-sm text-blue-700">
              {chartData[0]?.value || 0} fields ({chartData[0]?.percentage || 0}%)
            </div>
          </div>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-green-600" />
            <h5 className="font-semibold text-green-900">Average Risk</h5>
          </div>
          <div className="mt-2">
            <div className="text-2xl font-bold text-green-600">
              {chartData.length > 0 ? Math.round(chartData.reduce((sum, item) => sum + item.avgRisk, 0) / chartData.length) : 0}
            </div>
            <div className="text-sm text-green-700">
              Across all regulations
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h5 className="font-medium text-gray-900 mb-3">Quick Filters</h5>
        <div className="flex flex-wrap gap-2">
          {chartData.map(regulation => (
            <button
              key={regulation.name}
              onClick={() => handleSliceClick(regulation)}
              className="flex items-center space-x-2 px-3 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm"
            >
              <div 
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: regulation.color }}
              />
              <span>{regulation.name}</span>
              <span className="text-gray-500">({regulation.value})</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default RegulationPieChart