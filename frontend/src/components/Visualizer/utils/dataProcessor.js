/**
 * Data Processing Utilities for Schema Visualizer
 * ==============================================
 * 
 * Utilities to convert scanner JSON output to normalized format
 * and create aggregations for different visualizations
 * 
 * @author PII Scanner Team
 * @version 1.0.0
 */

/**
 * Convert scanner report JSON to normalized array format
 * @param {Object} reportData - Raw scanner JSON output
 * @returns {Array} Normalized array of field records
 */
export const convertReportToArray = (reportData) => {
  console.log('🔍 DEBUG dataProcessor: convertReportToArray called with:', reportData)
  
  if (!reportData) {
    console.log('❌ DEBUG dataProcessor: No reportData provided')
    return []
  }

  // Check if we have field_analyses (new format) or analysis_results (old format)
  let fieldAnalyses = {}
  
  if (reportData.field_analyses) {
    console.log('🔍 DEBUG dataProcessor: Using reportData.field_analyses')
    fieldAnalyses = reportData.field_analyses
  } else if (reportData.analysis_results?.field_analyses) {
    console.log('🔍 DEBUG dataProcessor: Using reportData.analysis_results.field_analyses')
    fieldAnalyses = reportData.analysis_results.field_analyses
  } else {
    console.log('❌ DEBUG dataProcessor: No field_analyses found in reportData')
    console.log('🔍 DEBUG dataProcessor: Available keys:', Object.keys(reportData))
    return []
  }

  console.log('🔍 DEBUG dataProcessor: Found fieldAnalyses with keys:', Object.keys(fieldAnalyses))
  console.log('🔍 DEBUG dataProcessor: First few entries:', Object.entries(fieldAnalyses).slice(0, 3))

  const normalizedRecords = []

  Object.entries(fieldAnalyses).forEach(([fieldKey, analysis]) => {
    // Handle different formats of field keys (table.column or just column)
    let table, column
    
    if (fieldKey.includes('.')) {
      [table, column] = fieldKey.split('.', 2)
    } else {
      // If no table.column format, try to extract from analysis or use field key as column
      table = analysis.table_name || analysis.table || 'unknown_table'
      column = analysis.field_name || analysis.column || fieldKey
    }
    
    // Clean up table names - remove any prefixes or clean formatting
    if (table === 'unknown' || table === 'unknown_table') {
      // Try to infer table from field patterns
      if (column.includes('patient_') || column.includes('medical_') || column.includes('diagnosis')) {
        table = 'patient_records'
      } else if (column.includes('customer_') || column.includes('account_') || column.includes('credit_')) {
        table = 'customer_accounts'  
      } else if (column.includes('employee_') || column.includes('salary') || column.includes('hire_')) {
        table = 'employee_directory'
      }
    }

    // Map risk level to numeric score
    const riskScore = mapRiskLevelToScore(analysis.risk_level, analysis.confidence_score)
    
    // Determine classification based on regulations and sensitivity
    const classification = determineClassification(analysis)
    
    // Extract regulations array
    const regulations = analysis.applicable_regulations || []

    const record = {
      table: table,
      column: column,
      data_type: analysis.data_type || 'unknown',
      classification: classification,
      regulations: regulations,
      risk_score: riskScore,
      justification: analysis.rationale || analysis.description || 'No details provided',
      owner: analysis.optional?.owner || null,
      country_code: analysis.optional?.country_code || null,
      last_seen: analysis.optional?.last_seen || null,
      recommended_action: analysis.optional?.recommended_action || 'Review and classify',
      
      // Original analysis data for reference
      _original: analysis
    }

    // Debug first few records to see classification values
    if (normalizedRecords.length < 5) {
      console.log(`🔍 DEBUG dataProcessor: Field ${fieldKey}:`, {
        classification: record.classification,
        regulations: record.regulations,
        risk_score: record.risk_score,
        original_classification: analysis.classification,
        original_regulations: analysis.applicable_regulations
      })
    }

    normalizedRecords.push(record)
  })
  
  console.log('🔍 DEBUG dataProcessor: Sample records:', normalizedRecords.slice(0, 3))
  console.log('🔍 DEBUG dataProcessor: Classification breakdown:', 
    normalizedRecords.reduce((acc, record) => {
      acc[record.classification] = (acc[record.classification] || 0) + 1
      return acc
    }, {})
  )

  return normalizedRecords
}

/**
 * Map risk level and confidence to numeric score (0-100)
 * @param {string} riskLevel - Risk level (LOW, MEDIUM, HIGH, CRITICAL)
 * @param {number} confidence - Confidence score (0-1)
 * @returns {number} Risk score (0-100)
 */
export const mapRiskLevelToScore = (riskLevel, confidence = 0.5) => {
  const riskMapping = {
    'LOW': 20,
    'MEDIUM': 50,
    'HIGH': 80,
    'CRITICAL': 95,
    'NONE': 5
  }
  
  const baseScore = riskMapping[riskLevel?.toUpperCase()] || 30
  
  // Adjust by confidence if available
  if (confidence && typeof confidence === 'number') {
    return Math.round(baseScore * Math.max(0.3, Math.min(1.0, confidence)))
  }
  
  return baseScore
}

