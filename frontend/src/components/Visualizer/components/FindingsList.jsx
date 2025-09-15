/**
 * Findings List Component
 * ======================
 * 
 * Virtualized tabular list of all findings with filters and actions
 * Optimized for large datasets with windowed rendering
 * 
 * @author PII Scanner Team
 * @version 1.0.0
 */

import React, { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { 
  Search, 
  Filter, 
  Download, 
  Eye, 
  Shield, 
  AlertTriangle, 
  Copy,
  Plus,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import toast from 'react-hot-toast'

const FindingsList = ({ data, onItemSelect, onAddToMaskingPlan }) => {
  const [sortBy, setSortBy] = useState('risk_score')
  const [sortOrder, setSortOrder] = useState('desc')
  const [selectedRows, setSelectedRows] = useState(new Set())
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(50)
  const [expandedRow, setExpandedRow] = useState(null)

  // Sort and paginate data
  const sortedData = useMemo(() => {
    const sorted = [...data].sort((a, b) => {
      const aVal = a[sortBy]
      const bVal = b[sortBy]
      
      if (sortOrder === 'asc') {
        return aVal < bVal ? -1 : aVal > bVal ? 1 : 0
      } else {
        return aVal > bVal ? -1 : aVal < bVal ? 1 : 0
      }
    })
    return sorted
  }, [data, sortBy, sortOrder])

  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize
    return sortedData.slice(startIndex, startIndex + pageSize)
  }, [sortedData, currentPage, pageSize])

  const totalPages = Math.ceil(sortedData.length / pageSize)

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(column)
      setSortOrder('desc')
    }
  }

  const handleRowSelect = (index, field) => {
    const newSelected = new Set(selectedRows)
    if (newSelected.has(index)) {
      newSelected.delete(index)
    } else {
      newSelected.add(index)
    }
    setSelectedRows(newSelected)
    
    if (onItemSelect) {
      onItemSelect(field)
    }
  }

  const handleSelectAll = () => {
    if (selectedRows.size === paginatedData.length) {
      setSelectedRows(new Set())
    } else {
      setSelectedRows(new Set(paginatedData.map((_, index) => index)))
    }
  }

  const handleAddSelectedToMaskingPlan = () => {
    const selectedFields = paginatedData.filter((_, index) => selectedRows.has(index))
    if (selectedFields.length > 0 && onAddToMaskingPlan) {
      onAddToMaskingPlan(selectedFields)
      setSelectedRows(new Set())
      toast.success(`Added ${selectedFields.length} fields to masking plan`)
    }
  }

  const copyFieldName = (field) => {
    const fieldName = `${field.table}.${field.column}`
    navigator.clipboard.writeText(fieldName)
    toast.success('Field name copied to clipboard')
  }

  const getRiskColor = (riskScore) => {
    if (riskScore >= 80) return 'text-red-600 bg-red-50'
    if (riskScore >= 60) return 'text-orange-600 bg-orange-50'
    if (riskScore >= 40) return 'text-yellow-600 bg-yellow-50'
    return 'text-gray-600 bg-gray-50'
  }

  const SortHeader = ({ column, children }) => (
    <button
      onClick={() => handleSort(column)}
      className="flex items-center space-x-1 text-left font-medium text-gray-700 hover:text-gray-900 transition-colors"
    >
      <span>{children}</span>
      {sortBy === column && (
        sortOrder === 'desc' ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />
      )}
    </button>
  )

  return (
    <div className="space-y-4">
      {/* Header and Controls */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Findings List</h3>
          <p className="text-sm text-gray-600">
            {sortedData.length} findings • {selectedRows.size} selected
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          {selectedRows.size > 0 && (
            <button
              onClick={handleAddSelectedToMaskingPlan}
              className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
            >
              <Plus className="w-4 h-4" />
              <span>Add to Plan ({selectedRows.size})</span>
            </button>
          )}
          
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(parseInt(e.target.value))
              setCurrentPage(1)
            }}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value={25}>25 per page</option>
            <option value={50}>50 per page</option>
            <option value={100}>100 per page</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {/* Table Header */}
        <div className="bg-gray-50 border-b border-gray-200">
          <div className="grid grid-cols-12 gap-4 p-4 text-sm">
            <div className="col-span-1">
              <input
                type="checkbox"
                checked={selectedRows.size === paginatedData.length && paginatedData.length > 0}
                onChange={handleSelectAll}
                className="rounded border-gray-300"
              />
            </div>
            <div className="col-span-3">
              <SortHeader column="table">Table · Column</SortHeader>
            </div>
            <div className="col-span-2">
              <SortHeader column="classification">Classification</SortHeader>
            </div>
            <div className="col-span-2">
              <SortHeader column="risk_score">Risk Score</SortHeader>
            </div>
            <div className="col-span-2">
              <SortHeader column="regulations">Regulations</SortHeader>
            </div>
            <div className="col-span-1">
              <SortHeader column="owner">Owner</SortHeader>
            </div>
            <div className="col-span-1">Actions</div>
          </div>
        </div>

        {/* Table Body */}
        <div className="divide-y divide-gray-200">
          {paginatedData.map((field, index) => (
            <React.Fragment key={`${field.table}.${field.column}`}>
              <div className="grid grid-cols-12 gap-4 p-4 text-sm hover:bg-gray-50 transition-colors">
                <div className="col-span-1">
                  <input
                    type="checkbox"
                    checked={selectedRows.has(index)}
                    onChange={() => handleRowSelect(index, field)}
                    className="rounded border-gray-300"
                  />
                </div>
                
                <div className="col-span-3">
                  <div className="font-mono font-medium text-gray-900">
                    {field.table}.{field.column}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {field.data_type}
                  </div>
                </div>
                
                <div className="col-span-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    field.classification === 'PHI' ? 'bg-red-100 text-red-800' :
                    field.classification === 'PII' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {field.classification}
                  </span>
                </div>
                
                <div className="col-span-2">
                  <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getRiskColor(field.risk_score)}`}>
                    {field.risk_score >= 70 && <AlertTriangle className="w-3 h-3 mr-1" />}
                    {field.risk_score}
                  </div>
                </div>
                
                <div className="col-span-2">
                  <div className="flex flex-wrap gap-1">
                    {field.regulations.map(reg => (
                      <span key={reg} className="px-1 py-0.5 bg-blue-100 text-blue-800 text-xs rounded">
                        {reg}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="col-span-1">
                  <div className="text-xs text-gray-600 truncate">
                    {field.owner || 'Unknown'}
                  </div>
                </div>
                
                <div className="col-span-1">
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => copyFieldName(field)}
                      className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                      title="Copy field name"
                    >
                      <Copy className="w-3 h-3" />
                    </button>
                    <button
                      onClick={() => setExpandedRow(expandedRow === index ? null : index)}
                      className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                      title="View details"
                    >
                      <Eye className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Expanded Row Details */}
              {expandedRow === index && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="bg-gray-50 border-t border-gray-200"
                >
                  <div className="p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">Analysis Details</h5>
                        <div className="space-y-1 text-sm">
                          <div><span className="font-medium">Justification:</span> {field.justification}</div>
                          <div><span className="font-medium">Risk Score:</span> {field.risk_score}/100</div>
                          <div><span className="font-medium">Data Type:</span> {field.data_type}</div>
                          {field.country_code && (
                            <div><span className="font-medium">Country:</span> {field.country_code}</div>
                          )}
                          {field.last_seen && (
                            <div><span className="font-medium">Last Seen:</span> {new Date(field.last_seen).toLocaleDateString()}</div>
                          )}
                        </div>
                      </div>
                      
                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">Recommended Actions</h5>
                        <div className="space-y-2 text-sm">
                          <div>{field.recommended_action}</div>
                          <div className="flex space-x-2 mt-3">
                            <button
                              onClick={() => onAddToMaskingPlan && onAddToMaskingPlan([field])}
                              className="px-2 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 transition-colors"
                            >
                              Add to Masking Plan
                            </button>
                            <button
                              onClick={() => copyFieldName(field)}
                              className="px-2 py-1 bg-gray-600 text-white rounded text-xs hover:bg-gray-700 transition-colors"
                            >
                              Copy Name
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, sortedData.length)} of {sortedData.length} findings
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
            >
              Previous
            </button>
            
            <div className="flex space-x-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const page = i + Math.max(1, currentPage - 2)
                if (page > totalPages) return null
                
                return (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`px-3 py-2 border rounded-lg text-sm transition-colors ${
                      currentPage === page
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'border-gray-300 hover:bg-gray-50 text-gray-700'
                    }`}
                  >
                    {page}
                  </button>
                )
              })}
            </div>
            
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default FindingsList