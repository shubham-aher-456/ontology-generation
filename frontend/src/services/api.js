import axios from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Error handler
const handleError = (error) => {
  if (error.response) {
    throw new Error(error.response.data.detail || 'An error occurred')
  } else if (error.request) {
    throw new Error('No response from server')
  } else {
    throw new Error(error.message || 'An error occurred')
  }
}

// API methods
const apiService = {
  // Health check
  async healthCheck() {
    try {
      const response = await api.get('/health')
      return response.data
    } catch (error) {
      handleError(error)
    }
  },

  // Upload transcript
  async uploadTranscript(formData) {
    try {
      const response = await api.post('/transcripts/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    } catch (error) {
      handleError(error)
    }
  },

  // List transcripts
  async listTranscripts() {
    try {
      const response = await api.get('/transcripts')
      return response.data
    } catch (error) {
      handleError(error)
    }
  },

  // Get transcript
  async getTranscript(transcriptId) {
    try {
      const response = await api.get(`/transcripts/${transcriptId}`)
      return response.data
    } catch (error) {
      handleError(error)
    }
  },

  // Generate ontology
  async generateOntology(transcriptId) {
    try {
      const response = await api.post(`/transcripts/${transcriptId}/generate-ontology`)
      return response.data
    } catch (error) {
      handleError(error)
    }
  },

  // Get ontology
  async getOntology(transcriptId) {
    try {
      const response = await api.get(`/transcripts/${transcriptId}/ontology`)
      return response.data
    } catch (error) {
      handleError(error)
    }
  },

  // Load to knowledge graph
  async loadToGraph(transcriptId) {
    try {
      const response = await api.post(`/transcripts/${transcriptId}/load-to-graph`)
      return response.data
    } catch (error) {
      handleError(error)
    }
  },

  // Get graph statistics
  async getGraphStatistics() {
    try {
      const response = await api.get('/knowledge-graph/statistics')
      return response.data
    } catch (error) {
      handleError(error)
    }
  },

  // Find entity
  async findEntity(entityName) {
    try {
      const response = await api.get(`/knowledge-graph/entity/${entityName}`)
      return response.data
    } catch (error) {
      handleError(error)
    }
  },

  // Get entity relationships
  async getEntityRelationships(entityName, relationshipType = null) {
    try {
      const url = relationshipType 
        ? `/knowledge-graph/entity/${entityName}/relationships?relationship_type=${relationshipType}`
        : `/knowledge-graph/entity/${entityName}/relationships`
      const response = await api.get(url)
      return response.data
    } catch (error) {
      handleError(error)
    }
  },

  // Delete transcript
  async deleteTranscript(transcriptId) {
    try {
      const response = await api.delete(`/transcripts/${transcriptId}`)
      return response.data
    } catch (error) {
      handleError(error)
    }
  },

  // Clear knowledge graph
  async clearGraph() {
    try {
      const response = await api.delete('/knowledge-graph/clear')
      return response.data
    } catch (error) {
      handleError(error)
    }
  },
}

export default apiService
