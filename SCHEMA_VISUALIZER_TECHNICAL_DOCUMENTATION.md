# Schema Visualizer - Technical Documentation

## Overview

The Schema Visualizer is an interactive React dashboard component that processes PII/PHI scanner results and presents them through multiple visualization types. It transforms raw classification data into actionable insights for data privacy compliance.

## Architecture

### Component Structure
```
SchemaVisualizer.jsx (Main Container)
├── components/
│   ├── Heatmap.jsx (Table-level risk heatmap)
│   ├── FindingsList.jsx (Virtualized findings table)
│   ├── Treemap.jsx (Hierarchical exposure analysis)
│   ├── RegulationPieChart.jsx (Compliance distribution)
│   ├── MaskingPlanExport.jsx (SQL generation & export)
│   ├── ScatterQuadrant.jsx (Risk prioritization matrix)
│   ├── TopRiskColumns.jsx (Highest risk fields)
│   └── SankeyFlow.jsx (Data flow visualization)
├── utils/
│   ├── dataProcessor.js (Core data transformation)
│   └── exportUtils.js (Export functionality)
```

## Data Flow Pipeline

### 1. Input Data Source
```javascript
// Data flows from backend classification results
POST /api/generate-report/{session_id} 
→ Returns: {
  analysis_results: {
    field_analyses: {
      "table.field": {
        classification: "MEDICAL" | "PII" | "NON_SENSITIVE",
        applicable_regulations: ["HIPAA", "GDPR", "CCPA"],
        is_sensitive: boolean,
        confidence_score: 0.0-1.0,
        rationale: "explanation"
      }
    }
  }
}
```

### 2. Data Transformation (dataProcessor.js)
```javascript
convertReportToArray(reportData) → normalizedRecords[]
├── determineClassification() → Maps backend classifications to UI types
├── mapRiskLevelToScore() → Converts confidence to 0-100 risk score
├── aggregateByTable() → Groups fields by table for heatmap
├── aggregateByRegulation() → Groups by compliance requirements
└── getTopRiskyColumns() → Identifies highest priority fields
```

### 3. Classification Mapping Logic
```javascript
Backend Classification → Frontend Display
"MEDICAL" → "PHI" (Protected Health Information)
"PII" → "PII" (Personally Identifiable Information)  
"FINANCIAL" → "PII" (Financial PII)
"NON_SENSITIVE" → "NON_SENSITIVE"
Unknown/Undefined → "Unknown"
```

### 4. Visualization Data Structures

#### Table Aggregation
```javascript
{
  table: "patient_records",
  total_fields: 6,
  sensitive_fields: 4,
  avg_risk: 85,
  regulations: ["HIPAA"],
  top_columns: [
    {column: "medical_record_number", risk_score: 95, classification: "PHI"}
  ]
}
```

#### Field Analysis Record
```javascript
{
  table: "patient_records",
  column: "medical_record_number", 
  classification: "PHI",
  regulations: ["HIPAA"],
  risk_score: 95,
  justification: "Medical record identifiers are PHI under HIPAA",
  recommended_action: "Mask with tokenization"
}
```

## Visualization Components Deep Dive

### 1. Table Heatmap (Heatmap.jsx)
**Purpose**: Table-level risk exposure overview
**Data Source**: `aggregateByTable(normalizedData)`
**Logic**: 
- Color intensity based on `avg_risk` score
- Size based on `total_fields` count
- Displays sensitive field ratio and regulation compliance

**Key Metrics**:
- Risk Score: 0-39 (Low), 40-69 (Medium), 70-89 (High), 90+ (Critical)
- Exposure = sensitive_fields × avg_risk

### 2. Priority Quadrant (ScatterQuadrant.jsx)  
**Purpose**: Risk vs exposure prioritization matrix
**Data Source**: Table aggregations
**Logic**:
- X-axis: Sensitive field count (exposure)
- Y-axis: Average risk score
- Quadrants: Priority 1 (High Risk/Many Fields) → Priority 4 (Low Risk/Few Fields)

### 3. Findings List (FindingsList.jsx)
**Purpose**: Detailed field-level analysis with filtering
**Data Source**: `normalizedRecords` array
**Features**:
- Virtual scrolling for performance (handles 1000+ records)
- Multi-column filtering (classification, regulation, table, risk level)
- Sortable columns
- Export selected findings

### 4. Treemap Analysis (Treemap.jsx)
**Purpose**: Hierarchical view of data exposure by classification/regulation
**Data Source**: `aggregateByClassification()` and `aggregateByRegulation()`
**Logic**: 
- Size = field count
- Color = average risk level
- Grouping by Classification → Regulation → Table

### 5. Regulation Distribution (RegulationPieChart.jsx)
**Purpose**: Compliance scope visualization
**Data Source**: `aggregateByRegulation(normalizedData)`
**Shows**: Field count distribution across HIPAA, GDPR, CCPA, PCI-DSS

### 6. Top Risk Columns (TopRiskColumns.jsx)
**Purpose**: Immediate attention priority list
**Data Source**: `getTopRiskyColumns(normalizedData, limit=20)`
**Logic**: Filters sensitive fields, sorts by risk_score descending

