import React from 'react'
import { Network } from 'lucide-react'
import './Header.css'

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <Network size={32} />
          <h1>Ontology Knowledge Base</h1>
        </div>
        <p className="tagline">Transform transcripts into intelligent knowledge graphs</p>
      </div>
    </header>
  )
}

export default Header
