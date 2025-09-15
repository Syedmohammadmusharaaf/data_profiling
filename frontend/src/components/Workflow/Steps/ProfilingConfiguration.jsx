import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Shield, Lock, FileText, Plus, X, Eye, Filter } from 'lucide-react'
import toast from 'react-hot-toast'
import { workflowApi } from '../../../services/api'

const ProfilingConfiguration = ({ 
  workflowData, 
  updateWorkflowData, 
  nextStep, 
  previousStep,
  isLoading, 
  setIsLoading 
}) => {
  const [selectedScanType, setSelectedScanType] = useState('')
  const [displayedFields, setDisplayedFields] = useState([])
  const [customFields, setCustomFields] = useState([])
  const [newCustomField, setNewCustomField] = useState('')
  const [showCustomFields, setShowCustomFields] = useState(false)

  const scanTypes = [
    {
      id: 'PII',
      title: 'Data scan for PII fields',
      description: 'General PII detection including emails, phones, addresses, etc.',
      icon: FileText,
      color: 'blue'
    },
    {
      id: 'HIPAA',
      title: 'Data scan specific to HIPAA regulation',
      description: 'Healthcare-focused scanning for PHI and medical data',
      icon: Shield,
      color: 'green'
    },
    {
      id: 'GDPR',
      title: 'Data scan specific to GDPR regulation',
      description: 'European privacy regulation compliance scanning',
      icon: Lock,
      color: 'purple'
    }
  ]

  const handleScanTypeSelection = async (scanType) => {
    setSelectedScanType(scanType)
    setIsLoading(true)

    try {
      const result = await workflowApi.configureScan({
        tables: workflowData.selectedTables || [],
        scan_type: scanType,
        custom_fields: customFields
      })

      setDisplayedFields(result.predefined_patterns || [])
      updateWorkflowData('scanConfig', {
        scanType,
        regulations: result.regulations,
        predefinedPatterns: result.predefined_patterns,
        recommendedFields: result.recommended_fields
      })

      toast.success(`${scanType} scan configured successfully`)
    } catch (error) {
      toast.error(error.message || 'Configuration failed')
    } finally {
      setIsLoading(false)
    }
  }

  const addCustomField = () => {
    if (!newCustomField.trim()) return
    
    if (customFields.includes(newCustomField.trim())) {
      toast.error('Field already exists')
      return
    }

    setCustomFields(prev => [...prev, newCustomField.trim()])
    setNewCustomField('')
    toast.success('Custom field added')
  }

  const removeCustomField = (field) => {
    setCustomFields(prev => prev.filter(f => f !== field))
    toast.success('Custom field removed')
  }

  const handleNext = () => {
    if (!selectedScanType) {
      toast.error('Please select a scan type')
      return
    }

    const finalConfig = {
      ...workflowData.scanConfig,
      customFields,
      finalFieldList: [...displayedFields.map(p => p.name || p), ...customFields]
    }

    updateWorkflowData('scanConfig', finalConfig)
    nextStep({ scanConfig: finalConfig })
  }

  return (
    <div id="profiling-configuration-container" className="space-y-8">
      {/* Step Title */}
      <div id="profiling-configuration-header" className="text-center">
        <h2 id="profiling-configuration-title" className="text-2xl font-bold text-gray-900 mb-2">Profiling Configuration</h2>
        <p id="profiling-configuration-description" className="text-gray-600">Configure scan type and define custom fields</p>
      </div>

      {/* Step 4: Select Scan Type */}
      <motion.div
        id="scan-type-selection-container"
        className="space-y-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div id="scan-type-header" className="flex items-center space-x-2">
          <div id="scan-type-step-icon" className="w-8 h-8 rounded-full flex items-center justify-center bg-blue-100 text-blue-600">
            <span>4</span>
          </div>
          <h3 id="scan-type-title" className="text-lg font-semibold text-gray-900">Select Scan Type</h3>
        </div>

        <div id="scan-types-grid" className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {scanTypes.map((scanType) => {
            const Icon = scanType.icon
            const isSelected = selectedScanType === scanType.id
            
            return (
              <motion.div
                key={scanType.id}
                id={`scan-type-${scanType.id.toLowerCase()}`}
                className={`relative p-6 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
                  isSelected
                    ? `border-${scanType.color}-500 bg-${scanType.color}-50 ring-2 ring-${scanType.color}-200`
                    : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
                }`}
                onClick={() => handleScanTypeSelection(scanType.id)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div id={`scan-type-content-${scanType.id.toLowerCase()}`} className="text-center">
                  <div 
                    id={`scan-type-icon-${scanType.id.toLowerCase()}`}
                    className={`w-16 h-16 mx-auto mb-4 rounded-full bg-${scanType.color}-100 flex items-center justify-center`}
                  >
                    <Icon className={`w-8 h-8 text-${scanType.color}-600`} />
                  </div>
                  <h4 id={`scan-type-title-${scanType.id.toLowerCase()}`} className="font-semibold text-gray-900 mb-2">{scanType.title}</h4>
                  <p id={`scan-type-desc-${scanType.id.toLowerCase()}`} className="text-sm text-gray-600">{scanType.description}</p>
                </div>

                {isSelected && (
                  <motion.div
                    id={`scan-type-selected-indicator-${scanType.id.toLowerCase()}`}
                    className="absolute top-2 right-2"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className={`w-6 h-6 bg-${scanType.color}-500 rounded-full flex items-center justify-center`}>
                      <Eye className="w-4 h-4 text-white" />
                    </div>
                  </motion.div>
                )}
              </motion.div>
            )
          })}
        </div>
      </motion.div>

      {/* Step 5: Display Fields Related to Regulation */}
      {selectedScanType && displayedFields.length > 0 && (
        <motion.div
          id="displayed-fields-container"
          className="space-y-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div id="displayed-fields-header" className="flex items-center space-x-2">
            <div id="displayed-fields-icon" className="w-8 h-8 rounded-full flex items-center justify-center bg-green-100 text-green-600">
              <Eye className="w-5 h-5" />
            </div>
            <h3 id="displayed-fields-title" className="text-lg font-semibold text-gray-900">
              Fields Specific to {selectedScanType} Regulation
            </h3>
          </div>

          <div id="predefined-patterns-container" className="bg-gray-50 rounded-lg p-6">
            <div id="predefined-patterns-grid" className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {displayedFields.map((field, index) => (
                <motion.div
                  key={index}
                  id={`predefined-field-${index}`}
                  className="bg-white rounded-md px-3 py-2 text-sm border border-gray-200"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                >
                  {typeof field === 'string' ? field : field.name || field.pattern}
                </motion.div>
              ))}
            </div>
            
            <div id="predefined-patterns-count" className="mt-4 text-sm text-gray-600">
              <strong>{displayedFields.length}</strong> predefined patterns will be used for detection
            </div>
          </div>
        </motion.div>
      )}

      {/* Step 6: Add Custom Fields */}
      {selectedScanType && (
        <motion.div
          id="custom-fields-container"
          className="space-y-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <div id="custom-fields-header" className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div id="custom-fields-icon" className="w-8 h-8 rounded-full flex items-center justify-center bg-blue-100 text-blue-600">
                <Filter className="w-5 h-5" />
              </div>
              <h3 id="custom-fields-title" className="text-lg font-semibold text-gray-900">Add Custom Fields?</h3>
            </div>
            
            <button
              id="toggle-custom-fields-btn"
              onClick={() => setShowCustomFields(!showCustomFields)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
                showCustomFields
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {showCustomFields ? 'Hide' : 'Show'} Custom Fields
            </button>
          </div>

          {showCustomFields && (
            <motion.div
              id="custom-fields-form"
              className="bg-white rounded-lg border border-gray-200 p-6"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              transition={{ duration: 0.3 }}
            >
              <div className="space-y-4">
                <div id="custom-field-input-container" className="flex space-x-3">
                  <input
                    id="custom-field-input"
                    type="text"
                    value={newCustomField}
                    onChange={(e) => setNewCustomField(e.target.value)}
                    placeholder="Enter custom field name (e.g., customer_ssn, employee_id)"
                    className="form-input flex-1"
                    onKeyPress={(e) => e.key === 'Enter' && addCustomField()}
                  />
                  <button
                    id="add-custom-field-btn"
                    onClick={addCustomField}
                    className="btn-primary flex items-center space-x-2"
                    disabled={!newCustomField.trim()}
                  >
                    <Plus className="w-4 h-4" />
                    <span>Add</span>
                  </button>
                </div>

                {customFields.length > 0 && (
                  <div id="custom-fields-list" className="space-y-2">
                    <h4 id="custom-fields-list-title" className="text-sm font-medium text-gray-700">Custom Fields ({customFields.length})</h4>
                    <div id="custom-fields-tags" className="flex flex-wrap gap-2">
                      {customFields.map((field, index) => (
                        <motion.div
                          key={index}
                          id={`custom-field-tag-${index}`}
                          className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center space-x-2"
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ duration: 0.2 }}
                        >
                          <span>{field}</span>
                          <button
                            id={`remove-custom-field-${index}`}
                            onClick={() => removeCustomField(field)}
                            className="text-blue-600 hover:text-blue-800"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                <div id="custom-fields-tips" className="text-sm text-gray-600">
                  <p><strong>Tips:</strong></p>
                  <ul className="list-disc list-inside space-y-1 mt-2">
                    <li>Use descriptive field names (e.g., "customer_ssn" instead of "ssn")</li>
                    <li>Include table context if helpful (e.g., "users_email", "orders_credit_card")</li>
                    <li>Custom fields will be added to the detection patterns</li>
                  </ul>
                </div>
              </div>
            </motion.div>
          )}
        </motion.div>
      )}

      {/* Summary */}
      {selectedScanType && (
        <motion.div
          id="configuration-summary"
          className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <h4 id="configuration-summary-title" className="font-semibold text-gray-900 mb-3">Configuration Summary</h4>
          <div id="configuration-summary-grid" className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div id="scan-type-summary">
              <span className="text-sm text-gray-600">Scan Type:</span>
              <p className="font-medium text-gray-900">{selectedScanType}</p>
            </div>
            <div id="predefined-patterns-summary">
              <span className="text-sm text-gray-600">Predefined Patterns:</span>
              <p className="font-medium text-gray-900">{displayedFields.length}</p>
            </div>
            <div id="custom-fields-summary">
              <span className="text-sm text-gray-600">Custom Fields:</span>
              <p className="font-medium text-gray-900">{customFields.length}</p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Actions */}
      <div id="profiling-configuration-actions" className="flex justify-between items-center pt-6 border-t">
        <button
          id="profiling-previous-btn"
          onClick={previousStep}
          className="btn-secondary"
          disabled={isLoading}
        >
          Previous
        </button>
        
        <button
          id="continue-to-classification-btn"
          onClick={handleNext}
          className="btn-primary"
          disabled={isLoading || !selectedScanType}
        >
          Continue to Classification
        </button>
      </div>
    </div>
  )
}

export default ProfilingConfiguration