/**
 * Determine classification from analysis data
 * @param {Object} analysis - Field analysis object
 * @returns {string} Classification (PHI, PII, SENSITIVE, Unknown)
 */
export const determineClassification = (analysis) => {
  console.log('🔍 DEBUG determineClassification: Processing field with:', {
    classification: analysis.classification,
    is_sensitive: analysis.is_sensitive,
    applicable_regulations: analysis.applicable_regulations,
    pii_type: analysis.pii_type
  })
  
  // First check if the field has an explicit classification
  const originalClassification = analysis.classification || analysis.pii_type
  
  // Map backend classifications to frontend display classifications
  if (originalClassification === 'MEDICAL' || originalClassification === 'HIPAA') {
    console.log('🔍 DEBUG determineClassification: Mapped to PHI')
    return 'PHI'
  }
  
  if (originalClassification === 'PII' || originalClassification === 'PERSONAL_IDENTIFIER' || 
      originalClassification === 'FINANCIAL' || originalClassification === 'CONTACT') {
    console.log('🔍 DEBUG determineClassification: Mapped to PII')
    return 'PII'
  }
  
  // Check regulations if no explicit classification
  const regulations = analysis.applicable_regulations || []
  if (regulations.includes('HIPAA')) {
    console.log('🔍 DEBUG determineClassification: Mapped to PHI via regulations')
    return 'PHI'
  }
  
  // Check for other PII indicators
  if (regulations.includes('GDPR') || regulations.includes('CCPA')) {
    console.log('🔍 DEBUG determineClassification: Mapped to PII via regulations')  
    return 'PII'
  }
  
  // Check is_sensitive flag
  if (analysis.is_sensitive === true) {
    console.log('🔍 DEBUG determineClassification: Mapped to SENSITIVE via is_sensitive flag')
    return 'SENSITIVE'
  }
  
  // Check for NON_SENSITIVE explicit classification
  if (originalClassification === 'NON_SENSITIVE' || analysis.is_sensitive === false) {
    console.log('🔍 DEBUG determineClassification: Mapped to NON_SENSITIVE')
    return 'NON_SENSITIVE'
  }
  
  console.log('🔍 DEBUG determineClassification: Defaulted to Unknown')
  return 'Unknown'
}

/**
 * Aggregate data by table for table-level analysis
 * @param {Array} normalizedData - Array of normalized records
 * @returns {Array} Table aggregation data
 */
export const aggregateByTable = (normalizedData) => {
  const tableMap = {}
  
  normalizedData.forEach(record => {
    const tableName = record.table
    
    if (!tableMap[tableName]) {
      tableMap[tableName] = {
        table: tableName,
        total_fields: 0,
        sensitive_fields: 0,
        avg_risk: 0,
        risk_sum: 0,
        regulations: new Set(),
        classifications: new Set(),
        top_columns: [],
        owner: record.owner,
        country_codes: new Set()
      }
    }
    
    const tableData = tableMap[tableName]
    tableData.total_fields++
    
    if (record.classification !== 'Unknown' && record.classification !== 'NON_SENSITIVE') {
      tableData.sensitive_fields++
    }
    
    tableData.risk_sum += record.risk_score
    tableData.avg_risk = Math.round(tableData.risk_sum / tableData.total_fields)
    
    // Track regulations and classifications
    record.regulations.forEach(reg => tableData.regulations.add(reg))
    tableData.classifications.add(record.classification)
    
    // Track top columns by risk
    tableData.top_columns.push({
      column: record.column,
      risk_score: record.risk_score,
      classification: record.classification
    })
    
    // Track geography
    if (record.country_code) {
      tableData.country_codes.add(record.country_code)
    }
  })
  
  // Post-process aggregated data
  Object.values(tableMap).forEach(table => {
    // Convert sets to arrays
    table.regulations = Array.from(table.regulations)
    table.classifications = Array.from(table.classifications)
    table.country_codes = Array.from(table.country_codes)
    
    // Sort and limit top columns
    table.top_columns.sort((a, b) => b.risk_score - a.risk_score)
    table.top_columns = table.top_columns.slice(0, 5)
    
    // Calculate exposure metric (count * avgRisk)
    table.exposure = table.sensitive_fields * table.avg_risk
  })
  
  return Object.values(tableMap).sort((a, b) => b.exposure - a.exposure)
}

/**
 * Aggregate data by regulation for compliance analysis
 * @param {Array} normalizedData - Array of normalized records
 * @returns {Array} Regulation aggregation data
 */
