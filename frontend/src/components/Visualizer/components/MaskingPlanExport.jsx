/**
 * Masking Plan Export Component with Preview
 * =========================================
 * 
 * Enhanced export functionality for masking plans with preview modal
 * Supports CSV, SQL, and JSON formats with visual preview before download
 * 
 * @author PII Scanner Team
 * @version 2.0.0
 */

import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Download, 
  FileText, 
  Database, 
  Copy, 
  Eye, 
  X,
  Code,
  FileJson,
  Table,
  Check
} from 'lucide-react'
import toast from 'react-hot-toast'
import { generateMaskingSQL } from '../utils/dataProcessor'

const MaskingPlanExport = ({ data = [], onClose }) => {
  const [selectedTemplate, setSelectedTemplate] = useState('hash')
  const [showPreview, setShowPreview] = useState(false)
  const [exportFormat, setExportFormat] = useState('sql')
  const [selectedFields, setSelectedFields] = useState([])

  // Filter to sensitive fields only
  const sensitiveFields = useMemo(() => {
    if (!data || !Array.isArray(data)) {
      return []
    }
    return data.filter(field => 
      field.classification !== 'Unknown' && 
      field.classification !== 'NON_SENSITIVE'
    )
  }, [data])

  // Auto-select all sensitive fields on mount
  React.useEffect(() => {
    if (sensitiveFields.length > 0) {
      setSelectedFields(sensitiveFields.map(field => `${field.table}.${field.column}`))
    }
  }, [sensitiveFields])

  // If no data available, show empty state
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg p-6 max-h-full overflow-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-semibold text-gray-900">Export Masking Plan</h3>
            <p className="text-sm text-gray-600 mt-1">
              Generate SQL scripts or reports for data masking implementation
            </p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg mb-2">No Data Available</div>
          <div className="text-gray-400 text-sm">
            Please complete a scan first to generate masking plans
          </div>
        </div>
      </div>
    )
  }

  const templates = [
    { 
      id: 'redact', 
      name: 'Redact', 
      description: 'Replace with "REDACTED" text',
      example: 'UPDATE table SET column = "REDACTED" WHERE column IS NOT NULL;'
    },
    { 
      id: 'nullify', 
      name: 'Nullify', 
      description: 'Set to NULL values',
      example: 'UPDATE table SET column = NULL WHERE column IS NOT NULL;'
    },
    { 
      id: 'hash', 
      name: 'Hash (Recommended)', 
      description: 'Replace with SHA256 hash - preserves uniqueness',
      example: 'UPDATE table SET column = SHA256(column) WHERE column IS NOT NULL;'
    },
    { 
      id: 'truncate', 
      name: 'Truncate', 
      description: 'Keep first 3 chars + *** (for readability)',
      example: 'UPDATE table SET column = LEFT(column, 3) || "***" WHERE column IS NOT NULL;'
    }
  ]

  const exportFormats = [
    { id: 'sql', name: 'SQL Script', icon: Database, description: 'Ready-to-execute SQL statements' },
    { id: 'csv', name: 'CSV Report', icon: Table, description: 'Spreadsheet-compatible field list' },
    { id: 'json', name: 'JSON Plan', icon: FileJson, description: 'Machine-readable configuration' }
  ]

  // Generate preview content
  const previewContent = useMemo(() => {
    const fieldsToMask = sensitiveFields.filter(field => 
      selectedFields.includes(`${field.table}.${field.column}`)
    )

    if (exportFormat === 'sql') {
      return fieldsToMask.map(field => generateMaskingSQL(field, selectedTemplate)).join('\n\n')
    } else if (exportFormat === 'csv') {
      const headers = ['Table', 'Column', 'Classification', 'Risk Score', 'Masking Method', 'Justification']
      const rows = fieldsToMask.map(field => [
        field.table,
        field.column,
        field.classification,
        field.risk_score,
        selectedTemplate,
        field.justification || 'Sensitive data requiring protection'
      ])
      return [headers, ...rows].map(row => row.join(',')).join('\n')
    } else if (exportFormat === 'json') {
      return JSON.stringify({
        masking_plan: {
          created: new Date().toISOString(),
          template: selectedTemplate,
          total_fields: fieldsToMask.length,
          fields: fieldsToMask.map(field => ({
            table: field.table,
            column: field.column,
            classification: field.classification,
            risk_score: field.risk_score,
            regulations: field.regulations,
            masking_method: selectedTemplate,
            sql: generateMaskingSQL(field, selectedTemplate)
          }))
        }
      }, null, 2)
    }
    return ''
  }, [sensitiveFields, selectedFields, selectedTemplate, exportFormat])

  // Statistics
  const stats = useMemo(() => {
    const selected = sensitiveFields.filter(field => 
      selectedFields.includes(`${field.table}.${field.column}`)
    )
    
    const byTable = selected.reduce((acc, field) => {
      acc[field.table] = (acc[field.table] || 0) + 1
      return acc
    }, {})

    return {
      totalSelected: selected.length,
      totalSensitive: sensitiveFields.length,
      byTable,
      avgRisk: selected.length > 0 ? Math.round(selected.reduce((sum, f) => sum + f.risk_score, 0) / selected.length) : 0
    }
  }, [sensitiveFields, selectedFields])

  const handleExport = () => {
    const filename = `masking_plan_${selectedTemplate}_${new Date().toISOString().split('T')[0]}`
    
    if (exportFormat === 'sql') {
      const blob = new Blob([previewContent], { type: 'text/sql' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${filename}.sql`
      a.click()
      URL.revokeObjectURL(url)
    } else if (exportFormat === 'csv') {
      const blob = new Blob([previewContent], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${filename}.csv`
      a.click()
      URL.revokeObjectURL(url)
    } else if (exportFormat === 'json') {
      const blob = new Blob([previewContent], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${filename}.json`
      a.click()
      URL.revokeObjectURL(url)
    }
    
    toast.success(`Exported ${stats.totalSelected} field masking plan successfully!`)
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(previewContent)
    toast.success('Masking plan copied to clipboard!')
  }

  const toggleFieldSelection = (fieldKey) => {
    setSelectedFields(prev => 
      prev.includes(fieldKey) 
        ? prev.filter(f => f !== fieldKey)
        : [...prev, fieldKey]
    )
  }

  const selectAll = () => {
    setSelectedFields(sensitiveFields.map(field => `${field.table}.${field.column}`))
  }

  const selectNone = () => {
    setSelectedFields([])
  }

  return (
    <div className="bg-white rounded-lg p-6 max-h-full overflow-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">Export Masking Plan</h3>
          <p className="text-sm text-gray-600 mt-1">
            Generate SQL scripts or reports for data masking implementation
          </p>
        </div>
        <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
          <X className="w-5 h-5 text-gray-500" />
        </button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-50 p-3 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{stats.totalSelected}</div>
          <div className="text-sm text-blue-800">Fields Selected</div>
        </div>
        <div className="bg-yellow-50 p-3 rounded-lg">
          <div className="text-2xl font-bold text-yellow-600">{stats.totalSensitive}</div>
          <div className="text-sm text-yellow-800">Sensitive Fields</div>
        </div>
        <div className="bg-red-50 p-3 rounded-lg">
          <div className="text-2xl font-bold text-red-600">{stats.avgRisk}</div>
          <div className="text-sm text-red-800">Avg Risk Score</div>
        </div>
        <div className="bg-green-50 p-3 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{Object.keys(stats.byTable).length}</div>
          <div className="text-sm text-green-800">Tables Affected</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - Configuration */}
        <div className="space-y-6">
          {/* Masking Template Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Masking Template
            </label>
            <div className="space-y-2">
              {templates.map(template => (
                <div
                  key={template.id}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedTemplate === template.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedTemplate(template.id)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">{template.name}</div>
                      <div className="text-sm text-gray-600">{template.description}</div>
                    </div>
                    {selectedTemplate === template.id && (
                      <Check className="w-5 h-5 text-blue-500" />
                    )}
                  </div>
                  {selectedTemplate === template.id && (
                    <div className="mt-2 p-2 bg-gray-100 rounded text-xs font-mono text-gray-700">
                      {template.example}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Export Format Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Export Format
            </label>
            <div className="grid grid-cols-3 gap-2">
              {exportFormats.map(format => (
                <button
                  key={format.id}
                  onClick={() => setExportFormat(format.id)}
                  className={`p-3 rounded-lg border text-center transition-colors ${
                    exportFormat === format.id
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <format.icon className="w-6 h-6 mx-auto mb-1" />
                  <div className="font-medium text-sm">{format.name}</div>
                  <div className="text-xs text-gray-600">{format.description}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - Field Selection */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-medium text-gray-700">
              Fields to Mask ({stats.totalSelected} selected)
            </label>
            <div className="space-x-2">
              <button
                onClick={selectAll}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Select All
              </button>
              <button
                onClick={selectNone}
                className="text-sm text-gray-600 hover:text-gray-800"
              >
                Select None
              </button>
            </div>
          </div>
          
          <div className="max-h-80 overflow-y-auto border border-gray-200 rounded-lg">
            {sensitiveFields.map((field) => {
              const fieldKey = `${field.table}.${field.column}`
              const isSelected = selectedFields.includes(fieldKey)
              
              return (
                <div
                  key={fieldKey}
                  className={`p-3 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                    isSelected ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => toggleFieldSelection(fieldKey)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{fieldKey}</div>
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          field.classification === 'PHI' 
                            ? 'bg-red-100 text-red-700' 
                            : 'bg-yellow-100 text-yellow-700'
                        }`}>
                          {field.classification}
                        </span>
                        <span>Risk: {field.risk_score}</span>
                        {field.regulations && field.regulations.length > 0 && (
                          <span>Regulations: {field.regulations.join(', ')}</span>
                        )}
                      </div>
                    </div>
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggleFieldSelection(fieldKey)}
                      className="w-4 h-4 text-blue-600"
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-200">
        <button
          onClick={() => setShowPreview(!showPreview)}
          className="flex items-center space-x-2 px-4 py-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
        >
          <Eye className="w-4 h-4" />
          <span>{showPreview ? 'Hide' : 'Show'} Preview</span>
        </button>
        
        <div className="flex space-x-3">
          <button
            onClick={copyToClipboard}
            className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Copy className="w-4 h-4" />
            <span>Copy</span>
          </button>
          
          <button
            onClick={handleExport}
            disabled={stats.totalSelected === 0}
            className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export Plan</span>
          </button>
        </div>
      </div>

      {/* Preview Modal */}
      <AnimatePresence>
        {showPreview && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="mt-6 border border-gray-200 rounded-lg bg-gray-50"
          >
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <Code className="w-5 h-5 text-gray-600" />
                <span className="font-medium">
                  {exportFormat.toUpperCase()} Preview ({selectedTemplate} template)
                </span>
              </div>
              <button
                onClick={() => setShowPreview(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            
            <div className="p-4">
              <pre className="text-sm font-mono text-gray-800 bg-white p-4 rounded border max-h-96 overflow-auto">
                {previewContent}
              </pre>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default MaskingPlanExport