/**
 * Export Utilities for Schema Visualizer
 * =====================================
 * 
 * Utilities for exporting masking plans as CSV and SQL files
 * Handles proper formatting, escaping, and file generation
 * 
 * @author PII Scanner Team
 * @version 1.0.0
 */

import { generateMaskingSQL } from './dataProcessor'

/**
 * Escape CSV cell content
 * @param {string} cell - Cell content to escape
 * @returns {string} Escaped cell content
 */
export const escapeCsvCell = (cell) => {
  if (cell == null) return ''
  
  const str = String(cell)
  
  // If cell contains comma, newline, or quotes, wrap in quotes and escape quotes
  if (str.includes(',') || str.includes('\n') || str.includes('"')) {
    return `"${str.replace(/"/g, '""')}"`
  }
  
  return str
}

/**
 * Convert masking plan to CSV format
 * @param {Array} plan - Array of field objects
 * @param {string} template - Masking template to use
 * @returns {string} CSV content
 */
export const convertToCSV = (plan, template = 'redact') => {
  if (!plan || plan.length === 0) {
    return 'table,column,risk,masking_snippet\n'
  }

  // CSV headers
  const headers = ['table', 'column', 'classification', 'risk_score', 'regulations', 'masking_snippet']
  let csv = headers.join(',') + '\n'

  // Add rows
  plan.forEach(field => {
    const row = [
      escapeCsvCell(field.table),
      escapeCsvCell(field.column),
      escapeCsvCell(field.classification),
      escapeCsvCell(field.risk_score),
      escapeCsvCell(field.regulations.join(';')),
      escapeCsvCell(generateMaskingSQL(field, template))
    ]
    csv += row.join(',') + '\n'
  })

  return csv
}

/**
 * Convert masking plan to SQL format
 * @param {Array} plan - Array of field objects
 * @param {string} template - Masking template to use
 * @returns {string} SQL content
 */
export const convertToSQL = (plan, template = 'redact') => {
  if (!plan || plan.length === 0) {
    return '-- No masking plan items to generate\n'
  }

  let sql = `-- Masking Plan SQL Script\n`
  sql += `-- Generated: ${new Date().toISOString()}\n`
  sql += `-- Template: ${template}\n`
  sql += `-- Total fields: ${plan.length}\n\n`

  // Group by table for better organization
  const tableGroups = {}
  plan.forEach(field => {
    if (!tableGroups[field.table]) {
      tableGroups[field.table] = []
    }
    tableGroups[field.table].push(field)
  })

  // Generate SQL for each table
  Object.entries(tableGroups).forEach(([tableName, fields]) => {
    sql += `-- ========================================\n`
    sql += `-- Table: ${tableName}\n`
    sql += `-- Fields: ${fields.length}\n`
    sql += `-- ========================================\n\n`

    fields.forEach((field, index) => {
      sql += `-- Field ${index + 1}: ${field.column} (${field.classification}, Risk: ${field.risk_score})\n`
      if (field.regulations.length > 0) {
        sql += `-- Regulations: ${field.regulations.join(', ')}\n`
      }
      sql += generateMaskingSQL(field, template) + '\n\n'
    })
  })

  sql += `-- End of masking plan\n`
  sql += `-- Total statements: ${plan.length}\n`

  return sql
}

/**
 * Download content as file
 * @param {string} content - File content
 * @param {string} filename - File name
 * @param {string} mimeType - MIME type
 */
export const downloadFile = (content, filename, mimeType = 'text/plain') => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  // Clean up the URL object
  setTimeout(() => URL.revokeObjectURL(url), 100)
}

/**
 * Download masking plan as CSV
 * @param {Array} plan - Array of field objects
 * @param {string} template - Masking template to use
 * @param {string} prefix - Filename prefix
 */
export const downloadCSV = (plan, template = 'redact', prefix = 'masking_plan') => {
  const csv = convertToCSV(plan, template)
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
  const filename = `${prefix}_${template}_${timestamp}.csv`
  
  downloadFile(csv, filename, 'text/csv')
}

/**
 * Download masking plan as SQL
 * @param {Array} plan - Array of field objects
 * @param {string} template - Masking template to use
 * @param {string} prefix - Filename prefix
 */