export const aggregateByRegulation = (normalizedData) => {
  const regulationMap = {}
  
  normalizedData.forEach(record => {
    record.regulations.forEach(regulation => {
      if (!regulationMap[regulation]) {
        regulationMap[regulation] = {
          regulation: regulation,
          count: 0,
          avg_risk: 0,
          risk_sum: 0,
          tables: new Set(),
          high_risk_count: 0
        }
      }
      
      const regData = regulationMap[regulation]
      regData.count++
      regData.risk_sum += record.risk_score
      regData.avg_risk = Math.round(regData.risk_sum / regData.count)
      regData.tables.add(record.table)
      
      if (record.risk_score >= 70) {
        regData.high_risk_count++
      }
    })
  })
  
  // Convert sets to arrays and add metadata
  Object.values(regulationMap).forEach(reg => {
    reg.tables = Array.from(reg.tables)
    reg.table_count = reg.tables.length
  })
  
  return Object.values(regulationMap).sort((a, b) => b.count - a.count)
}

/**
 * Aggregate data by classification type
 * @param {Array} normalizedData - Array of normalized records
 * @returns {Array} Classification aggregation data
 */
export const aggregateByClassification = (normalizedData) => {
  const classificationMap = {}
  
  normalizedData.forEach(record => {
    const classification = record.classification
    
    if (!classificationMap[classification]) {
      classificationMap[classification] = {
        classification: classification,
        count: 0,
        avg_risk: 0,
        risk_sum: 0,
        tables: new Set(),
        regulations: new Set()
      }
    }
    
    const classData = classificationMap[classification]
    classData.count++
    classData.risk_sum += record.risk_score
    classData.avg_risk = Math.round(classData.risk_sum / classData.count)
    classData.tables.add(record.table)
    
    record.regulations.forEach(reg => classData.regulations.add(reg))
  })
  
  // Post-process
  Object.values(classificationMap).forEach(cls => {
    cls.tables = Array.from(cls.tables)
    cls.regulations = Array.from(cls.regulations)
    cls.table_count = cls.tables.length
  })
  
  return Object.values(classificationMap).sort((a, b) => b.count - a.count)
}

/**
 * Aggregate data by owner for responsibility assignment
 * @param {Array} normalizedData - Array of normalized records
 * @returns {Array} Owner aggregation data
 */
export const aggregateByOwner = (normalizedData) => {
  const ownerMap = {}
  
  normalizedData.forEach(record => {
    const owner = record.owner || 'Unknown'
    
    if (!ownerMap[owner]) {
      ownerMap[owner] = {
        owner: owner,
        count: 0,
        avg_risk: 0,
        risk_sum: 0,
        tables: new Set(),
        regulations: new Set(),
        high_risk_count: 0
      }
    }
    
    const ownerData = ownerMap[owner]
    ownerData.count++
    ownerData.risk_sum += record.risk_score
    ownerData.avg_risk = Math.round(ownerData.risk_sum / ownerData.count)
    ownerData.tables.add(record.table)
    
    record.regulations.forEach(reg => ownerData.regulations.add(reg))
    
    if (record.risk_score >= 70) {
      ownerData.high_risk_count++
    }
  })
  
  // Post-process
  Object.values(ownerMap).forEach(owner => {
    owner.tables = Array.from(owner.tables)
    owner.regulations = Array.from(owner.regulations)
    owner.table_count = owner.tables.length
    owner.exposure = owner.count * owner.avg_risk
  })
  
  return Object.values(ownerMap).sort((a, b) => b.exposure - a.exposure)
}

/**
 * Get top risky columns across all data
 * @param {Array} normalizedData - Array of normalized records
 * @param {number} limit - Number of top columns to return
 * @returns {Array} Top risky columns
 */
export const getTopRiskyColumns = (normalizedData, limit = 20) => {
  return normalizedData
    .filter(record => record.classification !== 'Unknown' && record.classification !== 'NON_SENSITIVE')
    .sort((a, b) => b.risk_score - a.risk_score)
    .slice(0, limit)
    .map(record => ({
      ...record,
      field_key: `${record.table}.${record.column}`
    }))
}

/**
 * Generate masking SQL snippet for a field
 * @param {Object} field - Field record
 * @param {string} template - Masking template type
 * @returns {string} SQL snippet
 */
export const generateMaskingSQL = (field, template = 'redact') => {
  const tableName = field.table
  const columnName = field.column
  
  const templates = {
    redact: `UPDATE ${tableName} SET ${columnName} = 'REDACTED' WHERE ${columnName} IS NOT NULL;`,
    nullify: `UPDATE ${tableName} SET ${columnName} = NULL WHERE ${columnName} IS NOT NULL;`,
    hash: `UPDATE ${tableName} SET ${columnName} = SHA256(${columnName}) WHERE ${columnName} IS NOT NULL;`,
    truncate: `UPDATE ${tableName} SET ${columnName} = LEFT(${columnName}, 3) || '***' WHERE ${columnName} IS NOT NULL;`,
    tokenize: `-- Tokenize ${tableName}.${columnName}\n-- Implementation depends on your tokenization service`
  }
  
  return templates[template] || templates.redact
}