import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import DataPreparation from './Steps/DataPreparation'
import ProfilingConfiguration from './Steps/ProfilingConfiguration'
import AIClassification from './Steps/AIClassification'
import ValidationCompletion from './Steps/ValidationCompletion'
import WorkflowProgress from './WorkflowProgress'
import { workflowApi } from '../../services/api'
import { useLogger, workflowLogger } from '../../utils/logger'

const WorkflowManager = () => {
  const [currentStep, setCurrentStep] = useState(1)
  const [sessionId, setSessionId] = useState(null)
  const [workflowData, setWorkflowData] = useState({
    fileInfo: null,
    schemaData: null,
    scanConfig: null,
    classificationResults: null,
    finalResults: null
  })
  const [isLoading, setIsLoading] = useState(false)
  
  // Enhanced logging
  const workflowManagerLogger = useLogger('WorkflowManager')
  
  useEffect(() => {
    workflowManagerLogger.logMount()
    workflowManagerLogger.info('WorkflowManager initialized', {
      initialStep: currentStep,
      sessionId: sessionId,
      workflowDataKeys: Object.keys(workflowData)
    })
    
    return () => {
      workflowManagerLogger.logUnmount()
    }
  }, [workflowManagerLogger])
  
  const steps = [
    { id: 1, title: 'Data Preparation', component: DataPreparation },
    { id: 2, title: 'Profiling Configuration', component: ProfilingConfiguration },
    { id: 3, title: 'AI Classification', component: AIClassification },
    { id: 4, title: 'Validation & Completion', component: ValidationCompletion }
  ]
  
  const updateWorkflowData = (key, value) => {
    workflowManagerLogger.info(`Update workflow data: ${key}`, {
      key,
      hasValue: !!value,
      valueType: typeof value,
      timestamp: new Date().toISOString()
    })
    
    setWorkflowData(prev => ({
      ...prev,
      [key]: value
    }))
  }
  
  const nextStep = async (data = {}) => {
    try {
      workflowManagerLogger.info('Advancing to next step', {
        currentStep,
        nextStep: currentStep + 1,
        dataKeys: Object.keys(data),
        sessionId
      })
      
      // Update workflow data with step results
      Object.keys(data).forEach(key => {
        updateWorkflowData(key, data[key])
      })
      
      if (currentStep < steps.length) {
        const newStep = currentStep + 1
        setCurrentStep(newStep)
        
        workflowLogger.info(`Step advanced to ${newStep}`, {
          previousStep: currentStep,
          newStep,
          stepTitle: steps[newStep - 1]?.title,
          sessionId
        })
      } else {
        workflowManagerLogger.warn('Attempted to advance beyond final step', {
          currentStep,
          maxSteps: steps.length
        })
      }
    } catch (error) {
      workflowManagerLogger.error('Error advancing to next step', error, {
        currentStep,
        dataKeys: Object.keys(data)
      })
      toast.error('Failed to advance workflow step')
    }
  }
  
  const previousStep = () => {
    try {
      workflowManagerLogger.info('Going back to previous step', {
        currentStep,
        previousStep: currentStep - 1
      })
      
      if (currentStep > 1) {
        const newStep = currentStep - 1
        setCurrentStep(newStep)
        
        workflowLogger.info(`Step reverted to ${newStep}`, {
          previousStep: currentStep,
          newStep,
          stepTitle: steps[newStep - 1]?.title,
          sessionId
        })
      } else {
        workflowManagerLogger.warn('Attempted to go back from first step')
      }
    } catch (error) {
      workflowManagerLogger.error('Error going back to previous step', error)
      toast.error('Failed to go back to previous step')
    }
  }
  
  const goToStep = (stepId) => {
    if (stepId >= 1 && stepId <= steps.length) {
      setCurrentStep(stepId)
    }
  }
  
  const resetWorkflow = () => {
    setCurrentStep(1)
    setSessionId(null)
    setIsLoading(false) // Reset loading state
    setWorkflowData({
      fileInfo: null,
      schemaData: null,
      scanConfig: null,
      classificationResults: null,
      finalResults: null
    })
    
    // Clear any cached session data
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem('pii_scanner_session')
      sessionStorage.removeItem('workflow_progress')
      sessionStorage.removeItem('classification_debug')
    }
    
    // Force page reload to completely reset all component states
    window.location.reload()
  }
  
  // Get current step component
  const CurrentStepComponent = steps.find(step => step.id === currentStep)?.component
  
  return (
    <div id="workflow-manager" className="min-h-screen bg-gray-50">
      {/* Full-width header with better desktop layout */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <motion.div 
            id="workflow-header"
            className="text-center"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 id="workflow-title" className="text-3xl font-bold text-gray-900 mb-2">
              Data File Privacy and Compliance Flow
            </h1>
            <p id="workflow-description" className="text-gray-600 text-lg">
              Enterprise-grade PII/PHI detection and compliance analysis
            </p>
          </motion.div>
          
          {/* Progress Bar */}
          <div className="mt-8">
            <WorkflowProgress 
              id="workflow-progress"
              steps={steps}
              currentStep={currentStep}
              onStepClick={goToStep}
            />
          </div>
        </div>
      </div>
      
      {/* Main content area with full viewport utilization */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 min-h-[calc(100vh-280px)]">
          {/* Step Content Container - Full width usage for desktop */}
          <div id="step-content-container" className="p-6 lg:p-8">
            <AnimatePresence mode="wait">
              {CurrentStepComponent && (
                <motion.div
                  key={currentStep}
                  id={`step-${currentStep}-content`}
                  className="w-full"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <CurrentStepComponent
                    sessionId={sessionId}
                    setSessionId={setSessionId}
                    workflowData={workflowData}
                    updateWorkflowData={updateWorkflowData}
                    nextStep={nextStep}
                    previousStep={previousStep}
                    isLoading={isLoading}
                    setIsLoading={setIsLoading}
                    currentStep={currentStep}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
          
          {/* Bottom info bar - Shows progress only, navigation handled by step components */}
          <div className="border-t border-gray-200 bg-gray-50 px-6 py-4 lg:px-8">
            <div className="flex justify-center items-center">
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-500">
                  Step {currentStep} of {steps.length}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default WorkflowManager