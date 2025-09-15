/**
 * Scatter Quadrant Chart Component
 * ===============================
 * 
 * Prioritization scatter plot using two axes:
 * X = number of findings, Y = average risk
 * Quadrants separate Low/Low, Low/High, High/Low, High/High
 * 
 * @author PII Scanner Team
 * @version 1.0.0
 */

import React, { useState, useMemo } from 'react'
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Cell } from 'recharts'
import { motion } from 'framer-motion'
import { Target, AlertTriangle, TrendingUp, Database } from 'lucide-react'
import { aggregateByTable } from '../utils/dataProcessor'

const ScatterQuadrant = ({ data, onItemSelect, onAddToMaskingPlan }) => {
  const [selectedPoints, setSelectedPoints] = useState([])
  const [hoveredPoint, setHoveredPoint] = useState(null)

  // Prepare scatter plot data
  const scatterData = useMemo(() => {
    const tableData = aggregateByTable(data)
    
    return tableData.map(table => ({
      x: table.sensitive_fields, // Number of sensitive fields
      y: table.avg_risk, // Average risk score
      name: table.table,
      size: Math.max(50, Math.min(200, table.total_fields * 2)), // Size based on total fields
      totalFields: table.total_fields,
      sensitiveFields: table.sensitive_fields,
      avgRisk: table.avg_risk,
      exposure: table.exposure,
      regulations: table.regulations,
      topColumns: table.top_columns,
      _original: table
    }))
  }, [data])

  // Calculate quadrant boundaries (median values)
  const { xMedian, yMedian } = useMemo(() => {
    if (scatterData.length === 0) return { xMedian: 5, yMedian: 50 }
    
    const xValues = scatterData.map(d => d.x).sort((a, b) => a - b)
    const yValues = scatterData.map(d => d.y).sort((a, b) => a - b)
    
    const xMedian = xValues[Math.floor(xValues.length / 2)] || 5
    const yMedian = yValues[Math.floor(yValues.length / 2)] || 50
    
    return { xMedian, yMedian }
  }, [scatterData])

  // Categorize points by quadrant
  const quadrants = useMemo(() => {
    const categories = {
      highRiskHighCount: [], // Top-right: High risk, many fields (Priority 1)
      highRiskLowCount: [],  // Top-left: High risk, few fields (Priority 2)
      lowRiskHighCount: [],  // Bottom-right: Low risk, many fields (Priority 3)
      lowRiskLowCount: []    // Bottom-left: Low risk, few fields (Priority 4)
    }
    
    scatterData.forEach(point => {
      if (point.y >= yMedian && point.x >= xMedian) {
        categories.highRiskHighCount.push(point)
      } else if (point.y >= yMedian && point.x < xMedian) {
        categories.highRiskLowCount.push(point)
      } else if (point.y < yMedian && point.x >= xMedian) {
        categories.lowRiskHighCount.push(point)
      } else {
        categories.lowRiskLowCount.push(point)
      }
    })
    
    return categories
  }, [scatterData, xMedian, yMedian])

  // Color mapping for points based on risk level
  const getPointColor = (avgRisk) => {
    if (avgRisk >= 80) return '#dc2626' // red-600
    if (avgRisk >= 60) return '#ea580c' // orange-600
    if (avgRisk >= 40) return '#ca8a04' // yellow-600
    return '#2563eb' // blue-600
  }

  const handlePointClick = (point) => {
    const isSelected = selectedPoints.find(p => p.name === point.name)
    if (isSelected) {
      setSelectedPoints(prev => prev.filter(p => p.name !== point.name))
    } else {
      setSelectedPoints(prev => [...prev, point])
    }
    
    if (onItemSelect) {
      onItemSelect(point._original)
    }
  }

  const handleBatchMaskingPlan = () => {
    if (selectedPoints.length > 0 && onAddToMaskingPlan) {
      // Get all fields from selected tables
      const selectedTableNames = selectedPoints.map(p => p.name)
      const fieldsToAdd = data.filter(field => 
        selectedTableNames.includes(field.table) && field.classification !== 'Unknown'
      )
      onAddToMaskingPlan(fieldsToAdd)
      setSelectedPoints([])
    }
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg max-w-xs">
          <p className="font-semibold text-gray-900 mb-2">{data.name}</p>
          <div className="space-y-1 text-sm">
            <p className="text-gray-600">Sensitive Fields: {data.sensitiveFields}</p>
            <p className="text-gray-600">Total Fields: {data.totalFields}</p>
            <p className="text-gray-600">Average Risk: {data.avgRisk}</p>
            <p className="text-gray-600">Exposure: {Math.round(data.exposure)}</p>
            {data.regulations.length > 0 && (
              <p className="text-gray-600">Regulations: {data.regulations.join(', ')}</p>
            )}
            {data.topColumns.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-200">
                <p className="font-medium text-gray-700">Top Risk Columns:</p>
                {data.topColumns.slice(0, 3).map(col => (
                  <p key={col.column} className="text-xs text-gray-600">
                    {col.column} ({col.risk_score})
                  </p>
                ))}
              </div>
            )}
          </div>
        </div>
      )
    }
    return null
  }

  if (scatterData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <Target className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No data available for scatter plot</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Prioritization Quadrant</h3>
          <p className="text-sm text-gray-600">
            X-axis: Sensitive field count • Y-axis: Average risk score • Size: Total fields
          </p>
        </div>
        
        {selectedPoints.length > 0 && (
          <div className="flex items-center space-x-3">
            <span className="text-sm text-gray-600">{selectedPoints.length} tables selected</span>
            <button
              onClick={handleBatchMaskingPlan}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
            >
              Add to Masking Plan
            </button>
            <button
              onClick={() => setSelectedPoints([])}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors text-sm"
            >
              Clear Selection
            </button>
          </div>
        )}
      </div>

      {/* Scatter Chart */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 20, right: 20, bottom: 60, left: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis 
                type="number" 
                dataKey="x" 
                name="Sensitive Fields"
                domain={['dataMin - 1', 'dataMax + 1']}
              />
              <YAxis 
                type="number" 
                dataKey="y" 
                name="Average Risk"
                domain={[0, 100]}
              />
              
              {/* Quadrant Reference Lines */}
              <ReferenceLine x={xMedian} stroke="#6b7280" strokeDasharray="5 5" />
              <ReferenceLine y={yMedian} stroke="#6b7280" strokeDasharray="5 5" />
              
              <Tooltip content={<CustomTooltip />} />
              
              <Scatter
                data={scatterData}
                fill="#3b82f6"
              >
                {scatterData.map((entry, index) => {
                  const isSelected = selectedPoints.find(p => p.name === entry.name)
                  return (
                    <Cell
                      key={`cell-${index}`}
                      fill={getPointColor(entry.avgRisk)}
                      stroke={isSelected ? "#1f2937" : "none"}
                      strokeWidth={isSelected ? 3 : 0}
                      className="cursor-pointer hover:opacity-80"
                      onClick={() => handlePointClick(entry)}
                    />
                  )
                })}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>
        
        {/* Quadrant Labels */}
        <div className="relative -mt-8 pointer-events-none">
          <div className="absolute top-0 left-0 w-1/2 h-1/2 flex items-start justify-center pt-4">
            <div className="text-center">
              <div className="text-xs font-semibold text-yellow-700 bg-yellow-100 px-2 py-1 rounded">
                High Risk / Few Fields
              </div>
              <div className="text-xs text-gray-500 mt-1">Priority 2 • Quick fixes</div>
            </div>
          </div>
          <div className="absolute top-0 right-0 w-1/2 h-1/2 flex items-start justify-center pt-4">
            <div className="text-center">
              <div className="text-xs font-semibold text-red-700 bg-red-100 px-2 py-1 rounded">
                High Risk / Many Fields
              </div>
              <div className="text-xs text-gray-500 mt-1">Priority 1 • Urgent action</div>
            </div>
          </div>
          <div className="absolute bottom-0 left-0 w-1/2 h-1/2 flex items-end justify-center pb-4">
            <div className="text-center">
              <div className="text-xs font-semibold text-gray-700 bg-gray-100 px-2 py-1 rounded">
                Low Risk / Few Fields
              </div>
              <div className="text-xs text-gray-500 mt-1">Priority 4 • Monitor</div>
            </div>
          </div>
          <div className="absolute bottom-0 right-0 w-1/2 h-1/2 flex items-end justify-center pb-4">
            <div className="text-center">
              <div className="text-xs font-semibold text-blue-700 bg-blue-100 px-2 py-1 rounded">
                Low Risk / Many Fields
              </div>
              <div className="text-xs text-gray-500 mt-1">Priority 3 • Plan ahead</div>
            </div>
          </div>
        </div>
      </div>

      {/* Quadrant Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <h5 className="font-semibold text-red-900">Priority 1</h5>
          </div>
          <div className="text-2xl font-bold text-red-600 mb-1">
            {quadrants.highRiskHighCount.length}
          </div>
          <div className="text-sm text-red-700 mb-2">High Risk, Many Fields</div>
          {quadrants.highRiskHighCount.length > 0 && (
            <div className="text-xs text-red-600">
              Top: {quadrants.highRiskHighCount[0]?.name}
            </div>
          )}
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Target className="w-5 h-5 text-yellow-600" />
            <h5 className="font-semibold text-yellow-900">Priority 2</h5>
          </div>
          <div className="text-2xl font-bold text-yellow-600 mb-1">
            {quadrants.highRiskLowCount.length}
          </div>
          <div className="text-sm text-yellow-700 mb-2">High Risk, Few Fields</div>
          {quadrants.highRiskLowCount.length > 0 && (
            <div className="text-xs text-yellow-600">
              Top: {quadrants.highRiskLowCount[0]?.name}
            </div>
          )}
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <h5 className="font-semibold text-blue-900">Priority 3</h5>
          </div>
          <div className="text-2xl font-bold text-blue-600 mb-1">
            {quadrants.lowRiskHighCount.length}
          </div>
          <div className="text-sm text-blue-700 mb-2">Low Risk, Many Fields</div>
          {quadrants.lowRiskHighCount.length > 0 && (
            <div className="text-xs text-blue-600">
              Top: {quadrants.lowRiskHighCount[0]?.name}
            </div>
          )}
        </div>

        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Database className="w-5 h-5 text-gray-600" />
            <h5 className="font-semibold text-gray-900">Priority 4</h5>
          </div>
          <div className="text-2xl font-bold text-gray-600 mb-1">
            {quadrants.lowRiskLowCount.length}
          </div>
          <div className="text-sm text-gray-700 mb-2">Low Risk, Few Fields</div>
          {quadrants.lowRiskLowCount.length > 0 && (
            <div className="text-xs text-gray-600">
              Top: {quadrants.lowRiskLowCount[0]?.name}
            </div>
          )}
        </div>
      </div>

      {/* Recommended Actions */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Recommended Actions</h4>
        <div className="space-y-3">
          {quadrants.highRiskHighCount.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg"
            >
              <div>
                <div className="font-semibold text-red-900">Immediate Action Required</div>
                <div className="text-sm text-red-700">
                  {quadrants.highRiskHighCount.length} tables with high risk and many sensitive fields
                </div>
              </div>
              <button
                onClick={() => {
                  if (onAddToMaskingPlan) {
                    const fields = data.filter(field => 
                      quadrants.highRiskHighCount.some(table => table.name === field.table) &&
                      field.classification !== 'Unknown'
                    )
                    onAddToMaskingPlan(fields)
                  }
                }}
                className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm"
              >
                Add All to Plan
              </button>
            </motion.div>
          )}

          {quadrants.highRiskLowCount.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="flex items-center justify-between p-3 bg-yellow-50 border border-yellow-200 rounded-lg"
            >
              <div>
                <div className="font-semibold text-yellow-900">Quick Wins Available</div>
                <div className="text-sm text-yellow-700">
                  {quadrants.highRiskLowCount.length} tables with high risk but few fields - easy to fix
                </div>
              </div>
              <button
                onClick={() => {
                  if (onAddToMaskingPlan) {
                    const fields = data.filter(field => 
                      quadrants.highRiskLowCount.some(table => table.name === field.table) &&
                      field.classification !== 'Unknown'
                    )
                    onAddToMaskingPlan(fields)
                  }
                }}
                className="px-3 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors text-sm"
              >
                Add Quick Wins
              </button>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ScatterQuadrant