export const downloadSQL = (plan, template = 'redact', prefix = 'masking_plan') => {
  const sql = convertToSQL(plan, template)
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
  const filename = `${prefix}_${template}_${timestamp}.sql`
  
  downloadFile(sql, filename, 'text/sql')
}

/**
 * Generate summary report of masking plan
 * @param {Array} plan - Array of field objects
 * @returns {Object} Summary statistics
 */
export const generatePlanSummary = (plan) => {
  if (!plan || plan.length === 0) {
    return {
      totalFields: 0,
      totalTables: 0,
      byClassification: {},
      byRegulation: {},
      byRiskLevel: {},
      avgRisk: 0,
      estimatedEffort: 0
    }
  }

  const summary = {
    totalFields: plan.length,
    totalTables: new Set(plan.map(f => f.table)).size,
    byClassification: {},
    byRegulation: {},
    byRiskLevel: { low: 0, medium: 0, high: 0, critical: 0 },
    avgRisk: 0,
    estimatedEffort: 0
  }

  let totalRisk = 0

  plan.forEach(field => {
    // Count by classification
    const classification = field.classification || 'Unknown'
    summary.byClassification[classification] = (summary.byClassification[classification] || 0) + 1

    // Count by regulation
    field.regulations.forEach(reg => {
      summary.byRegulation[reg] = (summary.byRegulation[reg] || 0) + 1
    })

    // Count by risk level
    const riskScore = field.risk_score || 0
    totalRisk += riskScore
    
    if (riskScore >= 80) summary.byRiskLevel.critical++
    else if (riskScore >= 60) summary.byRiskLevel.high++
    else if (riskScore >= 40) summary.byRiskLevel.medium++
    else summary.byRiskLevel.low++

    // Estimate effort (in hours) - can be customized
    summary.estimatedEffort += riskScore >= 80 ? 2 : riskScore >= 60 ? 1.5 : 1
  })

  summary.avgRisk = Math.round(totalRisk / plan.length)

  return summary
}

/**
 * Export plan summary as JSON
 * @param {Array} plan - Array of field objects
 * @param {Object} metadata - Additional metadata
 */
export const downloadPlanSummary = (plan, metadata = {}) => {
  const summary = generatePlanSummary(plan)
  
  const exportData = {
    metadata: {
      exportedAt: new Date().toISOString(),
      exportedBy: 'Schema Visualizer',
      version: '1.0.0',
      ...metadata
    },
    summary,
    plan: plan.map(field => ({
      table: field.table,
      column: field.column,
      classification: field.classification,
      risk_score: field.risk_score,
      regulations: field.regulations,
      justification: field.justification
    }))
  }

  const json = JSON.stringify(exportData, null, 2)
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19)
  const filename = `masking_plan_summary_${timestamp}.json`
  
  downloadFile(json, filename, 'application/json')
}

/**
 * Copy content to clipboard
 * @param {string} content - Content to copy
 * @returns {Promise<boolean>} Success status
 */
export const copyToClipboard = async (content) => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(content)
      return true
    } else {
      // Fallback for older browsers or non-secure contexts
      const textArea = document.createElement('textarea')
      textArea.value = content
      textArea.style.position = 'fixed'
      textArea.style.left = '-999999px'
      textArea.style.top = '-999999px'
      document.body.appendChild(textArea)
      textArea.focus()
      textArea.select()
      const result = document.execCommand('copy')
      textArea.remove()
      return result
    }
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
    return false
  }
}

/**
 * Generate masking plan preview
 * @param {Array} plan - Array of field objects
 * @param {string} template - Masking template to use
 * @param {number} limit - Number of items to preview
 * @returns {string} Preview content
 */
export const generatePlanPreview = (plan, template = 'redact', limit = 5) => {
  if (!plan || plan.length === 0) {
    return 'No items in masking plan'
  }

  const previewItems = plan.slice(0, limit)
  let preview = `Masking Plan Preview (${previewItems.length} of ${plan.length} items)\n`
  preview += `Template: ${template}\n\n`

  previewItems.forEach((field, index) => {
    preview += `${index + 1}. ${field.table}.${field.column}\n`
    preview += `   Classification: ${field.classification}, Risk: ${field.risk_score}\n`
    preview += `   SQL: ${generateMaskingSQL(field, template).split('\n')[0]}\n\n`
  })

  if (plan.length > limit) {
    preview += `... and ${plan.length - limit} more items\n`
  }

  return preview
}