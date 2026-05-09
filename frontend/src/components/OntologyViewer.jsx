import { useState, useEffect, useRef } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import { Network, ThumbsUp, MessageSquare, ZoomIn, ZoomOut, Maximize2, Info, Minimize2, X } from 'lucide-react'
import toast from 'react-hot-toast'
import './OntologyViewer.css'

function OntologyViewer({ ontologyData, onRequestFeedback, onConfirm }) {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] })
  const [selectedNode, setSelectedNode] = useState(null)
  const [showDetails, setShowDetails] = useState(false)
  const [highlightNodes, setHighlightNodes] = useState(new Set())
  const [highlightLinks, setHighlightLinks] = useState(new Set())
  const [isFullscreen, setIsFullscreen] = useState(false)
  const graphRef = useRef()

  useEffect(() => {
    if (ontologyData) {
      transformOntologyToGraph(ontologyData)
    }
  }, [ontologyData])

  const transformOntologyToGraph = (data) => {
    console.log('Transforming ontology data:', data)
    
    const nodes = []
    const links = []
    const nodeMap = new Map()

    // Check if data has entities
    if (!data.entities || data.entities.length === 0) {
      console.warn('No entities found in ontology data')
      toast.error('No entities found in the ontology. Please try regenerating.')
      setGraphData({ nodes: [], links: [] })
      return
    }

    // Create nodes from entities
    data.entities.forEach((entity) => {
      const node = {
        id: entity.name,
        name: entity.name,
        type: entity.type,
        description: entity.description,
        properties: entity.properties,
        val: 15 + (entity.properties?.length || 0) * 2,
        color: getColorByType(entity.type)
      }
      nodes.push(node)
      nodeMap.set(entity.name, node)
    })

    // Create links from relationships
    if (data.relationships && data.relationships.length > 0) {
      data.relationships.forEach((rel) => {
        if (nodeMap.has(rel.source) && nodeMap.has(rel.target)) {
          links.push({
            source: rel.source,
            target: rel.target,
            name: rel.name,
            type: rel.type,
            description: rel.description,
            properties: rel.properties,
            color: '#94a3b8',
            width: 2
          })
        }
      })
    }

    console.log(`Graph created: ${nodes.length} nodes, ${links.length} links`)
    setGraphData({ nodes, links })
  }

  const getColorByType = (type) => {
    const colors = {
      'concept': '#667eea',
      'entity': '#10b981',
      'attribute': '#f59e0b',
      'relationship': '#ef4444',
      'process': '#8b5cf6',
      'event': '#ec4899'
    }
    return colors[type] || '#6b7280'
  }

  const handleNodeClick = (node) => {
    setSelectedNode(node)
    setShowDetails(true)
    
    // Highlight connected nodes and links
    const connectedNodes = new Set()
    const connectedLinks = new Set()
    
    connectedNodes.add(node.id)
    
    graphData.links.forEach(link => {
      if (link.source.id === node.id || link.target.id === node.id) {
        connectedLinks.add(link)
        connectedNodes.add(link.source.id)
        connectedNodes.add(link.target.id)
      }
    })
    
    setHighlightNodes(connectedNodes)
    setHighlightLinks(connectedLinks)
  }
  
  const handleBackgroundClick = () => {
    setHighlightNodes(new Set())
    setHighlightLinks(new Set())
    setShowDetails(false)
    setSelectedNode(null)
  }

  const handleZoomIn = () => {
    if (graphRef.current) {
      graphRef.current.zoom(graphRef.current.zoom() * 1.2, 400)
    }
  }

  const handleZoomOut = () => {
    if (graphRef.current) {
      graphRef.current.zoom(graphRef.current.zoom() * 0.8, 400)
    }
  }

  const handleFitView = () => {
    if (graphRef.current) {
      graphRef.current.zoomToFit(400, 50)
    }
  }
  
  const handleCenterGraph = () => {
    if (graphRef.current) {
      graphRef.current.centerAt(0, 0, 1000)
      graphRef.current.zoom(1, 1000)
    }
  }
  
  const handleSpreadNodes = () => {
    // Restart the simulation with stronger repulsion
    if (graphRef.current) {
      const fg = graphRef.current
      fg.d3Force('charge').strength(-600)
      fg.d3Force('link').distance(150)
      fg.d3ReheatSimulation()
      
      // Auto-fit after spreading
      setTimeout(() => {
        fg.zoomToFit(400, 80)
      }, 2000)
      
      toast.success('Spreading nodes - will auto-fit in 2 seconds')
    }
  }
  
  const handleCompactNodes = () => {
    // Restart the simulation with weaker repulsion
    if (graphRef.current) {
      const fg = graphRef.current
      fg.d3Force('charge').strength(-200)
      fg.d3Force('link').distance(80)
      fg.d3ReheatSimulation()
      
      // Auto-fit after compacting
      setTimeout(() => {
        fg.zoomToFit(400, 80)
      }, 2000)
      
      toast.success('Compacting nodes - will auto-fit in 2 seconds')
    }
  }
  
  const handleResetLayout = () => {
    // Reset to default forces
    if (graphRef.current) {
      const fg = graphRef.current
      fg.d3Force('charge').strength(-400)
      fg.d3Force('link').distance(120)
      fg.d3ReheatSimulation()
      
      setTimeout(() => {
        fg.zoomToFit(400, 80)
      }, 2000)
      
      toast.success('Resetting layout - will auto-fit in 2 seconds')
    }
  }

  const handleConfirm = async () => {
    toast.success('Ontology confirmed and saved!')
    onConfirm()
  }

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
    // Re-fit graph after fullscreen toggle
    setTimeout(() => {
      if (graphRef.current) {
        graphRef.current.zoomToFit(400, 80)
      }
    }, 100)
  }

  const renderControls = () => (
    <div className="header-actions">
      <button className="btn-icon" onClick={handleSpreadNodes} title="Spread Nodes Apart">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M8 3L4 7l4 4M16 3l4 4-4 4M3 16l4 4 4-4M21 16l-4 4-4-4"/>
        </svg>
      </button>
      <button className="btn-icon" onClick={handleCompactNodes} title="Compact Nodes">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M4 8l4-4 4 4M4 16l4 4 4 4M16 8l4-4 4 4M16 16l4 4 4 4"/>
        </svg>
      </button>
      <button className="btn-icon" onClick={handleResetLayout} title="Reset Layout">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
          <path d="M21 3v5h-5"/>
          <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
          <path d="M3 21v-5h5"/>
        </svg>
      </button>
      <button className="btn-icon" onClick={handleZoomIn} title="Zoom In">
        <ZoomIn size={20} />
      </button>
      <button className="btn-icon" onClick={handleZoomOut} title="Zoom Out">
        <ZoomOut size={20} />
      </button>
      <button className="btn-icon" onClick={handleCenterGraph} title="Center Graph">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="12" cy="12" r="3"/>
          <circle cx="12" cy="12" r="10"/>
        </svg>
      </button>
      <button className="btn-icon" onClick={handleFitView} title="Fit View">
        <Maximize2 size={20} />
      </button>
      {!isFullscreen && (
        <button className="btn-icon" onClick={toggleFullscreen} title="Fullscreen View">
          <Maximize2 size={20} />
        </button>
      )}
    </div>
  )

  const renderGraph = (height) => (
    <ForceGraph2D
      ref={graphRef}
      graphData={graphData}
      width={isFullscreen ? window.innerWidth : undefined}
      height={height}
      nodeLabel="name"
      nodeColor={node => highlightNodes.size === 0 || highlightNodes.has(node.id) ? node.color : '#e5e7eb'}
      nodeVal="val"
      nodeCanvasObject={(node, ctx, globalScale) => {
        const label = node.name
        const fontSize = 14 / globalScale
        const isHighlighted = highlightNodes.size === 0 || highlightNodes.has(node.id)
        const isSelected = selectedNode && selectedNode.id === node.id
        
        ctx.font = `bold ${fontSize}px Sans-Serif`
        
        // Draw node circle with highlighting
        ctx.beginPath()
        ctx.arc(node.x, node.y, node.val, 0, 2 * Math.PI, false)
        ctx.fillStyle = isHighlighted ? node.color : '#e5e7eb'
        ctx.fill()
        
        // Thicker border for selected node
        ctx.strokeStyle = isSelected ? '#fbbf24' : '#fff'
        ctx.lineWidth = isSelected ? 5 / globalScale : 3 / globalScale
        ctx.stroke()
        
        // Draw label with background for better readability
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        const textY = node.y + node.val + 12 / globalScale
        
        // Background for text
        const textWidth = ctx.measureText(label).width
        ctx.fillStyle = isHighlighted ? 'rgba(255, 255, 255, 0.95)' : 'rgba(229, 231, 235, 0.8)'
        ctx.fillRect(node.x - textWidth/2 - 4, textY - fontSize/2 - 2, textWidth + 8, fontSize + 4)
        
        // Text
        ctx.fillStyle = isHighlighted ? '#1f2937' : '#9ca3af'
        ctx.fillText(label, node.x, textY)
      }}
      linkLabel="name"
      linkColor={link => {
        if (highlightLinks.size === 0) return link.color
        return highlightLinks.has(link) ? '#3b82f6' : '#e5e7eb'
      }}
      linkWidth={link => {
        if (highlightLinks.size === 0) return 2
        return highlightLinks.has(link) ? 4 : 1
      }}
      linkDirectionalArrowLength={link => {
        if (highlightLinks.size === 0) return 8
        return highlightLinks.has(link) ? 10 : 6
      }}
      linkDirectionalArrowRelPos={1}
      linkCanvasObjectMode={() => 'after'}
      linkCanvasObject={(link, ctx, globalScale) => {
        const label = link.name
        if (!label) return
        
        const isHighlighted = highlightLinks.size === 0 || highlightLinks.has(link)
        const fontSize = isHighlighted ? 12 / globalScale : 10 / globalScale
        ctx.font = `${isHighlighted ? 'bold' : ''} ${fontSize}px Sans-Serif`
        
        const midX = (link.source.x + link.target.x) / 2
        const midY = (link.source.y + link.target.y) / 2
        
        // Background for label
        const textWidth = ctx.measureText(label).width
        ctx.fillStyle = isHighlighted ? 'rgba(59, 130, 246, 0.95)' : 'rgba(229, 231, 235, 0.8)'
        ctx.fillRect(midX - textWidth/2 - 4, midY - fontSize/2 - 2, textWidth + 8, fontSize + 4)
        
        // Label text
        ctx.fillStyle = isHighlighted ? '#ffffff' : '#9ca3af'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.fillText(label, midX, midY)
      }}
      onNodeClick={handleNodeClick}
      onBackgroundClick={handleBackgroundClick}
      cooldownTicks={150}
      d3AlphaDecay={0.01}
      d3VelocityDecay={0.2}
      linkDistance={120}
      chargeStrength={-400}
      enableNodeDrag={true}
      enableZoomInteraction={true}
      enablePanInteraction={true}
      onEngineStop={() => {
        if (graphRef.current) {
          graphRef.current.zoomToFit(400, 80)
        }
      }}
    />
  )

  const renderNodeDetails = () => (
    showDetails && selectedNode && (
      <div className={isFullscreen ? "fullscreen-node-details" : "node-details"}>
        <div className="details-header">
          <h3>
            <Info size={20} />
            {selectedNode.name}
          </h3>
          <button className="close-btn" onClick={() => setShowDetails(false)}>×</button>
        </div>
        
        <div className="details-content">
          <div className="detail-row">
            <span className="detail-label">Type:</span>
            <span className="detail-value type-badge" style={{ background: selectedNode.color }}>
              {selectedNode.type}
            </span>
          </div>
          
          {selectedNode.description && (
            <div className="detail-row">
              <span className="detail-label">Description:</span>
              <span className="detail-value">{selectedNode.description}</span>
            </div>
          )}
          
          {selectedNode.properties && selectedNode.properties.length > 0 && (
            <div className="detail-section">
              <h4>Properties</h4>
              <div className="properties-list">
                {selectedNode.properties.map((prop, idx) => (
                  <div key={idx} className="property-item">
                    <span className="prop-name">{prop.name}</span>
                    <span className="prop-type">{prop.data_type}</span>
                    {prop.required && <span className="prop-required">Required</span>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  )

  if (isFullscreen) {
    return (
      <div className="fullscreen-modal">
        <div className="fullscreen-header">
          <div className="header-left">
            <h2 className="section-title">
              <Network size={24} />
              Ontology Graph - Fullscreen
            </h2>
            <div className="stats">
              <span className="stat-badge">
                {graphData.nodes.length} Entities
              </span>
              <span className="stat-badge">
                {graphData.links.length} Relationships
              </span>
            </div>
          </div>
          
          <div className="header-actions">
            {renderControls()}
            <button className="btn-icon" onClick={toggleFullscreen} title="Exit Fullscreen">
              <Minimize2 size={20} />
            </button>
            <button className="btn-icon" onClick={toggleFullscreen} title="Close">
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="fullscreen-graph">
          {renderGraph(window.innerHeight - 80)}
          
          <div className="graph-legend">
            <h4>Entity Types</h4>
            <div className="legend-items">
              <div className="legend-item">
                <span className="legend-color" style={{ background: '#667eea' }}></span>
                Concept
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{ background: '#10b981' }}></span>
                Entity
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{ background: '#f59e0b' }}></span>
                Attribute
              </div>
              <div className="legend-item">
                <span className="legend-color" style={{ background: '#8b5cf6' }}></span>
                Process
              </div>
            </div>
          </div>
          
          <div className="graph-help">
            <h4>💡 Quick Tips</h4>
            <ul>
              <li><strong>Click node</strong> to focus on its connections</li>
              <li><strong>Click background</strong> to show all</li>
              <li><strong>Drag nodes</strong> to rearrange</li>
              <li><strong>Mouse wheel</strong> to zoom</li>
              <li><strong>Spread/Compact</strong> to adjust spacing</li>
            </ul>
          </div>
          
          {renderNodeDetails()}
        </div>
      </div>
    )
  }

  return (
    <div className="ontology-viewer fade-in">
      <div className="viewer-header">
        <div className="header-left">
          <h2 className="section-title">
            <Network size={24} />
            Generated Ontology Graph
          </h2>
          <div className="stats">
            <span className="stat-badge">
              {graphData.nodes.length} Entities
            </span>
            <span className="stat-badge">
              {graphData.links.length} Relationships
            </span>
          </div>
        </div>
        
        {renderControls()}
      </div>

      <div className="graph-container">
        {renderGraph(600)}
        
        <div className="graph-legend">
          <h4>Entity Types</h4>
          <div className="legend-items">
            <div className="legend-item">
              <span className="legend-color" style={{ background: '#667eea' }}></span>
              Concept
            </div>
            <div className="legend-item">
              <span className="legend-color" style={{ background: '#10b981' }}></span>
              Entity
            </div>
            <div className="legend-item">
              <span className="legend-color" style={{ background: '#f59e0b' }}></span>
              Attribute
            </div>
            <div className="legend-item">
              <span className="legend-color" style={{ background: '#8b5cf6' }}></span>
              Process
            </div>
          </div>
        </div>
        
        <div className="graph-help">
          <h4>💡 Quick Tips</h4>
          <ul>
            <li><strong>Click node</strong> to focus on its connections</li>
            <li><strong>Click background</strong> to show all</li>
            <li><strong>Drag nodes</strong> to rearrange</li>
            <li><strong>Mouse wheel</strong> to zoom</li>
            <li><strong>Spread/Compact</strong> to adjust spacing</li>
          </ul>
        </div>
      </div>

      {renderNodeDetails()}

      <div className="action-buttons">
        <button className="btn btn-feedback" onClick={onRequestFeedback}>
          <MessageSquare size={20} />
          Provide Feedback
        </button>
        <button className="btn btn-confirm" onClick={handleConfirm}>
          <ThumbsUp size={20} />
          Confirm Ontology
        </button>
      </div>
    </div>
  )
}

export default OntologyViewer
