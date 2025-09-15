/**
 * Table Heatmap Visualization Component
 * ===================================
 * 
 * Shows table-level exposure as a grid of cards (heatmap-like)
 * Color-coded by risk level, sized by field count
 * 
 * @author PII Scanner Team
 * @version 1.0.0
 */

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Eye, Shield, AlertTriangle, Database, Users } from 'lucide-react'

const TableHeatmap = ({ data, aggregatedData, onItemSelect, onAddToMaskingPlan }) => {
  const [selectedTable, setSelectedTable] = useState(null)
  const [hoveredTable, setHoveredTable] = useState(null)

  const tables = aggregatedData.tables || []

  // Color mapping for risk levels
  const getRiskColor = (avgRisk) => {
    if (avgRisk >= 80) return 'from-red-100 to-red-200 border-red-300 text-red-900'
    if (avgRisk >= 60) return 'from-orange-100 to-orange-200 border-orange-300 text-orange-900'
    if (avgRisk >= 40) return 'from-yellow-100 to-yellow-200 border-yellow-300 text-yellow-900'
    if (avgRisk >= 20) return 'from-blue-100 to-blue-200 border-blue-300 text-blue-900'
    return 'from-gray-100 to-gray-200 border-gray-300 text-gray-900'
  }

  const handleTableClick = (table) => {
    setSelectedTable(table)
    if (onItemSelect) {
      onItemSelect(table)
    }
  }

  const handleAddToMaskingPlan = (table) => {
    if (onAddToMaskingPlan) {
      // Add all sensitive fields from this table to masking plan
      const tableFields = data.filter(field => 
        field.table === table.table && field.classification !== 'Unknown'
      )
      onAddToMaskingPlan(tableFields)
    }
  }

  if (tables.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <Database className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No table data available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Table-level Risk Exposure</h3>
          <p className="text-sm text-gray-600">
            Each card represents a table. Color indicates average risk, size shows field count.
          </p>
        </div>
        {aggregatedData.samplingActive && (
          <div className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">
            Showing top 50 of {aggregatedData.totalTables} tables
          </div>
        )}
      </div>

      {/* Heatmap Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {tables.map((table, index) => (
          <motion.div
            key={table.table}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className={`
              relative p-4 rounded-lg border-2 cursor-pointer transition-all duration-200
              bg-gradient-to-br ${getRiskColor(table.avg_risk)}
              hover:shadow-lg hover:scale-105
              ${selectedTable?.table === table.table ? 'ring-2 ring-blue-500 ring-offset-2' : ''}
            `}
            onClick={() => handleTableClick(table)}
            onMouseEnter={() => setHoveredTable(table)}
            onMouseLeave={() => setHoveredTable(null)}
          >
            {/* Risk Level Badge */}
            <div className="absolute top-2 right-2">
              {table.avg_risk >= 70 ? (
                <AlertTriangle className="w-4 h-4 text-red-600" />
              ) : table.avg_risk >= 40 ? (
                <Shield className="w-4 h-4 text-yellow-600" />
              ) : (
                <Shield className="w-4 h-4 text-green-600" />
              )}
            </div>

            {/* Table Name */}
            <div className="mb-3">
              <h4 className="font-semibold text-sm truncate" title={table.table}>
                {table.table}
              </h4>
            </div>

            {/* Metrics */}
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="opacity-75">Fields:</span>
                <span className="font-medium">{table.total_fields}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="opacity-75">Sensitive:</span>
                <span className="font-medium text-red-700">{table.sensitive_fields}</span>
              </div>
              
              <div className="flex justify-between">
                <span className="opacity-75">Avg Risk:</span>
                <span className="font-bold">{table.avg_risk}</span>
              </div>
              
              {table.regulations.length > 0 && (
                <div className="flex justify-between">
                  <span className="opacity-75">Regs:</span>
                  <span className="font-medium text-xs">
                    {table.regulations.join(', ')}
                  </span>
                </div>
              )}
            </div>

            {/* Exposure Bar */}
            <div className="mt-3 h-1 bg-black bg-opacity-10 rounded-full overflow-hidden">
              <div 
                className="h-full bg-current opacity-60"
                style={{ 
                  width: `${Math.min(100, (table.exposure / Math.max(...tables.map(t => t.exposure))) * 100)}%` 
                }}
              />
            </div>
          </motion.div>
        ))}
      </div>

      {/* Tooltip */}
      {hoveredTable && (
        <div className="fixed z-50 p-3 bg-gray-900 text-white text-sm rounded-lg shadow-lg pointer-events-none"
             style={{ 
               left: '50%', 
               top: '20%',
               transform: 'translateX(-50%)'
             }}>
          <div className="font-semibold mb-2">{hoveredTable.table}</div>
          <div className="space-y-1">
            <div>Total Fields: {hoveredTable.total_fields}</div>
            <div>Sensitive Fields: {hoveredTable.sensitive_fields}</div>
            <div>Average Risk: {hoveredTable.avg_risk}/100</div>
            <div>Exposure Score: {hoveredTable.exposure}</div>
            {hoveredTable.top_columns.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="font-medium mb-1">Top Risk Columns:</div>
                {hoveredTable.top_columns.slice(0, 3).map(col => (
                  <div key={col.column} className="text-xs">
                    {col.column} ({col.risk_score})
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Table Detail Modal */}
      {selectedTable && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-bold text-gray-900">{selectedTable.table}</h3>
                  <p className="text-gray-600">Table Details & Column Analysis</p>
                </div>
                <button
                  onClick={() => setSelectedTable(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
            </div>

            <div className="p-6">
              {/* Table Summary */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{selectedTable.total_fields}</div>
                  <div className="text-sm text-blue-700">Total Fields</div>
                </div>
                <div className="text-center p-3 bg-red-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">{selectedTable.sensitive_fields}</div>
                  <div className="text-sm text-red-700">Sensitive</div>
                </div>
                <div className="text-center p-3 bg-yellow-50 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">{selectedTable.avg_risk}</div>
                  <div className="text-sm text-yellow-700">Avg Risk</div>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{selectedTable.exposure}</div>
                  <div className="text-sm text-purple-700">Exposure</div>
                </div>
              </div>

              {/* Column List */}
              <div className="mb-6">
                <h4 className="text-lg font-semibold text-gray-900 mb-3">Column Details</h4>
                <div className="bg-gray-50 rounded-lg overflow-hidden">
                  <div className="grid grid-cols-4 gap-4 p-3 bg-gray-100 font-medium text-sm text-gray-700">
                    <div>Column</div>
                    <div>Classification</div>
                    <div>Risk Score</div>
                    <div>Regulations</div>
                  </div>
                  {data
                    .filter(field => field.table === selectedTable.table)
                    .sort((a, b) => b.risk_score - a.risk_score)
                    .map((field, index) => (
                      <div key={index} className="grid grid-cols-4 gap-4 p-3 border-t border-gray-200 text-sm">
                        <div className="font-mono font-medium">{field.column}</div>
                        <div>
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            field.classification === 'PHI' ? 'bg-red-100 text-red-800' :
                            field.classification === 'PII' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {field.classification}
                          </span>
                        </div>
                        <div className="font-medium">{field.risk_score}</div>
                        <div className="text-xs">{field.regulations.join(', ')}</div>
                      </div>
                    ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-between items-center">
                <div className="text-sm text-gray-600">
                  {selectedTable.regulations.length > 0 && (
                    <>Regulations: {selectedTable.regulations.join(', ')}</>
                  )}
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={() => handleAddToMaskingPlan(selectedTable)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  >
                    Add to Masking Plan
                  </button>
                  <button
                    onClick={() => setSelectedTable(null)}
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

export default TableHeatmap