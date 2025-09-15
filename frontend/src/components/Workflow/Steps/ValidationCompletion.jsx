/**
 * ValidationCompletion Component
 * =============================
 * 
 * Final step in the PII scanning workflow where users can:
 * - Review and modify field classifications
 * - Validate results with user changes applied
 * - Generate and export final reports
 * - View comprehensive statistics
 * 
 * @author PII Scanner Team
 * @version 2.0.0
 */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Eye, 
  Edit, 
  FileText, 
  CheckCircle, 
  Download,
  Share2,
  BarChart3,
  AlertCircle,
  X,
  Database
} from 'lucide-react'
import toast from 'react-hot-toast'
import { workflowApi } from '../../../services/api'
import SchemaVisualizer from '../../Visualizer/SchemaVisualizer'

const ValidationCompletion = ({ 
  sessionId,
  workflowData, 
  updateWorkflowData, 
  previousStep,
  isLoading, 
  setIsLoading 
}) => {
  // Component state
  const [userChanges, setUserChanges] = useState({})
  const [showChangesModal, setShowChangesModal] = useState(false)
  const [showReportPreviewModal, setShowReportPreviewModal] = useState(false)
  const [reportGenerated, setReportGenerated] = useState(false)
  const [reportData, setReportData] = useState(null)
  const [autoValidated, setAutoValidated] = useState(false)
  const [showSchemaVisualizer, setShowSchemaVisualizer] = useState(false)

  const classificationResults = workflowData.classificationResults || {}
  const consolidatedFields = classificationResults.consolidated || []
  
  // Remove auto-validation - let user manually trigger validation
  useEffect(() => {
    // Only show stats, don't auto-validate
    if (consolidatedFields.length > 0 && !autoValidated) {
      console.log('Classification results available with', consolidatedFields.length, 'fields')
      setAutoValidated(true)
    }
  }, [consolidatedFields.length, autoValidated])

  const handleFieldChange = (fieldIndex, newClassification) => {
    const field = consolidatedFields[fieldIndex]
    setUserChanges(prev => ({
      ...prev,
      [field.field]: {
        oldClassification: field.classification,
        newClassification,
        timestamp: new Date().toISOString()
      }
    }))
    toast.success(`${field.field} classification updated`)
  }

  const validateResults = async () => {
    try {
      setIsLoading(true)
      setReportGenerated(false)
      
      // Check if we have real classification results from backend
      if (!consolidatedFields || consolidatedFields.length === 0) {
        throw new Error('No classification results available. Please run classification first.')
      }
      
      // CRITICAL FIX: Don't send pii_fields_only to avoid backend filtering
      // The backend already has the correct 277 fields - we shouldn't override them
      const validationRequest = {
        session_id: sessionId,
        changes: userChanges,
        // pii_fields_only: removed to prevent backend from filtering to dummy data
      }

      const result = await workflowApi.validateResults(validationRequest)
      
      // Use the backend results as-is without frontend filtering
      const finalResults = result.final_results || result
      
      // Get the actual classification results from workflowData
      const classificationResults = workflowData.classificationResults
      
      // Create proper visualizer data from actual classification results
      const visualizerData = {
        analysis_results: {
          field_analyses: {}
        },
        summary: {
          total_fields: consolidatedFields.length,
          sensitive_fields: consolidatedFields.filter(f => 
            f.classification && 
            f.classification !== 'Non-sensitive' && 
            f.classification !== 'Non-Sensitive' &&
            f.classification !== 'NONE'
          ).length,
          processing_time: classificationResults?.processingTime || '0ms',
          session_id: sessionId
        }
      }

      // Convert consolidated fields with proper classification mapping
      consolidatedFields.forEach(field => {
        const fieldKey = field.field || `${field.table_name || field.tableName}.${field.column_name || field.columnName || field.fieldName}`
        
        // Ensure proper classification - map common variations
        let classification = field.classification
        if (!classification || classification === 'Non-sensitive' || classification === 'Non-Sensitive') {
          classification = 'Non-Sensitive'
        }
        
        // Calculate proper risk score based on classification
        let riskScore = 10 // default low risk
        let riskLevel = 'LOW'
        
        if (classification === 'PHI') {
          riskScore = 85
          riskLevel = 'HIGH'
        } else if (classification === 'PII') {
          riskScore = 65
          riskLevel = 'MEDIUM'
        } else if (classification === 'Sensitive') {
          riskScore = 45
          riskLevel = 'MEDIUM'
        }
        
        // Get regulations - ensure it's an array
        let regulations = field.regulations || []
        if (typeof regulations === 'string') {
          regulations = [regulations]
        }
        if (regulations.length === 0) {
          regulations = classification === 'PHI' ? ['HIPAA'] : classification === 'PII' ? ['GDPR'] : []
        }

        visualizerData.analysis_results.field_analyses[fieldKey] = {
          table_name: field.table_name || field.tableName || 'unknown_table',
          field_name: field.column_name || field.columnName || field.fieldName || field.field || 'unknown_field',
          data_type: field.data_type || field.dataType || 'VARCHAR',
          classification: classification,
          applicable_regulations: regulations,
          confidence_score: field.confidence_score || field.confidenceScore || 0.8,
          risk_level: riskLevel,
          risk_score: riskScore,
          rationale: field.justification || field.rationale || `Classified as ${classification} based on pattern matching`,
          source: field.source || 'enhanced_pattern_matching',
          optional: {
            owner: field.owner || null,
            country_code: field.country_code || null,
            last_seen: field.last_seen || new Date().toISOString()
          }
        }
      })

      updateWorkflowData('finalResults', finalResults)
      updateWorkflowData('visualizerData', visualizerData)
      
      const successMessage = `Results validated! Final report generated with all detected fields`
      toast.success(successMessage)
      
      // Auto-generate report with backend results
      setTimeout(() => generateReport(), 1000)
      
    } catch (error) {
      console.error('Validation error:', error)
      toast.error(error.message || 'Validation failed')
    } finally {
      setIsLoading(false)
    }
  }

  const generateReport = async () => {
    if (!sessionId) return

    try {
      setIsLoading(true)
      
      // First, store the actual classification results in the backend session
      const classificationData = {
        session_id: sessionId,
        classification_results: {
          field_analyses: {},
          summary: {
            total_fields: consolidatedFields.length,
            sensitive_fields: consolidatedFields.filter(f => 
              f.classification && 
              f.classification !== 'Non-sensitive' && 
              f.classification !== 'Non-Sensitive' &&
              f.classification !== 'NONE'
            ).length
          }
        }
      }

      // Convert consolidated fields to proper field analyses format
      consolidatedFields.forEach(field => {
        const fieldKey = field.field || `${field.table_name || field.tableName}.${field.column_name || field.columnName || field.fieldName}`
        
        classificationData.classification_results.field_analyses[fieldKey] = {
          table_name: field.table_name || field.tableName || 'unknown_table',
          field_name: field.column_name || field.columnName || field.fieldName || field.field || 'unknown_field',
          data_type: field.data_type || field.dataType || 'VARCHAR',
          classification: field.classification,
          applicable_regulations: Array.isArray(field.regulations) ? field.regulations : (field.regulations ? [field.regulations] : []),
          confidence_score: field.confidence_score || field.confidenceScore || 0.8,
          risk_level: field.classification === 'PHI' ? 'HIGH' : field.classification === 'PII' ? 'MEDIUM' : 'LOW',
          rationale: field.justification || field.rationale || `Classified as ${field.classification}`,
          source: field.source || 'enhanced_pattern_matching'
        }
      })

      // Update backend session with actual classification data
      await fetch(`${window.location.origin}/api/update-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(classificationData)
      }).catch(e => console.warn('Failed to update session:', e))

      // Now generate the report - it should pull the updated session data
      const result = await workflowApi.generateReport(sessionId, 'json')
      
      console.log('🔍 DEBUG: Generated report result:', result)
      console.log('🔍 DEBUG: Report field_analyses:', result.field_analyses)
      console.log('🔍 DEBUG: Report executive_summary:', result.executive_summary)
      
      // Convert the JSON report to proper visualizer format
      const reportVisualizerData = {
        analysis_results: {
          field_analyses: result.field_analyses || {}
        },
        summary: {
          total_fields: result.executive_summary?.total_fields_analyzed || 0,
          sensitive_fields: result.executive_summary?.sensitive_fields_found || 0,
          processing_time: result.executive_summary?.processing_time || '0ms',
          session_id: sessionId
        }
      }
      
      console.log('🔍 DEBUG: Created visualizer data:', reportVisualizerData)
      console.log('🔍 DEBUG: Field analyses count:', Object.keys(reportVisualizerData.analysis_results.field_analyses).length)
      
      setReportData(result)
      setReportGenerated(true)
      updateWorkflowData('visualizerData', reportVisualizerData) // Use JSON report data for visualizer
      toast.success('📊 Final report generated successfully!')
      
    } catch (error) {
      toast.error(`Report generation failed: ${error.message}`)
      console.error('Report generation error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const downloadReport = (format = 'json') => {
    if (!reportData) return

    const content = format === 'json' 
      ? JSON.stringify(reportData, null, 2)
      : generateCSVReport(reportData)
    
    const blob = new Blob([content], { 
      type: format === 'json' ? 'application/json' : 'text/csv' 
    })
    
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `pii_analysis_report_${sessionId}.${format}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    toast.success(`Report downloaded as ${format.toUpperCase()}`)
  }

  const generateCSVReport = (data) => {
    // Apply user changes to get current field classifications
    const updatedFields = consolidatedFields.map(field => {
      const userChange = userChanges[field.field]
      if (userChange) {
        return {
          ...field,
          classification: userChange.newClassification
        }
      }
      return field
    })

    // Helper function to categorize field classifications
    const categorizeField = (classification) => {
      if (!classification) return 'Non-sensitive'
      
      const classificationUpper = classification.toString().toUpperCase()
      
      // Check for exact PII/PHI matches first
      if (classificationUpper === 'PII') return 'PII'
      if (classificationUpper === 'PHI') return 'PHI'
      
      // Check for medical/health related types (PHI)
      const phiTypes = [
        'MEDICAL', 'MEDICAL_ID', 'MEDICAL_INFO', 'DIAGNOSIS', 'PRESCRIPTION', 
        'HEALTH', 'PATIENT', 'TREATMENT', 'CONDITION', 'SYMPTOM'
      ]
      if (phiTypes.some(type => classificationUpper.includes(type))) return 'PHI'
      
      // Check for personal identifiers (PII)
      const piiTypes = [
        'EMAIL', 'NAME', 'PHONE', 'SSN', 'ID', 'ADDRESS', 'DATE_OF_BIRTH', 
        'FINANCIAL', 'CREDIT_CARD', 'SOCIAL_SECURITY', 'DRIVER_LICENSE',
        'PASSPORT', 'USERNAME', 'PERSON', 'INDIVIDUAL'
      ]
      if (piiTypes.some(type => classificationUpper.includes(type))) return 'PII'
      
      // Check for non-sensitive classifications
      const nonSensitiveTypes = ['NON-PII', 'NON-SENSITIVE', 'NON_PII', 'NON_SENSITIVE', 'NONE']
      if (nonSensitiveTypes.some(type => classificationUpper.includes(type))) return 'Non-sensitive'
      
      // Default to PII for unknown but potentially sensitive classifications
      return 'PII'
    }

    // Filter to only include PII/PHI fields in the CSV report
    const piiFields = updatedFields.filter(field => {
      const category = categorizeField(field.classification)
      return category === 'PII' || category === 'PHI'
    }).map(field => ({
      field_name: field.field,
      classification: field.classification,
      source: field.source,
      needs_review: field.needsReview ? 'Yes' : 'No'
    }))

    const headers = ['Field Name', 'Classification', 'Source', 'Needs Review']
    const csvContent = [
      headers.join(','),
      ...piiFields.map(field => Object.values(field).join(','))
    ].join('\n')

    return csvContent
  }

  const formatJsonForPreview = (jsonData) => {
    return JSON.stringify(jsonData, null, 2)
  }

  const copyJsonToClipboard = async () => {
    if (!reportData) return
    
    try {
      await navigator.clipboard.writeText(formatJsonForPreview(reportData))
      toast.success('JSON copied to clipboard!')
    } catch (error) {
      toast.error('Failed to copy to clipboard')
    }
  }

  // Calculate summary statistics
  // Calculate stats based on current field classifications (with user changes applied)
  const updatedFields = consolidatedFields.map(field => {
    const userChange = userChanges[field.field]
    if (userChange) {
      return {
        ...field,
        classification: userChange.newClassification
      }
    }
    return field
  })

  // Helper function to detect dummy/mock data
  const isDummyField = (field) => {
    const dummyFieldNames = [
      'email', 'first_name', 'last_name', 'phone_number', 'ssn', 
      'date_of_birth', 'credit_card', 'patient_id', 'diagnosis', 'address'
    ]
    
    const dummySourceIndicators = [
      'Enhanced Local Patterns', 'Requires Review', 'Mock', 'Fallback', 'Demo'
    ]
    
    // Check if field name is in generic dummy list
    const isGenericDummy = dummyFieldNames.includes(field.field?.toLowerCase())
    
    // Check if source indicates dummy data
    const isDummySource = dummySourceIndicators.some(indicator => 
      field.source?.includes(indicator)
    )
    
    // Check if all fields have same confidence scores (indicates mock data)
    const hasGenericConfidence = field.confidence === 0.95 || field.confidence === 0.92 || 
                               field.confidence === 0.89 || field.confidence === 0.98
    
    return isGenericDummy && isDummySource && hasGenericConfidence
  }

  // Filter out dummy/mock fields and only include real uploaded DDL fields
  const realFields = updatedFields.filter(field => !isDummyField(field))

  // Helper function to categorize field classifications
  const categorizeField = (classification) => {
    if (!classification) return 'Non-sensitive'
    
    const classificationUpper = classification.toString().toUpperCase()
    
    // Check for exact PII/PHI matches first
    if (classificationUpper === 'PII') return 'PII'
    if (classificationUpper === 'PHI') return 'PHI'
    
    // Check for medical/health related types (PHI)
    const phiTypes = [
      'MEDICAL', 'MEDICAL_ID', 'MEDICAL_INFO', 'DIAGNOSIS', 'PRESCRIPTION', 
      'HEALTH', 'PATIENT', 'TREATMENT', 'CONDITION', 'SYMPTOM'
    ]
    if (phiTypes.some(type => classificationUpper.includes(type))) return 'PHI'
    
    // Check for personal identifiers (PII)
    const piiTypes = [
      'EMAIL', 'NAME', 'PHONE', 'SSN', 'ID', 'ADDRESS', 'DATE_OF_BIRTH', 
      'FINANCIAL', 'CREDIT_CARD', 'SOCIAL_SECURITY', 'DRIVER_LICENSE',
      'PASSPORT', 'USERNAME', 'PERSON', 'INDIVIDUAL'
    ]
    if (piiTypes.some(type => classificationUpper.includes(type))) return 'PII'
    
    // Check for non-sensitive classifications
    const nonSensitiveTypes = ['NON-PII', 'NON-SENSITIVE', 'NON_PII', 'NON_SENSITIVE', 'NONE']
    if (nonSensitiveTypes.some(type => classificationUpper.includes(type))) return 'Non-sensitive'
    
    // Default to PII for unknown but potentially sensitive classifications
    return 'PII'
  }

  const stats = {
    totalFields: realFields.length, // Use real fields count
    piiFields: realFields.filter(f => categorizeField(f.classification) === 'PII').length,
    phiFields: realFields.filter(f => categorizeField(f.classification) === 'PHI').length,
    nonPiiFields: realFields.filter(f => categorizeField(f.classification) === 'Non-sensitive').length,
    changedFields: Object.keys(userChanges).length,
    finalReportFields: realFields.filter(f => {
      const category = categorizeField(f.classification)
      return category === 'PII' || category === 'PHI'
    }).length,
    dummyFieldsExcluded: consolidatedFields.length - realFields.length // Track excluded dummy fields
  }

  return (
    <div className="space-y-8">
      {/* Step Title */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Validation & Completion</h2>
        <p className="text-gray-600">Review results and generate final compliance report</p>
      </div>

      {/* Step 11: User Review */}
      <motion.div
        className="space-y-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-full flex items-center justify-center bg-blue-100 text-blue-600">
              <span>11</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900">User Review of Consolidated Fields</h3>
          </div>
          
          <button
            onClick={() => setShowChangesModal(true)}
            className="btn-secondary flex items-center space-x-2"
          >
            <Edit className="w-4 h-4" />
            <span>Make Changes</span>
          </button>
        </div>

        {/* Summary Dashboard */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600 font-medium">Total Fields</p>
                <p className="text-2xl font-bold text-blue-900">{stats.totalFields}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-500" />
            </div>
          </div>

          <div className="bg-gradient-to-r from-red-50 to-red-100 p-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-red-600 font-medium">PII Fields</p>
                <p className="text-2xl font-bold text-red-900">{stats.piiFields}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-red-500" />
            </div>
          </div>

          <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-6 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-600 font-medium">PHI Fields</p>
                <p className="text-2xl font-bold text-purple-900">{stats.phiFields}</p>
              </div>
              <Eye className="w-8 h-8 text-purple-500" />
            </div>
          </div>

        </div>

        {/* Changes Summary */}
        {Object.keys(userChanges).length > 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h4 className="font-medium text-yellow-900 mb-2">Pending Changes ({Object.keys(userChanges).length})</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {Object.entries(userChanges).map(([field, change]) => (
                <div key={field} className="text-sm">
                  <span className="font-medium">{field}:</span>
                  <span className="text-red-600 line-through ml-1">{change.oldClassification}</span>
                  <span className="text-green-600 ml-1">→ {change.newClassification}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Classification Results Overview */}
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
            <h4 className="text-lg font-semibold text-gray-900">Classification Overview</h4>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600 mb-2">{stats.piiFields}</div>
                <div className="text-sm text-gray-600">PII Fields</div>
                <div className="text-xs text-gray-500 mt-1">
                  {stats.totalFields > 0 ? Math.round((stats.piiFields / stats.totalFields) * 100) : 0}% of total
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-2">{stats.phiFields}</div>
                <div className="text-sm text-gray-600">PHI Fields</div>
                <div className="text-xs text-gray-500 mt-1">
                  {stats.totalFields > 0 ? Math.round((stats.phiFields / stats.totalFields) * 100) : 0}% of total
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-gray-600 mb-2">{stats.nonPiiFields}</div>
                <div className="text-sm text-gray-600">Non-sensitive</div>
                <div className="text-xs text-gray-500 mt-1">
                  {stats.totalFields > 0 ? Math.round((stats.nonPiiFields / stats.totalFields) * 100) : 0}% of total
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Validation Action */}
        <div className="text-center">
          <button
            onClick={validateResults}
            className="btn-primary flex items-center space-x-2 mx-auto"
            disabled={isLoading || reportGenerated}
          >
            <CheckCircle className="w-5 h-5" />
            <span>{reportGenerated ? 'Results Validated' : 'Validate Results'}</span>
          </button>
        </div>
      </motion.div>

      {/* Step 12: Generate Report */}
      {reportGenerated && reportData && (
        <motion.div
          className="space-y-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-full flex items-center justify-center bg-green-100 text-green-600">
              <CheckCircle className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Generate and Share Final Report</h3>
          </div>

          <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h4 className="text-lg font-semibold text-green-900">Report Generated Successfully!</h4>
                <p className="text-green-700">Your PII/PHI compliance analysis is complete</p>
              </div>
              <FileText className="w-12 h-12 text-green-600" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <span className="text-sm text-green-600">Generated:</span>
                <p className="font-medium text-green-900">
                  {new Date(reportData.generated_at).toLocaleString()}
                </p>
              </div>
              <div>
                <span className="text-sm text-green-600">Session:</span>
                <p className="font-medium text-green-900 font-mono text-sm break-all">
                  {sessionId}
                </p>
              </div>
            </div>

            <div id="report-actions" className="flex flex-wrap gap-3">
              <button
                id="preview-report-btn"
                onClick={() => setShowReportPreviewModal(true)}
                className="btn-primary flex items-center space-x-2"
              >
                <Eye className="w-4 h-4" />
                <span>Preview Report</span>
              </button>
              
              <button
                id="schema-visualizer-btn"
                onClick={() => setShowSchemaVisualizer(true)}
                className="btn-primary flex items-center space-x-2 bg-purple-600 hover:bg-purple-700"
              >
                <Database className="w-4 h-4" />
                <span>Schema Visualizer</span>
              </button>
              
              <button
                id="download-json-btn"
                onClick={() => downloadReport('json')}
                className="btn-secondary flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Download JSON</span>
              </button>
              
              <button
                id="download-csv-btn"
                onClick={() => downloadReport('csv')}
                className="btn-secondary flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Download CSV</span>
              </button>
              
              <button
                id="share-report-btn"
                onClick={() => toast.success('Share functionality coming soon!')}
                className="btn-secondary flex items-center space-x-2"
              >
                <Share2 className="w-4 h-4" />
                <span>Share Report</span>
              </button>
            </div>
          </div>

          {/* Process Complete */}
          <div className="text-center py-8">
            <motion.div
              className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.5 }}
            >
              <CheckCircle className="w-8 h-8 text-green-600" />
            </motion.div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Process Complete</h3>
            <p className="text-gray-600">
              Your data privacy and compliance analysis has been successfully completed!
            </p>
          </div>
        </motion.div>
      )}

      {/* Actions */}
      <div className="flex justify-between items-center pt-6 border-t">
        <button
          onClick={previousStep}
          className="btn-secondary"
          disabled={isLoading}
        >
          Previous
        </button>
        
        <div className="flex space-x-3">
          <button
            onClick={() => window.location.href = '/dashboard'}
            className="btn-secondary"
            disabled={!reportGenerated}
          >
            View Dashboard
          </button>
          <button
            onClick={() => window.location.reload()}
            className="btn-primary"
            disabled={!reportGenerated}
          >
            Start New Analysis
          </button>
        </div>
      </div>

      {/* Changes Modal */}
      {showChangesModal && (
        <div id="changes-modal-overlay" className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div id="changes-modal" className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 id="changes-modal-title" className="text-lg font-semibold text-gray-900">Review and Modify Classifications</h3>
              <button
                id="changes-modal-close-btn"
                onClick={() => setShowChangesModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div id="changes-modal-content" className="space-y-3">
              {consolidatedFields.map((field, index) => (
                <div key={index} id={`field-editor-${index}`} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                  <div className="flex-1">
                    <span id={`field-name-${index}`} className="font-medium text-gray-900">{field.field}</span>
                  </div>
                  
                  <div className="flex space-x-2">
                    {['PII', 'PHI', 'Non-PII'].map(classification => (
                      <button
                        key={classification}
                        id={`field-${index}-${classification.toLowerCase().replace('-', '')}`}
                        onClick={() => handleFieldChange(index, classification)}
                        className={`px-3 py-1 text-xs rounded-md transition-colors ${
                          field.classification === classification
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                      >
                        {classification}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                id="changes-modal-done-btn"
                onClick={() => setShowChangesModal(false)}
                className="btn-secondary"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* JSON Report Preview Modal */}
      {showReportPreviewModal && reportData && (
        <div id="report-preview-modal-overlay" className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div id="report-preview-modal" className="bg-white rounded-lg p-6 max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 id="report-preview-title" className="text-lg font-semibold text-gray-900">Report Preview - JSON Format</h3>
              <div className="flex items-center space-x-2">
                <button
                  id="copy-json-btn"
                  onClick={copyJsonToClipboard}
                  className="text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                  title="Copy JSON to clipboard"
                >
                  <Download className="w-4 h-4" />
                  <span className="text-sm">Copy</span>
                </button>
                <button
                  id="report-preview-close-btn"
                  onClick={() => setShowReportPreviewModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            {/* Report Summary */}
            <div id="report-summary" className="bg-gray-50 rounded-lg p-4 mb-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div id="report-generated-at">
                  <span className="text-gray-600">Generated:</span>
                  <p className="font-medium">{new Date(reportData.generated_at).toLocaleString()}</p>
                </div>
                <div id="report-file-name">
                  <span className="text-gray-600">File:</span>
                  <p className="font-medium">{reportData.file_info?.name}</p>
                </div>
                <div id="report-total-findings">
                  <span className="text-gray-600">Total Findings:</span>
                  <p className="font-medium">{reportData.analysis_results?.findings?.length || 0}</p>
                </div>
                <div id="report-compliance-score">
                  <span className="text-gray-600">Compliance Score:</span>
                  <p className="font-medium">{reportData.compliance_score || 'N/A'}%</p>
                </div>
              </div>
            </div>
            
            {/* JSON Preview */}
            <div id="json-preview-container" className="border border-gray-200 rounded-lg">
              <div id="json-preview-header" className="bg-gray-100 px-4 py-2 border-b border-gray-200 flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">JSON Content</span>
                <span className="text-xs text-gray-500">
                  {JSON.stringify(reportData).length} characters
                </span>
              </div>
              <pre id="json-preview-content" className="p-4 text-xs overflow-x-auto bg-gray-900 text-green-400 rounded-b-lg">
                <code>{formatJsonForPreview(reportData)}</code>
              </pre>
            </div>
            
            {/* Preview Actions */}
            <div id="preview-modal-actions" className="flex justify-between items-center mt-6">
              <div className="text-sm text-gray-600">
                Preview of the complete JSON report that will be downloaded
              </div>
              <div className="flex space-x-3">
                <button
                  id="preview-download-json-btn"
                  onClick={() => {
                    downloadReport('json')
                    setShowReportPreviewModal(false)
                  }}
                  className="btn-primary flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>Download JSON</span>
                </button>
                <button
                  id="preview-modal-close-bottom-btn"
                  onClick={() => setShowReportPreviewModal(false)}
                  className="btn-secondary"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Schema Visualizer Modal */}
      {showSchemaVisualizer && workflowData.visualizerData && (
        <SchemaVisualizer 
          reportData={workflowData.visualizerData}
          onClose={() => setShowSchemaVisualizer(false)}
        />
      )}
    </div>
  )
}

export default ValidationCompletion