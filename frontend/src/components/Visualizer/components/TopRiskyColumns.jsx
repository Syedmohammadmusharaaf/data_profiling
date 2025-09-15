/**
 * Top Risky Columns Component
 * ==========================
 * 
 * Shows the highest risk individual columns across all tables
 * Quick access to the most critical fields that need attention
 * 
 * @author PII Scanner Team
 * @version 1.0.0
 */

import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, Shield, Copy, Eye, Plus, ExternalLink } from 'lucide-react'
import toast from 'react-hot-toast'
import { generateMaskingSQL } from '../utils/dataProcessor'

const TopRiskyColumns = ({ data, onItemSelect, onAddToMaskingPlan }) => {
  const [selectedTemplate, setSelectedTemplate] = useState('redact')
  const [expandedColumn, setExpandedColumn] = useState(null)

  // Get top risky columns
  const topColumns = data
    .filter(field => field.classification !== 'Unknown')
    .sort((a, b) => b.risk_score - a.risk_score)
    .slice(0, 20)

  const getRiskIcon = (riskScore) => {
    if (riskScore >= 80) return <AlertTriangle className="w-4 h-4 text-red-500" />
    if (riskScore >= 60) return <AlertTriangle className="w-4 h-4 text-orange-500" />
    return <Shield className="w-4 h-4 text-yellow-500" />
  }

  const getRiskColor = (riskScore) => {
    if (riskScore >= 80) return 'border-l-red-500 bg-red-50'
    if (riskScore >= 60) return 'border-l-orange-500 bg-orange-50'
    if (riskScore >= 40) return 'border-l-yellow-500 bg-yellow-50'
    return 'border-l-gray-500 bg-gray-50'
  }

  const copyFieldName = (field) => {
    const fieldName = `${field.table}.${field.column}`
    navigator.clipboard.writeText(fieldName)
    toast.success('Field name copied to clipboard')
  }

  const copyMaskingSQL = (field) => {
    const sql = generateMaskingSQL(field, selectedTemplate)
    navigator.clipboard.writeText(sql)
    toast.success('Masking SQL copied to clipboard')
  }

  const handleAddToMaskingPlan = (field) => {
    if (onAddToMaskingPlan) {
      onAddToMaskingPlan([field])
      toast.success(`Added ${field.table}.${field.column} to masking plan`)
    }
  }

  const handleJumpToTable = (field) => {
    if (onItemSelect) {
      onItemSelect(field)
    }
    toast.info(`Navigating to ${field.table} table view`)
  }

  if (topColumns.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <Shield className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No high-risk columns found</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Top Risk Columns</h3>
          <p className="text-sm text-gray-600">
            Highest risk individual columns requiring immediate attention
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Masking Template:</label>
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded text-sm"
            >
              <option value="redact">Redact</option>
              <option value="nullify">Nullify</option>
              <option value="hash">Hash</option>
              <option value="truncate">Truncate</option>
              <option value="tokenize">Tokenize</option>
            </select>
          </div>
        </div>
      </div>

      {/* Top Columns List */}
      <div className="space-y-3">
        {topColumns.map((field, index) => (
          <motion.div
            key={`${field.table}.${field.column}`}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className={`border-l-4 bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200 ${getRiskColor(field.risk_score)}`}
          >
            <div className="flex items-center justify-between">
              {/* Column Info */}
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                    {getRiskIcon(field.risk_score)}
                  </div>
                  
                  <div>
                    <div className="font-mono font-semibold text-gray-900">
                      {field.table}.{field.column}
                    </div>
                    <div className="flex items-center space-x-3 mt-1">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        field.classification === 'PHI' ? 'bg-red-100 text-red-800' :
                        field.classification === 'PII' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {field.classification}
                      </span>
                      <span className="text-sm text-gray-600">{field.data_type}</span>
                      {field.regulations.length > 0 && (
                        <div className="flex space-x-1">
                          {field.regulations.map(reg => (
                            <span key={reg} className="px-1 py-0.5 bg-blue-100 text-blue-800 text-xs rounded">
                              {reg}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Risk Score */}
              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <div className="text-2xl font-bold text-gray-900">{field.risk_score}</div>
                  <div className="text-xs text-gray-500">Risk Score</div>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => copyFieldName(field)}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
                    title="Copy field name"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  
                  <button
                    onClick={() => copyMaskingSQL(field)}
                    className="p-2 text-blue-400 hover:text-blue-600 hover:bg-blue-100 rounded transition-colors"
                    title="Copy masking SQL"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  
                  <button
                    onClick={() => handleJumpToTable(field)}
                    className="p-2 text-green-400 hover:text-green-600 hover:bg-green-100 rounded transition-colors"
                    title="Jump to table view"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </button>
                  
                  <button
                    onClick={() => handleAddToMaskingPlan(field)}
                    className="p-2 text-purple-400 hover:text-purple-600 hover:bg-purple-100 rounded transition-colors"
                    title="Add to masking plan"
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                  
                  <button
                    onClick={() => setExpandedColumn(expandedColumn === index ? null : index)}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
                    title="View details"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            {/* Expanded Details */}
            {expandedColumn === index && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 pt-4 border-t border-gray-200"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h5 className="font-medium text-gray-900 mb-2">Analysis Details</h5>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="font-medium text-gray-700">Justification:</span>
                        <p className="text-gray-600 mt-1">{field.justification}</p>
                      </div>
                      
                      {field.owner && (
                        <div>
                          <span className="font-medium text-gray-700">Owner:</span>
                          <span className="text-gray-600 ml-2">{field.owner}</span>
                        </div>
                      )}
                      
                      {field.country_code && (
                        <div>
                          <span className="font-medium text-gray-700">Country:</span>
                          <span className="text-gray-600 ml-2">{field.country_code}</span>
                        </div>
                      )}
                      
                      {field.last_seen && (
                        <div>
                          <span className="font-medium text-gray-700">Last Seen:</span>
                          <span className="text-gray-600 ml-2">
                            {new Date(field.last_seen).toLocaleDateString()}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <h5 className="font-medium text-gray-900 mb-2">Masking SQL Preview</h5>
                    <div className="bg-gray-900 text-gray-100 p-3 rounded-lg text-sm font-mono overflow-x-auto">
                      {generateMaskingSQL(field, selectedTemplate)}
                    </div>
                    <div className="mt-2 flex space-x-2">
                      <button
                        onClick={() => copyMaskingSQL(field)}
                        className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 transition-colors"
                      >
                        Copy SQL
                      </button>
                      <button
                        onClick={() => handleAddToMaskingPlan(field)}
                        className="px-3 py-1 bg-green-600 text-white rounded text-xs hover:bg-green-700 transition-colors"
                      >
                        Add to Plan
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Summary */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-blue-900">Quick Actions</h4>
            <p className="text-sm text-blue-700 mt-1">
              Showing top {topColumns.length} highest risk columns
            </p>
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={() => {
                if (onAddToMaskingPlan) {
                  onAddToMaskingPlan(topColumns.slice(0, 10))
                  toast.success('Added top 10 columns to masking plan')
                }
              }}
              className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
            >
              Add Top 10 to Plan
            </button>
            
            <button
              onClick={() => {
                const allSQL = topColumns.slice(0, 10)
                  .map(field => generateMaskingSQL(field, selectedTemplate))
                  .join('\n\n')
                navigator.clipboard.writeText(allSQL)
                toast.success('Top 10 masking SQL copied to clipboard')
              }}
              className="px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm"
            >
              Copy Top 10 SQL
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TopRiskyColumns