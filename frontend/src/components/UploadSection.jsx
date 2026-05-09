import React, { useState, useRef } from 'react'
import { Upload, FileText, Loader, Sparkles } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../services/api'
import './UploadSection.css'

function UploadSection({ onTranscriptUploaded, onOntologyGenerated, transcriptId, isLoading, setIsLoading }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const fileInputRef = useRef(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (!selectedFile.name.match(/\.(txt|md|json)$/)) {
        toast.error('Please upload a .txt, .md, or .json file')
        return
      }
      setFile(selectedFile)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      if (!droppedFile.name.match(/\.(txt|md|json)$/)) {
        toast.error('Please upload a .txt, .md, or .json file')
        return
      }
      setFile(droppedFile)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file first')
      return
    }

    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', file.name.replace(/\.[^/.]+$/, ''))
      formData.append('description', 'Uploaded transcript for ontology generation')

      const response = await api.uploadTranscript(formData)
      toast.success('Transcript uploaded successfully!')
      onTranscriptUploaded(response.transcript_id)
    } catch (error) {
      toast.error(error.message || 'Failed to upload transcript')
    } finally {
      setUploading(false)
    }
  }

  const handleGenerateOntology = async () => {
    if (!transcriptId) {
      toast.error('Please upload a transcript first')
      return
    }

    setGenerating(true)
    setIsLoading(true)
    try {
      await api.generateOntology(transcriptId)
      toast.success('Ontology generation started!')
      
      // Fetch the generated ontology
      const ontologyData = await api.getOntology(transcriptId)
      
      // Load to knowledge graph
      await api.loadToGraph(transcriptId)
      
      toast.success('Ontology generated and loaded to graph!')
      onOntologyGenerated(ontologyData)
    } catch (error) {
      toast.error(error.message || 'Failed to generate ontology')
      setIsLoading(false)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="upload-section fade-in">
      <div className="upload-card">
        <h2 className="section-title">
          <FileText size={24} />
          Upload Transcript
        </h2>
        
        <div 
          className={`drop-zone ${file ? 'has-file' : ''}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.md,.json"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
          
          {file ? (
            <div className="file-info">
              <FileText size={48} className="file-icon" />
              <p className="file-name">{file.name}</p>
              <p className="file-size">{(file.size / 1024).toFixed(2)} KB</p>
            </div>
          ) : (
            <div className="drop-placeholder">
              <Upload size={48} />
              <p>Drag & drop your transcript here</p>
              <p className="drop-hint">or click to browse</p>
              <p className="file-types">Supported: .txt, .md, .json</p>
            </div>
          )}
        </div>

        <div className="button-group">
          <button 
            className="btn btn-primary"
            onClick={handleUpload}
            disabled={!file || uploading}
          >
            {uploading ? (
              <>
                <Loader size={20} className="spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload size={20} />
                Upload Transcript
              </>
            )}
          </button>

          <button 
            className="btn btn-secondary"
            onClick={handleGenerateOntology}
            disabled={!transcriptId || generating || isLoading}
          >
            {generating ? (
              <>
                <Loader size={20} className="spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles size={20} />
                Generate Ontology
              </>
            )}
          </button>
        </div>

        {transcriptId && (
          <div className="success-message">
            <span className="success-icon">✓</span>
            Transcript uploaded successfully! Ready to generate ontology.
          </div>
        )}
      </div>
    </div>
  )
}

export default UploadSection
