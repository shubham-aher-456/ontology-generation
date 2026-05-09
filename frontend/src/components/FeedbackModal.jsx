import React, { useState } from 'react'
import { X, Send, Loader } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../services/api'
import './FeedbackModal.css'

function FeedbackModal({ transcriptId, onClose, onSubmit, onOntologyRegenerated }) {
  const [feedback, setFeedback] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!feedback.trim()) {
      toast.error('Please provide feedback')
      return
    }

    setIsSubmitting(true)
    try {
      // In a real implementation, you would send feedback to backend
      // For now, we'll regenerate the ontology
      toast.success('Feedback received! Regenerating ontology...')
      
      // Simulate feedback processing and regeneration
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Regenerate ontology
      await api.generateOntology(transcriptId)
      const ontologyData = await api.getOntology(transcriptId)
      await api.loadToGraph(transcriptId)
      
      toast.success('Ontology regenerated based on your feedback!')
      onOntologyRegenerated(ontologyData)
      onSubmit()
      onClose()
    } catch (error) {
      toast.error(error.message || 'Failed to process feedback')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Provide Feedback</h2>
          <button className="close-button" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="modal-body">
          <p className="feedback-instruction">
            Help us improve the ontology by providing specific feedback about what needs to be changed, 
            added, or removed. Be as detailed as possible.
          </p>

          <textarea
            className="feedback-textarea"
            placeholder="Example: 
- Add a relationship between Customer and Payment
- Remove the duplicate Product entity
- Change the Order entity to include a status attribute
- The Invoice entity should have a relationship with Payment..."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            rows={10}
          />

          <div className="feedback-tips">
            <h4>💡 Tips for effective feedback:</h4>
            <ul>
              <li>Be specific about entities and relationships</li>
              <li>Mention what's missing or incorrect</li>
              <li>Suggest improvements or additions</li>
              <li>Describe the expected domain model</li>
            </ul>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-cancel" onClick={onClose}>
            Cancel
          </button>
          <button 
            className="btn btn-submit" 
            onClick={handleSubmit}
            disabled={isSubmitting || !feedback.trim()}
          >
            {isSubmitting ? (
              <>
                <Loader size={20} className="spin" />
                Processing...
              </>
            ) : (
              <>
                <Send size={20} />
                Submit & Regenerate
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default FeedbackModal
