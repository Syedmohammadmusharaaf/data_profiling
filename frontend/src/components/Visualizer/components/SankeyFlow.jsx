/**
 * Sankey Flow Diagram Component
 * ============================
 * 
 * Shows data flows: Column → Table → Owner
 * Reveals relationships and cross-table data spread
 * 
 * @author PII Scanner Team
 * @version 1.0.0
 */

import React, { useMemo } from 'react'
import { motion } from 'framer-motion'
import { GitBranch, Database, Users, ArrowRight } from 'lucide-react'

const SankeyFlow = ({ data = [], onItemSelect, height = 400 }) => {
  // Helper functions defined first to avoid temporal dead zone
  const getClassificationColor = (classification) => {
    switch (classification) {
      case 'PHI': return '#ef4444' // red
      case 'PII': return '#f59e0b' // yellow
      case 'Unknown': return '#6b7280' // gray
      default: return '#3b82f6' // blue
    }
  }

  const getTableColor = (owner) => {
    // Generate consistent color based on owner
    if (!owner || owner === 'Unknown') return '#9ca3af'
    
    const colors = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444']
    const index = owner.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length
    return colors[index]
  }

  const getOwnerColor = (owner) => {
    return getTableColor(owner)
  }

  // Process data for Sankey-like visualization
  const flowData = useMemo(() => {
    if (!data || data.length === 0) return { nodes: [], links: [] }

    // Group data to create flows
    const columnTypes = {}
    const tableOwners = {}
    const ownerCounts = {}

    data.forEach(field => {
      // Column type classification
      const columnType = field.classification || 'Unknown'
      if (!columnTypes[columnType]) {
        columnTypes[columnType] = new Set()
      }
      columnTypes[columnType].add(field.table)

      // Table to owner mapping
      const owner = field.owner || 'Unknown'
      if (!tableOwners[field.table]) {
        tableOwners[field.table] = owner
      }

      // Owner field counts
      if (!ownerCounts[owner]) {
        ownerCounts[owner] = 0
      }
      ownerCounts[owner]++
    })

    // Create nodes
    const nodes = []
    let nodeId = 0

    // Level 1: Column Classifications
    const classificationNodes = {}
    Object.keys(columnTypes).forEach(classification => {
      const count = data.filter(f => (f.classification || 'Unknown') === classification).length
      const node = {
        id: nodeId++,
        name: classification,
        level: 1,
        type: 'classification',
        count: count,
        color: getClassificationColor(classification)
      }
      nodes.push(node)
      classificationNodes[classification] = node
    })

    // Level 2: Tables
    const tableNodes = {}
    const uniqueTables = [...new Set(data.map(f => f.table))]
    uniqueTables.forEach(table => {
      const tableData = data.filter(f => f.table === table)
      const count = tableData.length
      const owner = tableOwners[table]
      const node = {
        id: nodeId++,
        name: table,
        level: 2,
        type: 'table',
        count: count,
        owner: owner,
        color: getTableColor(owner)
      }
      nodes.push(node)
      tableNodes[table] = node
    })

    // Level 3: Owners
    const ownerNodes = {}
    Object.entries(ownerCounts).forEach(([owner, count]) => {
      const node = {
        id: nodeId++,
        name: owner,
        level: 3,
        type: 'owner',
        count: count,
        color: getOwnerColor(owner)
      }
      nodes.push(node)
      ownerNodes[owner] = node
    })

    // Create links
    const links = []
    let linkId = 0

    // Classification → Table links
    Object.entries(columnTypes).forEach(([classification, tables]) => {
      tables.forEach(table => {
        const count = data.filter(f => 
          (f.classification || 'Unknown') === classification && f.table === table
        ).length
        
        links.push({
          id: linkId++,
          source: classificationNodes[classification].id,
          target: tableNodes[table].id,
          value: count,
          type: 'classification-table'
        })
      })
    })

    // Table → Owner links
    uniqueTables.forEach(table => {
      const owner = tableOwners[table]
      const count = data.filter(f => f.table === table).length
      
      links.push({
        id: linkId++,
        source: tableNodes[table].id,
        target: ownerNodes[owner].id,
        value: count,
        type: 'table-owner'
      })
    })

    return { nodes, links }
  }, [data])

  const handleNodeClick = (node) => {
    if (onItemSelect) {
      onItemSelect({
        type: node.type,
        name: node.name,
        count: node.count,
        level: node.level
      })
    }
  }

  if (flowData.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        <div className="text-center">
          <GitBranch className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No data available for flow analysis</p>
        </div>
      </div>
    )
  }

  // Group nodes by level for positioning
  const nodesByLevel = {
    1: flowData.nodes.filter(n => n.level === 1),
    2: flowData.nodes.filter(n => n.level === 2),
    3: flowData.nodes.filter(n => n.level === 3)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900">Data Flow Analysis</h3>
        <p className="text-sm text-gray-600">
          Relationships between classifications, tables, and data owners
        </p>
      </div>

      {/* Flow Visualization */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-red-500 rounded"></div>
              <span className="text-sm text-gray-600">PHI</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-yellow-500 rounded"></div>
              <span className="text-sm text-gray-600">PII</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gray-500 rounded"></div>
              <span className="text-sm text-gray-600">Non-sensitive</span>
            </div>
          </div>
        </div>

        {/* Simplified Flow Representation */}
        <div className="space-y-8">
          {/* Level Headers */}
          <div className="grid grid-cols-3 gap-8 text-center">
            <div className="flex items-center justify-center space-x-2">
              <Database className="w-5 h-5 text-blue-600" />
              <h4 className="font-semibold text-gray-900">Classifications</h4>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <Database className="w-5 h-5 text-green-600" />
              <h4 className="font-semibold text-gray-900">Tables</h4>
            </div>
            <div className="flex items-center justify-center space-x-2">
              <Users className="w-5 h-5 text-purple-600" />
              <h4 className="font-semibold text-gray-900">Owners</h4>
            </div>
          </div>

          {/* Flow Content */}
          <div className="grid grid-cols-3 gap-8">
            {/* Level 1: Classifications */}
            <div className="space-y-3">
              {nodesByLevel[1]
                .sort((a, b) => b.count - a.count)
                .map((node, index) => (
                  <motion.div
                    key={node.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => handleNodeClick(node)}
                  >
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: node.color }}
                      />
                      <span className="font-medium text-gray-900">{node.name}</span>
                    </div>
                    <div className="text-sm text-gray-600">{node.count}</div>
                  </motion.div>
                ))}
            </div>

            {/* Level 2: Tables */}
            <div className="space-y-3">
              {nodesByLevel[2]
                .sort((a, b) => b.count - a.count)
                .slice(0, 10) // Limit to top 10 for display
                .map((node, index) => (
                  <motion.div
                    key={node.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => handleNodeClick(node)}
                  >
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: node.color }}
                      />
                      <div>
                        <div className="font-medium text-gray-900 truncate" title={node.name}>
                          {node.name.length > 20 ? node.name.substring(0, 17) + '...' : node.name}
                        </div>
                        <div className="text-xs text-gray-500">{node.owner}</div>
                      </div>
                    </div>
                    <div className="text-sm text-gray-600">{node.count}</div>
                  </motion.div>
                ))}
              {nodesByLevel[2].length > 10 && (
                <div className="text-center text-sm text-gray-500 py-2">
                  +{nodesByLevel[2].length - 10} more tables
                </div>
              )}
            </div>

            {/* Level 3: Owners */}
            <div className="space-y-3">
              {nodesByLevel[3]
                .sort((a, b) => b.count - a.count)
                .map((node, index) => (
                  <motion.div
                    key={node.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => handleNodeClick(node)}
                  >
                    <div className="flex items-center space-x-3">
                      <div 
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: node.color }}
                      />
                      <span className="font-medium text-gray-900 truncate" title={node.name}>
                        {node.name === 'Unknown' ? 'Unknown Owner' : node.name}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">{node.count}</div>
                  </motion.div>
                ))}
            </div>
          </div>

          {/* Flow Arrows */}
          <div className="grid grid-cols-2 gap-8">
            <div className="flex items-center justify-center">
              <ArrowRight className="w-6 h-6 text-gray-400" />
            </div>
            <div className="flex items-center justify-center">
              <ArrowRight className="w-6 h-6 text-gray-400" />
            </div>
          </div>
        </div>
      </div>

      {/* Flow Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Database className="w-5 h-5 text-blue-600" />
            <h5 className="font-semibold text-blue-900">Classifications</h5>
          </div>
          <div className="text-2xl font-bold text-blue-600 mb-1">
            {nodesByLevel[1].length}
          </div>
          <div className="text-sm text-blue-700">
            Data sensitivity types identified
          </div>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Database className="w-5 h-5 text-green-600" />
            <h5 className="font-semibold text-green-900">Tables</h5>
          </div>
          <div className="text-2xl font-bold text-green-600 mb-1">
            {nodesByLevel[2].length}
          </div>
          <div className="text-sm text-green-700">
            Database tables containing sensitive data
          </div>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Users className="w-5 h-5 text-purple-600" />
            <h5 className="font-semibold text-purple-900">Data Owners</h5>
          </div>
          <div className="text-2xl font-bold text-purple-600 mb-1">
            {nodesByLevel[3].length}
          </div>
          <div className="text-sm text-purple-700">
            Responsible parties for data governance
          </div>
        </div>
      </div>

      {/* Insights */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Flow Insights</h4>
        
        <div className="space-y-3">
          {nodesByLevel[3].find(n => n.name === 'Unknown') && (
            <div className="flex items-start space-x-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <Users className="w-5 h-5 text-yellow-600 mt-0.5" />
              <div>
                <div className="font-medium text-yellow-900">Unassigned Ownership</div>
                <div className="text-sm text-yellow-700 mt-1">
                  {nodesByLevel[3].find(n => n.name === 'Unknown')?.count || 0} fields have no assigned data owner. 
                  Consider assigning ownership for better governance.
                </div>
              </div>
            </div>
          )}

          {nodesByLevel[1].find(n => n.name === 'PHI') && (
            <div className="flex items-start space-x-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <Database className="w-5 h-5 text-red-600 mt-0.5" />
              <div>
                <div className="font-medium text-red-900">PHI Data Detected</div>
                <div className="text-sm text-red-700 mt-1">
                  {nodesByLevel[1].find(n => n.name === 'PHI')?.count || 0} PHI fields identified. 
                  Ensure HIPAA compliance measures are in place.
                </div>
              </div>
            </div>
          )}

          <div className="text-sm text-gray-600">
            <strong>Recommendation:</strong> Review the data flow to ensure proper access controls 
            and data governance policies are applied at each level.
          </div>
        </div>
      </div>
    </div>
  )
}

export default SankeyFlow