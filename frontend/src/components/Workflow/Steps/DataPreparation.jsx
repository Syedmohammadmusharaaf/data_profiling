import React, { useState, useCallback, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import { 
  Upload, 
  File, 
  CheckCircle, 
  AlertTriangle, 
  ArrowRight,
  Database, 
  FileText, 
  Server,
  Key,
  Globe,
  Settings
} from 'lucide-react'
import toast from 'react-hot-toast'
import { workflowApi, apiUtils } from '../../../services/api'
import { useLogger } from '../../../utils/logger'

const DataPreparation = ({ 
  sessionId, 
  setSessionId, 
  workflowData, 
  updateWorkflowData, 
  nextStep, 
  isLoading, 
  setIsLoading 
}) => {
  const [uploadStatus, setUploadStatus] = useState('idle') // idle, uploading, success, error
  const [extractStatus, setExtractStatus] = useState('idle')
  const [selectedTables, setSelectedTables] = useState([])
  const [dataSource, setDataSource] = useState('file') // 'file' or 'database'
  const [dbConnection, setDbConnection] = useState({
    type: 'mysql',
    host: '',
    port: '',
    database: '',
    username: '',
    password: '',
    ssl: false
  })
  const [connectionStatus, setConnectionStatus] = useState('idle') // idle, testing, success, error

  // Enhanced logging
  const dataPreparationLogger = useLogger('DataPreparation')
  
  useEffect(() => {
    dataPreparationLogger.logMount()
    dataPreparationLogger.info('DataPreparation component initialized', {
      sessionId,
      dataSource,
      uploadStatus,
      extractStatus,
      selectedTablesCount: selectedTables.length
    })
    
    return () => {
      dataPreparationLogger.logUnmount()
    }
  }, [dataPreparationLogger, sessionId, dataSource, uploadStatus, extractStatus, selectedTables.length])

  // Database types supported
  const dbTypes = [
    { value: 'mysql', label: 'MySQL', port: '3306', icon: '🐬' },
    { value: 'postgresql', label: 'PostgreSQL', port: '5432', icon: '🐘' },
    { value: 'sqlserver', label: 'SQL Server', port: '1433', icon: '🏢' },
    { value: 'oracle', label: 'Oracle', port: '1521', icon: '🔴' },
    { value: 'sqlite', label: 'SQLite', port: '', icon: '📁' },
    { value: 'mongodb', label: 'MongoDB', port: '27017', icon: '🍃' },
    { value: 'snowflake', label: 'Snowflake', port: '', icon: '❄️' },
    { value: 'redshift', label: 'Amazon Redshift', port: '5439', icon: '🟠' }
  ]

  // File upload handler (existing functionality)
  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return

    dataPreparationLogger.info('File upload initiated', {
      fileName: file.name,
      fileSize: file.size,
      fileType: file.type,
      lastModified: file.lastModified
    })

    // Validate file type
    if (!apiUtils.validateFileType(file)) {
      dataPreparationLogger.warn('Invalid file type uploaded', {
        fileName: file.name,
        fileType: file.type
      })
      toast.error('Invalid file type. Please upload DDL, SQL, JSON, CSV, or Excel files.')
      return
    }

    setIsLoading(true)
    setUploadStatus('uploading')

    try {
      // Upload file
      const fileType = file.name.split('.').pop().toLowerCase()
      const uploadResult = await workflowApi.uploadSchema(file, fileType)
      
      setSessionId(uploadResult.session_id)
      updateWorkflowData('fileInfo', {
        name: uploadResult.file_name,
        size: uploadResult.file_size,
        type: uploadResult.file_type,
        sessionId: uploadResult.session_id,
        source: 'file'
      })
      
      setUploadStatus('success')
      toast.success('File uploaded successfully!')

      // Immediately extract schema (no delay to prevent state issues)
      console.log('Starting schema extraction for session:', uploadResult.session_id)
      await extractSchema(uploadResult.session_id)

    } catch (error) {
      console.error('Upload error:', error)
      setUploadStatus('error')
      toast.error(error.message || 'Upload failed')
    } finally {
      setIsLoading(false)
    }
  }, [setSessionId, updateWorkflowData, setIsLoading])

  // Database connection handler
  const handleDatabaseConnect = async () => {
    setIsLoading(true)
    setConnectionStatus('testing')
    
    try {
      // Test database connection and extract schema
      const connectionResult = await workflowApi.connectDatabase(dbConnection)
      
      setSessionId(connectionResult.session_id)
      updateWorkflowData('fileInfo', {
        name: `${dbConnection.type}://${dbConnection.host}:${dbConnection.port}/${dbConnection.database}`,
        type: 'database',
        sessionId: connectionResult.session_id,
        source: 'database',
        connectionDetails: {
          type: dbConnection.type,
          host: dbConnection.host,
          database: dbConnection.database
        }
      })
      
      // Auto-extract schema from database
      if (connectionResult.schema_data) {
        updateWorkflowData('schemaData', {
          tables: connectionResult.tables,
          totalTables: connectionResult.total_tables,
          totalColumns: connectionResult.total_columns
        })
        
        setExtractStatus('success')
        setConnectionStatus('success')
        toast.success(`Connected successfully: ${connectionResult.total_tables} tables, ${connectionResult.total_columns} columns`)
      }
      
    } catch (error) {
      setConnectionStatus('error')
      toast.error(error.message || 'Database connection failed')
    } finally {
      setIsLoading(false)
    }
  }

  // Schema extraction handler (for file uploads) with enhanced error handling
  const extractSchema = async (currentSessionId = sessionId) => {
    if (!currentSessionId) {
      console.error('No session ID provided for schema extraction')
      return
    }

    console.log('Extracting schema for session:', currentSessionId)
    setExtractStatus('extracting')
    setIsLoading(true)

    try {
      const result = await workflowApi.extractSchema(currentSessionId)
      console.log('Schema extraction result:', result)
      
      // Validate the result structure
      if (!result || !result.tables) {
        throw new Error('Invalid schema extraction result - missing tables data')
      }

      const schemaData = {
        tables: result.tables,
        totalTables: result.total_tables || Object.keys(result.tables).length,
        totalColumns: result.total_columns || Object.values(result.tables).reduce((acc, table) => acc + (table?.length || 0), 0)
      }
      
      console.log('Processed schema data:', schemaData)
      
      updateWorkflowData('schemaData', schemaData)
      
      setExtractStatus('success')
      toast.success(`Schema extracted: ${schemaData.totalTables} tables, ${schemaData.totalColumns} columns`)

      // Auto-select all tables to improve workflow UX
      const allTableNames = Object.keys(schemaData.tables)
      setSelectedTables(allTableNames)
      updateWorkflowData('selectedTables', allTableNames)
      
      // Show info toast about auto-selection
      setTimeout(() => {
        toast.success(`All ${allTableNames.length} tables automatically selected for analysis`)
      }, 1000)

    } catch (error) {
      console.error('Schema extraction error:', error)
      setExtractStatus('error')
      toast.error(error.message || 'Schema extraction failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleTableSelection = (tableName) => {
    setSelectedTables(prev => {
      if (prev.includes(tableName)) {
        return prev.filter(t => t !== tableName)
      } else {
        return [...prev, tableName]
      }
    })
  }

  const handleNext = () => {
    if (selectedTables.length === 0) {
      toast.error('Please select at least one table for profiling')
      return
    }

    updateWorkflowData('selectedTables', selectedTables)
    nextStep({ selectedTables })
  }

  const handleDbTypeChange = (type) => {
    const dbType = dbTypes.find(db => db.value === type)
    setDbConnection(prev => ({
      ...prev,
      type,
      port: dbType?.port || prev.port
    }))
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.ddl', '.sql'],
      'application/json': ['.json'],
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    maxFiles: 1,
    disabled: isLoading
  })

  const isSchemaReady = (uploadStatus === 'success' || connectionStatus === 'success') && 
                      (extractStatus === 'success') && 
                      workflowData.schemaData

  return (
    <div id="data-preparation-container" className="space-y-8">
      {/* Step Title */}
      <div id="data-preparation-header" className="text-center">
        <h2 id="data-preparation-title" className="text-2xl font-bold text-gray-900 mb-2">
          Data Preparation
        </h2>
        <p id="data-preparation-description" className="text-gray-600">
          Choose your data source: upload a schema file or connect directly to your database
        </p>
      </div>

      {/* Data Source Selection */}
      <motion.div
        className="flex justify-center space-x-4 mb-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <button
          onClick={() => setDataSource('file')}
          className={`px-6 py-3 rounded-lg border-2 transition-all duration-200 ${
            dataSource === 'file'
              ? 'border-blue-500 bg-blue-50 text-blue-700'
              : 'border-gray-300 text-gray-600 hover:border-gray-400'
          }`}
          disabled={isLoading}
        >
          <div className="flex items-center space-x-2">
            <File className="w-5 h-5" />
            <span className="font-medium">Upload Schema File</span>
          </div>
        </button>
        
        <button
          onClick={() => setDataSource('database')}
          className={`px-6 py-3 rounded-lg border-2 transition-all duration-200 ${
            dataSource === 'database'
              ? 'border-blue-500 bg-blue-50 text-blue-700'
              : 'border-gray-300 text-gray-600 hover:border-gray-400'
          }`}
          disabled={isLoading}
        >
          <div className="flex items-center space-x-2">
            <Database className="w-5 h-5" />
            <span className="font-medium">Connect to Database</span>
          </div>
        </button>
      </motion.div>

      {/* File Upload Section */}
      {dataSource === 'file' && (
        <motion.div
          id="upload-step-container"
          className="space-y-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div id="upload-step-header" className="flex items-center space-x-2">
            <div 
              id="upload-step-icon"
              className={`w-8 h-8 rounded-full flex items-center justify-center ${
                uploadStatus === 'success' ? 'bg-green-100 text-green-600' : 'bg-blue-100 text-blue-600'
              }`}
            >
              {uploadStatus === 'success' ? <CheckCircle className="w-5 h-5" /> : <span>1</span>}
            </div>
            <h3 id="upload-step-title" className="text-lg font-semibold text-gray-900">Upload Schema File</h3>
          </div>

          <div
            id="file-drop-zone"
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200 cursor-pointer ${
              isDragActive 
                ? 'border-blue-500 bg-blue-50' 
                : uploadStatus === 'success'
                ? 'border-green-500 bg-green-50'
                : uploadStatus === 'error'
                ? 'border-red-500 bg-red-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input id="file-input" {...getInputProps()} />
            
            <div className="space-y-4">
              {uploadStatus === 'uploading' ? (
                <div id="upload-spinner" className="animate-spin mx-auto w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full"></div>
              ) : uploadStatus === 'success' ? (
                <CheckCircle id="upload-success-icon" className="mx-auto w-16 h-16 text-green-500" />
              ) : uploadStatus === 'error' ? (
                <AlertTriangle id="upload-error-icon" className="mx-auto w-16 h-16 text-red-500" />
              ) : (
                <Upload id="upload-default-icon" className="mx-auto w-16 h-16 text-gray-400" />
              )}
              
              <div id="upload-status-content">
                {uploadStatus === 'uploading' && (
                  <p id="upload-loading-text" className="text-lg font-medium text-blue-600">Uploading file...</p>
                )}
                {uploadStatus === 'success' && workflowData.fileInfo && (
                  <div id="upload-success-content" className="space-y-2">
                    <p id="upload-success-text" className="text-lg font-medium text-green-600">File uploaded successfully!</p>
                    <div id="file-info" className="text-sm text-gray-600">
                      <p id="file-name"><strong>File:</strong> {workflowData.fileInfo.name}</p>
                      <p id="file-size"><strong>Size:</strong> {apiUtils.formatFileSize(workflowData.fileInfo.size)}</p>
                      <p id="file-type"><strong>Type:</strong> {workflowData.fileInfo.type?.toUpperCase() || 'Unknown'}</p>
                    </div>
                  </div>
                )}
                {uploadStatus === 'error' && (
                  <div id="upload-error-content" className="space-y-2">
                    <p id="upload-error-text" className="text-lg font-medium text-red-600">Upload failed</p>
                    <p id="upload-error-help" className="text-sm text-gray-600">Please try again with a valid file</p>
                  </div>
                )}
                {uploadStatus === 'idle' && (
                  <div id="upload-idle-content" className="space-y-2">
                    <p id="upload-idle-text" className="text-lg font-medium text-gray-900">
                      {isDragActive ? 'Drop your file here' : 'Drag & drop your schema file here'}
                    </p>
                    <p id="upload-browse-text" className="text-gray-600">or click to browse files</p>
                    <p id="upload-formats-text" className="text-sm text-gray-500">
                      Supports: DDL, SQL, JSON, CSV, Excel files
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Database Connection Section */}
      {dataSource === 'database' && (
        <motion.div
          id="database-connection-container"
          className="space-y-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div id="database-step-header" className="flex items-center space-x-2">
            <div 
              id="database-step-icon"
              className={`w-8 h-8 rounded-full flex items-center justify-center ${
                connectionStatus === 'success' ? 'bg-green-100 text-green-600' : 'bg-blue-100 text-blue-600'
              }`}
            >
              {connectionStatus === 'success' ? <CheckCircle className="w-5 h-5" /> : <span>1</span>}
            </div>
            <h3 id="database-step-title" className="text-lg font-semibold text-gray-900">Connect to Database</h3>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6">
            {/* Database Type Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">Database Type</label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {dbTypes.map((db) => (
                  <button
                    key={db.value}
                    onClick={() => handleDbTypeChange(db.value)}
                    className={`p-3 border rounded-lg text-left transition-all duration-200 ${
                      dbConnection.type === db.value
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    disabled={isLoading}
                  >
                    <div className="flex items-center space-x-2">
                      <span className="text-lg">{db.icon}</span>
                      <span className="text-sm font-medium">{db.label}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Connection Details Form */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Server className="inline w-4 h-4 mr-1" />
                  Host/Server
                </label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="localhost or server.example.com"
                  value={dbConnection.host}
                  onChange={(e) => setDbConnection(prev => ({ ...prev, host: e.target.value }))}
                  disabled={isLoading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Globe className="inline w-4 h-4 mr-1" />
                  Port
                </label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Default port"
                  value={dbConnection.port}
                  onChange={(e) => setDbConnection(prev => ({ ...prev, port: e.target.value }))}
                  disabled={isLoading || dbConnection.type === 'sqlite'}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Database className="inline w-4 h-4 mr-1" />
                  Database Name
                </label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="database_name"
                  value={dbConnection.database}
                  onChange={(e) => setDbConnection(prev => ({ ...prev, database: e.target.value }))}
                  disabled={isLoading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Key className="inline w-4 h-4 mr-1" />
                  Username
                </label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="username"
                  value={dbConnection.username}
                  onChange={(e) => setDbConnection(prev => ({ ...prev, username: e.target.value }))}
                  disabled={isLoading}
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Key className="inline w-4 h-4 mr-1" />
                  Password
                </label>
                <input
                  type="password"
                  className="form-input"
                  placeholder="password"
                  value={dbConnection.password}
                  onChange={(e) => setDbConnection(prev => ({ ...prev, password: e.target.value }))}
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* SSL Option */}
            <div className="mb-6">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={dbConnection.ssl}
                  onChange={(e) => setDbConnection(prev => ({ ...prev, ssl: e.target.checked }))}
                  className="form-checkbox"
                  disabled={isLoading}
                />
                <span className="text-sm text-gray-700">Use SSL/TLS connection</span>
              </label>
            </div>

            {/* Connection Status */}
            {connectionStatus === 'testing' && (
              <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                  <span className="text-blue-700 text-sm">Testing connection...</span>
                </div>
              </div>
            )}

            {connectionStatus === 'success' && workflowData.fileInfo && (
              <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span className="text-green-700 text-sm">Connected successfully!</span>
                </div>
                <div className="mt-2 text-xs text-green-600">
                  <p><strong>Connection:</strong> {workflowData.fileInfo.name}</p>
                </div>
              </div>
            )}

            {connectionStatus === 'error' && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-red-500" />
                  <span className="text-red-700 text-sm">Connection failed. Please check your credentials.</span>
                </div>
              </div>
            )}

            {/* Connect Button */}
            <button
              onClick={handleDatabaseConnect}
              className="btn-primary w-full flex items-center justify-center space-x-2"
              disabled={isLoading || !dbConnection.host || !dbConnection.database}
            >
              {connectionStatus === 'testing' ? (
                <>
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
                  <span>Testing Connection...</span>
                </>
              ) : (
                <>
                  <Database className="w-4 h-4" />
                  <span>Connect & Extract Schema</span>
                </>
              )}
            </button>
          </div>
        </motion.div>
      )}

      {/* Schema Statistics (shown for both sources) */}
      {isSchemaReady && (
        <motion.div
          id="schema-stats"
          className="grid grid-cols-3 gap-4 mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div id="tables-stat" className="bg-blue-50 p-4 rounded-lg text-center">
            <Database className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-blue-600">
              {workflowData.schemaData.totalTables}
            </div>
            <div className="text-sm text-gray-600">Tables</div>
          </div>
          <div id="columns-stat" className="bg-green-50 p-4 rounded-lg text-center">
            <FileText className="w-8 h-8 text-green-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-green-600">
              {workflowData.schemaData.totalColumns}
            </div>
            <div className="text-sm text-gray-600">Columns</div>
          </div>
          <div id="selected-stat" className="bg-purple-50 p-4 rounded-lg text-center">
            <CheckCircle className="w-8 h-8 text-purple-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-purple-600">
              {selectedTables.length}
            </div>
            <div className="text-sm text-gray-600">Selected</div>
          </div>
        </motion.div>
      )}

      {/* Table Selection (shown for both sources) */}
      {isSchemaReady && (
        <motion.div
          id="table-selection-container"
          className="space-y-4 w-full"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <div id="table-selection-header" className="flex items-center space-x-2 sticky top-0 bg-white z-10 pb-4">
            <div id="table-selection-icon" className="w-8 h-8 rounded-full flex items-center justify-center bg-blue-100 text-blue-600">
              <span>2</span>
            </div>
            <h3 id="table-selection-title" className="text-lg font-semibold text-gray-900">
              Select Tables for PII/PHI Analysis
            </h3>
          </div>

          {/* Scrollable Tables Container with improved viewport usage */}
          <div 
            id="tables-scroll-container" 
            className="max-h-[60vh] overflow-y-auto overflow-x-hidden border rounded-lg bg-gray-50 p-4"
            style={{
              scrollbarWidth: 'thin',
              scrollbarColor: '#CBD5E1 #F1F5F9'
            }}
          >
            <style dangerouslySetInnerHTML={{__html: `
              #tables-scroll-container::-webkit-scrollbar {
                width: 8px;
              }
              #tables-scroll-container::-webkit-scrollbar-track {
                background: #f1f5f9;
                border-radius: 4px;
              }
              #tables-scroll-container::-webkit-scrollbar-thumb {
                background: #cbd5e1;
                border-radius: 4px;
              }
              #tables-scroll-container::-webkit-scrollbar-thumb:hover {
                background: #94a3b8;
              }
            `}} />
            
            <div id="tables-grid" className="grid grid-cols-1 xl:grid-cols-4 lg:grid-cols-3 md:grid-cols-2 gap-4 pr-2">
              {Object.entries(workflowData.schemaData.tables).map(([tableName, columns]) => (
                <motion.div
                  key={tableName}
                  id={`table-card-${tableName}`}
                  className={`border rounded-lg p-4 cursor-pointer transition-all duration-200 bg-white shadow-sm ${
                    selectedTables.includes(tableName)
                      ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200 shadow-md'
                      : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
                  }`}
                  onClick={() => handleTableSelection(tableName)}
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h4 id={`table-name-${tableName}`} className="font-medium text-gray-900 truncate" title={tableName}>
                        {tableName}
                      </h4>
                      <p id={`table-columns-${tableName}`} className="text-sm text-gray-600 mt-1">
                        {columns.length} columns
                      </p>
                    </div>
                    <div 
                      id={`table-checkbox-${tableName}`}
                      className={`w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 ml-2 ${
                        selectedTables.includes(tableName)
                          ? 'bg-blue-500 border-blue-500'
                          : 'border-gray-300'
                      }`}
                    >
                      {selectedTables.includes(tableName) && (
                        <CheckCircle className="w-3 h-3 text-white" />
                      )}
                    </div>
                  </div>
                  
                  {/* Show first few columns as preview */}
                  <div id={`table-preview-${tableName}`} className="mt-3 pt-3 border-t border-gray-200">
                    <div className="text-xs text-gray-500 line-clamp-2">
                      {columns.slice(0, 4).map(col => col.column_name || col.name).join(', ')}
                      {columns.length > 4 && ` +${columns.length - 4} more`}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Actions - Sticky at bottom with better desktop layout */}
          <div id="table-selection-actions" className="flex flex-col sm:flex-row justify-between items-center pt-6 border-t bg-white sticky bottom-0 z-10 space-y-4 sm:space-y-0">
            <div id="table-selection-info" className="text-sm text-gray-600 font-medium">
              {selectedTables.length} of {Object.keys(workflowData.schemaData.tables).length} tables selected
              {selectedTables.length > 0 && (
                <span className="text-blue-600 ml-2">
                  ({Object.values(workflowData.schemaData.tables)
                    .filter((_, index) => selectedTables.includes(Object.keys(workflowData.schemaData.tables)[index]))
                    .reduce((total, columns) => total + columns.length, 0)} total columns)
                </span>
              )}
            </div>
            
            <div className="flex space-x-3">
              <button
                id="select-all-tables-btn"
                onClick={() => setSelectedTables(Object.keys(workflowData.schemaData.tables))}
                className="btn-secondary min-w-[100px] py-2 px-4 text-sm font-medium"
                disabled={isLoading}
                title="Select all available tables"
              >
                Select All
              </button>
              <button
                id="clear-all-tables-btn"
                onClick={() => setSelectedTables([])}
                className="btn-secondary min-w-[100px] py-2 px-4 text-sm font-medium"
                disabled={isLoading}
                title="Clear all selected tables"
              >
                Clear All
              </button>
              <button
                id="continue-to-profiling-btn"
                onClick={handleNext}
                className="btn-primary min-w-[150px] py-2 px-6 text-sm font-medium shadow-lg hover:shadow-xl transition-shadow"
                disabled={isLoading || selectedTables.length === 0}
                title={selectedTables.length === 0 ? "Please select at least one table" : "Continue to next step"}
              >
                Continue to Profiling
                <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}

export default DataPreparation