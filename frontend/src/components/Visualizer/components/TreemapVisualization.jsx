/**
 * Treemap Visualization Component
 * ==============================
 * 
 * Shows exposure aggregated by grouping dimensions
 * (classification, owner, regulation, table) using size and color
 * 
 * @author PII Scanner Team
 * @version 1.0.0
 */

import React, { useState, useMemo } from 'react'
import { Treemap, ResponsiveContainer, Tooltip } from 'recharts'
import { motion } from 'framer-motion'
import { BarChart3, Users, Shield, Database } from 'lucide-react'
import { aggregateByClassification, aggregateByOwner, aggregateByRegulation, aggregateByTable } from '../utils/dataProcessor'

const TreemapVisualization = ({ data, onItemSelect, onAddToMaskingPlan }) => {
  const [groupMode, setGroupMode] = useState('classification')
  const [selectedGroup, setSelectedGroup] = useState(null)

  // Aggregate data based on selected grouping mode
  const treemapData = useMemo(() => {
    let aggregatedData = []
    
    switch (groupMode) {
      case 'classification':
        aggregatedData = aggregateByClassification(data)
        break
      case 'owner':
        aggregatedData = aggregateByOwner(data)
        break
      case 'regulation':
        aggregatedData = aggregateByRegulation(data)
        break
      case 'table':
        aggregatedData = aggregateByTable(data)
        break
      default:
        aggregatedData = aggregateByClassification(data)
    }

    // Format for treemap
    return aggregatedData
      .filter(item => item.count > 0)
      .map(item => ({
        name: item[groupMode] || item.name || 'Unknown',
        size: item.exposure || item.count * (item.avg_risk || item.avgRisk || 50),
        count: item.count,
        avgRisk: item.avg_risk || item.avgRisk || 0,
        highRiskCount: item.high_risk_count || item.highRiskCount || 0,
        tables: item.tables || [],
        regulations: item.regulations || [],
        _original: item
      }))
      .sort((a, b) => b.size - a.size)
      .slice(0, 20) // Limit to top 20 for readability
  }, [data, groupMode])

  // Color mapping based on average risk
  const getColor = (avgRisk) => {
    if (avgRisk >= 80) return '#fee2e2' // red-100
    if (avgRisk >= 60) return '#fef3c7' // yellow-100
    if (avgRisk >= 40) return '#dbeafe' // blue-100
    return '#f3f4f6' // gray-100
  }

  const getBorderColor = (avgRisk) => {
    if (avgRisk >= 80) return '#dc2626' // red-600
    if (avgRisk >= 60) return '#d97706' // yellow-600
    if (avgRisk >= 40) return '#2563eb' // blue-600
    return '#6b7280' // gray-500
  }

  // Custom treemap content component with defensive rendering
  const SafeTreemapContent = (props) => {
    // Defensive checks to prevent crashes
    const { payload, x, y, width, height } = props || {}
    
    if (!payload || width < 20 || height < 20) {
      return null
    }

    const { name, count, avgRisk, size } = payload
    const displayName = String(name || 'Unknown')
    const fontSize = Math.max(10, Math.min(14, width / 8, height / 4))
    const showDetails = width > 60 && height > 40

    return (
      <g>
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          fill={getColor(avgRisk || 0)}
          stroke={getBorderColor(avgRisk || 0)}
          strokeWidth={2}
          className="cursor-pointer hover:opacity-80 transition-opacity"
          onClick={() => handleTreemapClick(payload)}
        />
        <text
          x={x + width / 2}
          y={y + height / 2 - (showDetails ? 10 : 0)}
          textAnchor="middle"
          dominantBaseline="middle"
          fontSize={fontSize}
          fontWeight="600"
          fill="#374151"
          className="pointer-events-none"
        >
          {displayName.length > 15 ? displayName.substring(0, 12) + '...' : displayName}
        </text>
        {showDetails && (
          <>
            <text
              x={x + width / 2}
              y={y + height / 2 + 5}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize={fontSize - 2}
              fill="#6b7280"
              className="pointer-events-none"
            >
              {count} fields
            </text>
            <text
              x={x + width / 2}
              y={y + height / 2 + 18}
              textAnchor="middle"
              dominantBaseline="middle"
              fontSize={fontSize - 2}
              fill="#6b7280"
              className="pointer-events-none"
            >
              Risk: {avgRisk || 0}
            </text>
          </>
        )}
      </g>
    )
  }

  const handleTreemapClick = (item) => {
    setSelectedGroup(item)
    if (onItemSelect) {
      onItemSelect(item)
    }
  }

  const handleModeChange = (newMode) => {
    setGroupMode(newMode)
    setSelectedGroup(null)
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg max-w-xs">
          <p className="font-semibold text-gray-900">{data.name}</p>
          <div className="mt-2 space-y-1 text-sm">
            <p className="text-gray-600">Fields: {data.count}</p>
            <p className="text-gray-600">Avg Risk: {data.avgRisk}</p>
            <p className="text-gray-600">Exposure: {Math.round(data.size)}</p>
            {data.highRiskCount > 0 && (
              <p className="text-red-600">High Risk: {data.highRiskCount}</p>
            )}
            {data.tables.length > 0 && (
              <p className="text-gray-600">Tables: {data.tables.length}</p>
            )}
          </div>
        </div>
      )
    }
    return null
  }

  const groupModes = [
    { id: 'classification', label: 'Classification', icon: Shield, description: 'Group by PHI/PII/Other' },
    { id: 'owner', label: 'Owner', icon: Users, description: 'Group by data owner' },
    { id: 'regulation', label: 'Regulation', icon: BarChart3, description: 'Group by compliance regulation' },
    { id: 'table', label: 'Table', icon: Database, description: 'Group by database table' }
  ]

  if (treemapData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No data available for treemap visualization</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header and Mode Selector */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Exposure Treemap</h3>
          <p className="text-sm text-gray-600">
            Size represents exposure (count × risk), color shows average risk level
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          {groupModes.map(mode => {
            const Icon = mode.icon
            return (
              <button
                key={mode.id}
                onClick={() => handleModeChange(mode.id)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                  groupMode === mode.id
                    ? 'bg-blue-100 text-blue-900 border border-blue-200'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
                title={mode.description}
              >
                <Icon className="w-4 h-4" />
                <span>{mode.label}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Treemap */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <Treemap
              data={treemapData}
              dataKey="size"
              aspectRatio={4 / 3}
              stroke="#ffffff"
              strokeWidth={2}
              content={<SafeTreemapContent />}
            >
              <Tooltip content={<CustomTooltip />} />
            </Treemap>
          </ResponsiveContainer>
        </div>
        
        {/* Legend */}
        <div className="mt-4 flex items-center justify-center space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: getColor(20) }}></div>
            <span>Low Risk (0-39)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: getColor(50) }}></div>
            <span>Medium Risk (40-59)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: getColor(70) }}></div>
            <span>High Risk (60-79)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: getColor(90) }}></div>
            <span>Critical Risk (80+)</span>
          </div>
        </div>
      </div>

      {/* Top Groups Summary */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">
          Top {groupMode.charAt(0).toUpperCase() + groupMode.slice(1)} Groups
        </h4>
        <div className="space-y-3">
          {treemapData.slice(0, 5).map((item, index) => (
            <motion.div
              key={item.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
              onClick={() => handleTreemapClick(item)}
            >
              <div className="flex items-center space-x-3">
                <div className="text-lg font-bold text-gray-400">#{index + 1}</div>
                <div>
                  <div className="font-semibold text-gray-900">{item.name}</div>
                  <div className="text-sm text-gray-600">
                    {item.count} fields • Avg Risk: {item.avgRisk}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="text-xl font-bold text-gray-900">{Math.round(item.size)}</div>
                  <div className="text-xs text-gray-500">Exposure</div>
                </div>
                {item.highRiskCount > 0 && (
                  <div className="text-right">
                    <div className="text-lg font-bold text-red-600">{item.highRiskCount}</div>
                    <div className="text-xs text-gray-500">High Risk</div>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Group Detail Modal */}
      {selectedGroup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{selectedGroup.name}</h3>
                  <p className="text-gray-600">{groupMode.charAt(0).toUpperCase() + groupMode.slice(1)} Group Details</p>
                </div>
                <button
                  onClick={() => setSelectedGroup(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="p-6">
              {/* Group Summary */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{selectedGroup.count}</div>
                  <div className="text-sm text-blue-700">Total Fields</div>
                </div>
                <div className="text-center p-3 bg-yellow-50 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">{selectedGroup.avgRisk}</div>
                  <div className="text-sm text-yellow-700">Avg Risk</div>
                </div>
                <div className="text-center p-3 bg-red-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">{selectedGroup.highRiskCount}</div>
                  <div className="text-sm text-red-700">High Risk</div>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{Math.round(selectedGroup.size)}</div>
                  <div className="text-sm text-purple-700">Exposure</div>
                </div>
              </div>

              {/* Related Tables/Data */}
              {selectedGroup.tables && selectedGroup.tables.length > 0 && (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-gray-900 mb-3">Related Tables</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedGroup.tables.map(table => (
                      <span key={table} className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">
                        {table}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-between items-center">
                <div className="text-sm text-gray-600">
                  {selectedGroup.regulations && selectedGroup.regulations.length > 0 && (
                    <>Regulations: {selectedGroup.regulations.join(', ')}</>
                  )}
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={() => {
                      // Add all fields from this group to masking plan
                      const groupFields = data.filter(field => {
                        switch (groupMode) {
                          case 'classification':
                            return field.classification === selectedGroup.name
                          case 'owner':
                            return field.owner === selectedGroup.name
                          case 'regulation':
                            return field.regulations.includes(selectedGroup.name)
                          case 'table':
                            return field.table === selectedGroup.name
                          default:
                            return false
                        }
                      })
                      if (onAddToMaskingPlan) {
                        onAddToMaskingPlan(groupFields)
                      }
                      setSelectedGroup(null)
                    }}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  >
                    Add Group to Masking Plan
                  </button>
                  <button
                    onClick={() => setSelectedGroup(null)}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TreemapVisualization