import React from 'react'
import { motion } from 'framer-motion'
import { Check, Upload, Settings, Cpu, CheckCircle } from 'lucide-react'

const WorkflowProgress = ({ steps, currentStep, className = '', id = 'workflow-progress', onStepClick = null }) => {
  const getStepIcon = (stepId) => {
    const icons = {
      1: Upload,
      2: Settings,
      3: Cpu,
      4: CheckCircle
    }
    return icons[stepId] || Check
  }

  const getStepStatus = (stepId) => {
    if (stepId < currentStep) return 'completed'
    if (stepId === currentStep) return 'active'
    return 'pending'
  }

  const handleStepClick = (stepId) => {
    if (onStepClick && stepId <= currentStep) {
      onStepClick(stepId)
    }
  }

  return (
    <div id={id} className={`w-full ${className}`}>
      <div id="progress-steps-container" className="flex items-center justify-between">
        {steps.map((step, index) => {
          const Icon = getStepIcon(step.id)
          const status = getStepStatus(step.id)
          const isLast = index === steps.length - 1
          const isClickable = onStepClick && step.id <= currentStep

          return (
            <React.Fragment key={step.id}>
              {/* Step */}
              <div 
                id={`progress-step-${step.id}`} 
                className={`flex flex-col items-center ${isClickable ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}`}
                onClick={() => handleStepClick(step.id)}
              >
                <motion.div
                  id={`progress-step-icon-${step.id}`}
                  className={`relative flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-300 ${
                    status === 'completed'
                      ? 'bg-green-500 border-green-500 text-white'
                      : status === 'active'
                      ? 'bg-blue-500 border-blue-500 text-white animate-pulse'
                      : 'bg-gray-100 border-gray-300 text-gray-400'
                  }`}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  {status === 'completed' ? (
                    <Check className="w-6 h-6" />
                  ) : (
                    <Icon className="w-6 h-6" />
                  )}
                  
                  {/* Step number */}
                  <div 
                    id={`progress-step-number-${step.id}`}
                    className="absolute -top-2 -right-2 w-6 h-6 bg-white border-2 border-gray-200 rounded-full flex items-center justify-center"
                  >
                    <span className="text-xs font-bold text-gray-600">{step.id}</span>
                  </div>
                </motion.div>

                {/* Step title */}
                <motion.div
                  id={`progress-step-title-${step.id}`}
                  className="mt-3 text-center"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 + 0.2 }}
                >
                  <h3 className={`text-sm font-medium ${
                    status === 'active' ? 'text-blue-600' : 'text-gray-700'
                  }`}>
                    {step.title}
                  </h3>
                  <p id={`progress-step-status-${step.id}`} className="text-xs text-gray-500 mt-1">
                    {status === 'completed' && 'Completed'}
                    {status === 'active' && 'In Progress'}
                    {status === 'pending' && 'Pending'}
                  </p>
                </motion.div>
              </div>

              {/* Connector line */}
              {!isLast && (
                <motion.div
                  id={`progress-connector-${step.id}`}
                  className={`flex-1 h-1 mx-4 rounded transition-all duration-500 ${
                    step.id < currentStep ? 'bg-green-500' : 'bg-gray-200'
                  }`}
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{ duration: 0.8, delay: index * 0.2 }}
                />
              )}
            </React.Fragment>
          )
        })}
      </div>

      {/* Progress percentage */}
      <div id="progress-percentage-container" className="mt-6">
        <div className="flex justify-between items-center mb-2">
          <span id="progress-label" className="text-sm font-medium text-gray-700">Overall Progress</span>
          <span id="progress-percentage-value" className="text-sm font-medium text-blue-600">
            {Math.round((currentStep / steps.length) * 100)}%
          </span>
        </div>
        <div id="progress-bar" className="progress-bar">
          <motion.div
            id="progress-fill"
            className="progress-fill"
            initial={{ width: 0 }}
            animate={{ width: `${(currentStep / steps.length) * 100}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
        </div>
      </div>
    </div>
  )
}

export default WorkflowProgress