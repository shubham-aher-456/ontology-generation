import React, { useState } from 'react'
import { Toaster } from 'react-hot-toast'
import Header from './components/Header'
import UploadSection from './components/UploadSection'
import OntologyViewer from './components/OntologyViewer'
import FeedbackModal from './components/FeedbackModal'
import './App.css'

function App() {
  const [transcriptId, setTranscriptId] = useState(null)
  const [ontologyData, setOntologyData] = useState(null)
  const [showFeedback, setShowFeedback] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleTranscriptUploaded = (id) => {
    setTranscriptId(id)
    setOntologyData(null)
  }

  const handleOntologyGenerated = (data) => {
    setOntologyData(data)
    setIsLoading(false)
  }

  const handleFeedbackSubmit = () => {
    setShowFeedback(false)
    setIsLoading(true)
  }

  const handleConfirmOntology = () => {
    setShowFeedback(false)
  }

  return (
    <div className="app">
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 4000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      
      <Header />
      
      <main className="main-content">
        <div className="container">
          <UploadSection 
            onTranscriptUploaded={handleTranscriptUploaded}
            onOntologyGenerated={handleOntologyGenerated}
            transcriptId={transcriptId}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
          
          {ontologyData && (
            <OntologyViewer 
              ontologyData={ontologyData}
              onRequestFeedback={() => setShowFeedback(true)}
              onConfirm={handleConfirmOntology}
              transcriptId={transcriptId}
            />
          )}
        </div>
      </main>

      {showFeedback && (
        <FeedbackModal
          transcriptId={transcriptId}
          onClose={() => setShowFeedback(false)}
          onSubmit={handleFeedbackSubmit}
          onOntologyRegenerated={handleOntologyGenerated}
        />
      )}
    </div>
  )
}

export default App