### 7. Masking Plan Export (MaskingPlanExport.jsx) 
**Purpose**: Generate SQL masking statements
**Logic**:
```javascript
generateMaskingSQL(field, template) → SQL statement
Templates: 'redact', 'nullify', 'hash', 'truncate', 'tokenize'

Example Output:
UPDATE patient_records SET medical_record_number = SHA256(medical_record_number) 
WHERE medical_record_number IS NOT NULL;
```

## Performance Optimizations

### 1. Virtual Scrolling
- FindingsList uses react-window for handling large datasets
- Renders only visible rows (handles 10,000+ records smoothly)

### 2. Data Processing Caching
- Aggregations computed once and cached
- Memoized expensive calculations using useMemo()

### 3. Defensive Rendering
- Graceful handling of missing/malformed data
- Loading states and error boundaries
- Progressive data loading for better UX

## Integration Points

### 1. Backend Integration
```javascript
// Triggered after classification completion
ValidationCompletion.jsx → onClick="View Schema Visualizer"
→ Passes workflowData.visualizerData (from generated report)
→ SchemaVisualizer processes via dataProcessor.js
```

### 2. Workflow Integration
```javascript
// Data flow through workflow steps:
DataPreparation → ProfilingConfiguration → AIClassification → ValidationCompletion
                                                                        ↓
                                                              generate-report API
                                                                        ↓ 
                                                              Schema Visualizer
```

## Data Quality Validation

### 1. Input Validation
- Checks for required fields in analysis_results
- Validates field_analyses structure
- Handles missing classifications gracefully

### 2. Classification Accuracy
- Backend provides context-aware regulation assignment
- Healthcare fields → HIPAA (PHI)
- Financial/Personal fields → GDPR/CCPA (PII)
- System fields → NON_SENSITIVE

### 3. Risk Score Calculation
```javascript
// Risk scoring algorithm
baseRiskScore = {
  'LOW': 20, 'MEDIUM': 50, 'HIGH': 80, 'CRITICAL': 95, 'NONE': 5
}
finalScore = baseRiskScore × confidence_score
// Ensures risk scores reflect both sensitivity and AI confidence
```

## Export Functionality

### 1. Masking Plan Generation
- Analyzes sensitive fields and generates appropriate SQL
- Supports multiple masking strategies per field type
- Includes field-specific recommendations

### 2. Report Export
- CSV export of findings list with filters
- JSON export of complete analysis
- PDF summary report (future enhancement)

## User Experience Design

### 1. Color Palette
- Light pastel colors for accessibility
- Risk-based color coding: Green (Low) → Yellow (Medium) → Orange (High) → Red (Critical)
- Consistent color mapping across all visualizations

### 2. Responsive Design
- Desktop-first approach (primary use case)
- Collapsible sidebar for smaller screens
- Keyboard navigation support

### 3. Interactive Elements
- Click-to-filter on charts
- Hover tooltips with detailed information
- Drill-down capabilities from aggregate to field level

## Error Handling & Edge Cases

### 1. Data Edge Cases
- Empty classification results → Shows "No data available" state
- Malformed field analyses → Logs warning, continues processing
- Missing table names → Uses "unknown_table" as fallback

### 2. Performance Edge Cases  
- Large datasets (1000+ fields) → Virtual scrolling + pagination
- Memory constraints → Progressive loading and data chunking
- Network timeouts → Retry logic with exponential backoff

## Future Enhancement Opportunities

### 1. Advanced Analytics
- Time-series analysis for data sensitivity trends
- Machine learning insights on classification patterns
- Compliance risk scoring algorithms

### 2. Integration Enhancements
- Real-time database connectivity
- Integration with data cataloging tools
- API for external compliance systems

### 3. Visualization Improvements
- 3D visualization for complex data relationships
- Interactive data lineage graphs
- Custom dashboard builder for different user roles

## Development Guidelines

### 1. Adding New Visualizations
1. Create component in `/components/` directory
2. Add data processing logic in `dataProcessor.js`
3. Update main `SchemaVisualizer.jsx` to include component
4. Add tests and documentation

### 2. Modifying Data Processing
- All data transformations should go through `dataProcessor.js`
- Maintain backward compatibility with existing API responses
- Add input validation for new data structures

### 3. Performance Considerations
- Use React.memo() for expensive components
- Implement proper key props for list rendering
- Monitor bundle size impact of new dependencies

## Troubleshooting Common Issues

### 1. "0 sensitive fields found"
**Cause**: Classification mapping issue in `determineClassification()`
**Fix**: Verify backend classification values match expected mapping

### 2. "unknown_table" in heatmap
**Cause**: Table name extraction from field keys
**Fix**: Ensure field keys follow "table.column" format or provide table_name in analysis

### 3. Empty visualizations
**Cause**: Data aggregation failing due to unexpected data structure
**Fix**: Check console logs, verify field_analyses format matches expected schema

---

**Last Updated**: January 2025
**Version**: 1.0
**Maintained By**: PII Scanner Development Team