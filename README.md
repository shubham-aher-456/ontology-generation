# 🌐 Ontology Knowledge Base

> Transform transcripts into intelligent, interactive knowledge graphs using AI

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.16-brightgreen.svg)](https://neo4j.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

The **Ontology Knowledge Base** is a full-stack application that automatically generates structured ontologies from unstructured text transcripts using advanced AI models. It provides an intuitive web interface for uploading transcripts, visualizing knowledge graphs, and iteratively refining ontologies through user feedback.

### What It Does

1. **Upload** - Submit meeting notes, documents, or any text transcript
2. **Process** - AI analyzes and extracts entities, relationships, and attributes
3. **Visualize** - Interactive force-directed graph shows the ontology structure
4. **Refine** - Provide feedback to improve and regenerate the ontology
5. **Store** - Save the final ontology to a Neo4j knowledge graph database


---

## ✨ Features

### 🎨 Frontend Features
- **Modern UI/UX** - Beautiful gradient design with smooth animations
- **Drag & Drop Upload** - Easy file upload with visual feedback
- **Interactive Graph Visualization** - Force-directed layout with zoom, pan, and drag
- **Real-time Feedback** - Instant notifications and loading states
- **Node Details Panel** - Click any entity to see properties and relationships
- **Iterative Refinement** - Provide feedback and regenerate ontologies
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Fullscreen Mode** - Expand graph for detailed exploration

### 🚀 Backend Features
- **AI-Powered Extraction** - Uses Azure OpenAI GPT-4 for intelligent ontology generation
- **Multi-Model Support** - Supports OpenAI and Anthropic Claude models
- **Structured Output** - Generates well-formed ontologies with entities, relationships, and attributes
- **Knowledge Graph Storage** - Persists ontologies in Neo4j graph database
- **Metadata Management** - PostgreSQL for transcript and ontology metadata
- **Caching Layer** - Redis for performance optimization
- **RESTful API** - Clean, documented API endpoints
- **Async Processing** - Non-blocking operations for better performance
- **Comprehensive Testing** - Unit, integration, and E2E tests

### 📊 Graph Features
- **Color-Coded Entities** - Different colors for concepts, entities, attributes, processes
- **Directional Relationships** - Arrows show relationship direction
- **Relationship Labels** - Clear labels on all connections
- **Node Sizing** - Size based on number of properties
- **Zoom Controls** - Zoom in/out, fit view, center graph
- **Layout Controls** - Spread, compact, and reset layout options
- **Highlighting** - Click nodes to highlight connections
- **Legend** - Visual guide to entity types


---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER BROWSER                            │
│                  http://localhost:3000                      │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              React Frontend (Vite)                    │ │
│  │  • Upload Interface                                   │ │
│  │  • Force-Directed Graph (react-force-graph-2d)       │ │
│  │  • Feedback Modal                                     │ │
│  │  • Interactive Controls                               │ │
│  └───────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/REST API
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                           │
│                http://localhost:8000                        │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Transcript   │  │  Ontology    │  │   LLM Service   │  │
│  │ Processor    │→ │  Generator   │→ │  (Azure OpenAI) │  │
│  └──────────────┘  └──────────────┘  └─────────────────┘  │
│                                              ↓              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Knowledge Graph Service (Neo4j)              │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓               ↓
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ PostgreSQL   │ │  Neo4j   │ │    Redis     │
│   :5433      │ │  :7688   │ │    :6380     │
│              │ │          │ │              │
│ Metadata     │ │ Knowledge│ │   Cache      │
│ Storage      │ │  Graph   │ │   Session    │
└──────────────┘ └──────────┘ └──────────────┘
```

### Technology Stack

**Frontend:**
- React 18.2 - UI framework
- Vite - Build tool and dev server
- react-force-graph-2d - Graph visualization
- Axios - HTTP client
- Lucide React - Icons
- React Hot Toast - Notifications

**Backend:**
- FastAPI - Web framework
- Python 3.10+ - Programming language
- Pydantic - Data validation
- Uvicorn - ASGI server
- Azure OpenAI - AI model provider

**Databases:**
- Neo4j 5.16 - Graph database for knowledge graphs
- PostgreSQL 15 - Relational database for metadata
- Redis 7 - In-memory cache

**DevOps:**
- Docker & Docker Compose - Containerization
- pytest - Testing framework
- GitHub Actions - CI/CD (optional)


---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

### Required
- **Python 3.10 or higher** - [Download](https://www.python.org/downloads/)
- **Node.js 16 or higher** - [Download](https://nodejs.org/)
- **Docker Desktop** - [Download](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download](https://git-scm.com/downloads)

### API Keys
- **Azure OpenAI API Key** - [Get one here](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
  - Or **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)
  - Or **Anthropic API Key** - [Get one here](https://console.anthropic.com/)

### System Requirements
- **RAM:** 8GB minimum, 16GB recommended
- **Disk Space:** 5GB free space
- **OS:** Windows 10/11, macOS 10.15+, or Linux

---

## 🚀 Installation

### Quick Start (5 Minutes)

```bash
# 1. Clone the repository
git clone <repository-url>
cd ontology-knowledge-base

# 2. Set up environment variables
cp .env.example .env
# Edit .env and add your API keys

# 3. Start Docker services
docker-compose up -d

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Start backend
python -m uvicorn src.main:app --reload

# 6. Install frontend dependencies (new terminal)
cd frontend
npm install

# 7. Start frontend
npm run dev

# 8. Open browser
# Navigate to http://localhost:3000
```


### Backend Setup

#### 1. Environment Configuration

Create a `.env` file in the root directory:

```bash
# Copy example file
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# LLM Provider Configuration
LLM_PROVIDER=azure_openai  # Options: azure_openai, openai, anthropic

# Azure OpenAI (if using azure_openai)
AZURE_OPENAI_API_KEY=your-azure-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# OpenAI (if using openai)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Anthropic (if using anthropic)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
ANTHROPIC_MODEL=claude-3-opus-20240229

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=ontology_kb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

NEO4J_URI=bolt://localhost:7688
NEO4J_USER=neo4j
NEO4J_PASSWORD=ontology123
NEO4J_DATABASE=neo4j

REDIS_HOST=localhost
REDIS_PORT=6380
REDIS_DB=0

# Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
API_HOST=0.0.0.0
API_PORT=8000
```

#### 2. Start Docker Services

```bash
# Start all services (PostgreSQL, Neo4j, Redis)
docker-compose up -d

# Verify services are running
docker ps

# Check service health
docker-compose ps
```

Expected output:
```
NAME                 STATUS              PORTS
ontology-postgres    Up (healthy)        0.0.0.0:5433->5432/tcp
ontology-neo4j       Up (healthy)        0.0.0.0:7475->7474/tcp, 0.0.0.0:7688->7687/tcp
ontology-redis       Up (healthy)        0.0.0.0:6380->6379/tcp
```

#### 3. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 4. Start Backend Server

```bash
# Development mode with auto-reload
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or using the shortcut
python src/main.py
```

Backend will be available at: `http://localhost:8000`

#### 5. Verify Backend

Open browser and navigate to:
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **System Status:** http://localhost:8000/system/status


### Frontend Setup

#### 1. Navigate to Frontend Directory

```bash
cd frontend
```

#### 2. Install Dependencies

```bash
# Install all npm packages
npm install
```

This will install:
- React and React DOM
- Vite (build tool)
- react-force-graph-2d (graph visualization)
- Axios (HTTP client)
- Lucide React (icons)
- React Hot Toast (notifications)

#### 3. Configure Frontend (Optional)

Edit `frontend/vite.config.js` if you need to change ports or proxy settings:

```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,  // Change frontend port
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Backend URL
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

#### 4. Start Development Server

```bash
# Start Vite dev server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

#### 5. Build for Production (Optional)

```bash
# Create optimized production build
npm run build

# Preview production build
npm run preview
```

### Alternative: Quick Start Script (Windows)

Simply double-click `start-frontend.bat` in the root directory. This will:
1. Check for Node.js installation
2. Install dependencies if needed
3. Start the development server
4. Open browser automatically


---

## 📖 Usage

### Complete Workflow Example

#### Step 1: Upload Transcript

1. Open `http://localhost:3000` in your browser
2. You'll see a beautiful landing page with an upload section
3. Drag and drop a `.txt` file or click to browse
4. Click **"Upload Transcript"** button
5. Wait for success notification ✅

**Supported file formats:** `.txt`, `.md`, `.json`

#### Step 2: Generate Ontology

1. After successful upload, click **"Generate Ontology"** button
2. Wait 10-30 seconds while AI processes your transcript
3. A loading indicator shows progress
4. The interactive graph appears automatically!

#### Step 3: Explore the Graph

**Interactive Controls:**
- 🖱️ **Mouse Wheel** - Zoom in/out
- 🖱️ **Click & Drag Background** - Pan around the graph
- 🖱️ **Click Node** - View entity details in side panel
- 🖱️ **Drag Node** - Rearrange node position
- 🔍 **Zoom Buttons** - Use +/- buttons in top-right
- 📐 **Fit View** - Click maximize button to fit all nodes
- 🔄 **Spread/Compact** - Adjust node spacing
- ↺ **Reset Layout** - Return to default layout

**Graph Features:**
- **Color-coded entities** - Blue (Concept), Green (Entity), Yellow (Attribute), Purple (Process)
- **Directional arrows** - Show relationship direction
- **Relationship labels** - Clear labels on all connections
- **Node sizing** - Larger nodes have more properties
- **Legend** - Visual guide in top-right corner
- **Help tips** - Quick reference in bottom-left

#### Step 4: View Node Details

1. Click any node in the graph
2. A details panel slides up showing:
   - Entity name and type
   - Description
   - All properties with data types
   - Required field indicators
3. Connected nodes and relationships are highlighted
4. Click background to deselect and show all nodes

#### Step 5: Provide Feedback (Optional)

If you want to improve the ontology:

1. Click **"Provide Feedback"** button
2. A modal appears with a text area
3. Type specific feedback, for example:

```
Please make the following changes:

1. Add a "Payment" entity with properties:
   - amount (number, required)
   - method (string, required)
   - status (string, required)

2. Add relationship: Order --paid_by--> Payment

3. Remove the duplicate "Product" entity

4. Update "Customer" entity:
   - Add "loyalty_points" property (number)
   - Add "registration_date" property (date)

5. Add relationship: Customer --writes--> Review --for--> Product
```

4. Click **"Submit & Regenerate"**
5. Wait for AI to process your feedback
6. New ontology appears with your requested changes!

#### Step 6: Confirm Ontology

1. Review the final ontology graph
2. Ensure all entities and relationships are correct
3. Click **"Confirm Ontology"** button
4. Success notification appears
5. Ontology is saved to Neo4j knowledge graph database! 💾


### Sample Transcript

Create a file `sample_transcript.txt`:

```
E-Commerce Platform Requirements

Our e-commerce platform needs to manage products, customers, and orders.

Products:
- Each product has a SKU, name, description, price, and category
- Products belong to categories like Electronics, Clothing, Books
- Products have inventory quantities and reorder levels
- Products can have multiple images and reviews

Customers:
- Customers register with email, password, name, and phone
- Customers can have multiple shipping addresses
- Customers have a default payment method
- Customers can create wishlists and shopping carts

Orders:
- Customers place orders containing multiple products
- Each order has an order number, date, status, and total amount
- Order status: pending, processing, shipped, delivered, cancelled
- Orders are shipped to a customer address
- Orders generate invoices

Payments:
- Each order has one payment
- Payments have method (credit card, PayPal, bank transfer)
- Payments have status (pending, completed, failed, refunded)
- Payments have transaction ID and timestamp

Reviews:
- Customers can write reviews for products they purchased
- Reviews have rating (1-5 stars), title, comment, and date
- Reviews can be marked as verified purchase
```

Upload this file and generate an ontology to see the system in action!

### Expected Graph Output

After processing, you'll see a graph with:

**Entities:**
- Customer (green)
- Product (green)
- Order (green)
- Payment (green)
- Review (green)
- Category (blue)
- Address (yellow)
- Invoice (green)

**Relationships:**
- Customer --places--> Order
- Order --contains--> Product
- Order --paid_by--> Payment
- Order --shipped_to--> Address
- Order --generates--> Invoice
- Customer --writes--> Review
- Review --for--> Product
- Product --belongs_to--> Category
- Customer --has--> Address


---

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Interactive API Docs
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Core Endpoints

#### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "ontology-knowledge-base",
  "version": "1.0.0"
}
```

#### Upload Transcript
```http
POST /transcripts/upload
Content-Type: multipart/form-data

file: <transcript-file>
```

Response:
```json
{
  "transcript_id": "uuid-here",
  "filename": "meeting_notes.txt",
  "size": 15234,
  "status": "uploaded",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Generate Ontology
```http
POST /ontology/generate
Content-Type: application/json

{
  "transcript_id": "uuid-here"
}
```

Response:
```json
{
  "ontology_id": "uuid-here",
  "transcript_id": "uuid-here",
  "entities": [
    {
      "name": "Customer",
      "type": "entity",
      "description": "A person who purchases products",
      "properties": [
        {
          "name": "email",
          "data_type": "string",
          "required": true
        }
      ]
    }
  ],
  "relationships": [
    {
      "source": "Customer",
      "target": "Order",
      "name": "places",
      "type": "relationship"
    }
  ],
  "status": "completed"
}
```

#### Regenerate with Feedback
```http
POST /ontology/regenerate
Content-Type: application/json

{
  "ontology_id": "uuid-here",
  "feedback": "Add Payment entity and connect to Order"
}
```

#### Confirm Ontology
```http
POST /ontology/{ontology_id}/confirm
```

Response:
```json
{
  "ontology_id": "uuid-here",
  "status": "confirmed",
  "saved_to_neo4j": true,
  "entities_created": 15,
  "relationships_created": 18
}
```

#### Get Knowledge Graph Statistics
```http
GET /knowledge-graph/statistics
```

Response:
```json
{
  "total_nodes": 150,
  "total_relationships": 230,
  "total_labels": 12,
  "total_relationship_types": 18
}
```

### Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message here",
  "status_code": 400,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Common status codes:
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error


---

## 📁 Project Structure

```
ontology-knowledge-base/
├── backend/
│   ├── src/
│   │   ├── domain/
│   │   │   ├── models.py              # Pydantic models
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── llm_service.py         # LLM integration
│   │   │   ├── ontology_generator.py  # Ontology generation
│   │   │   ├── transcript_processor.py # Text processing
│   │   │   ├── knowledge_graph_service.py # Neo4j integration
│   │   │   └── __init__.py
│   │   ├── main.py                    # FastAPI application
│   │   └── __init__.py
│   ├── config/
│   │   ├── settings.py                # Configuration
│   │   ├── logging_config.py          # Logging setup
│   │   └── __init__.py
│   ├── tests/
│   │   ├── test_domain_models.py
│   │   ├── test_llm_service.py
│   │   ├── test_ontology_generator.py
│   │   ├── test_transcript_processor.py
│   │   ├── test_integration_e2e.py
│   │   └── __init__.py
│   └── requirements.txt               # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx             # App header
│   │   │   ├── Header.css
│   │   │   ├── UploadSection.jsx      # File upload
│   │   │   ├── UploadSection.css
│   │   │   ├── OntologyViewer.jsx     # Graph visualization
│   │   │   ├── OntologyViewer.css
│   │   │   ├── FeedbackModal.jsx      # Feedback form
│   │   │   └── FeedbackModal.css
│   │   ├── services/
│   │   │   └── api.js                 # API client
│   │   ├── App.jsx                    # Main app component
│   │   ├── App.css
│   │   ├── main.jsx                   # Entry point
│   │   └── index.css                  # Global styles
│   ├── public/
│   │   └── vite.svg
│   ├── index.html                     # HTML template
│   ├── package.json                   # npm dependencies
│   ├── vite.config.js                 # Vite configuration
│   └── README.md                      # Frontend docs
│
├── data/                              # Data storage
├── docs/                              # Documentation
├── .env                               # Environment variables
├── .env.example                       # Example env file
├── .gitignore                         # Git ignore rules
├── docker-compose.yml                 # Docker services
├── Dockerfile                         # Backend container
├── pytest.ini                         # Pytest configuration
├── start-frontend.bat                 # Windows quick start
├── README.md                          # This file
├── QUICK_START_GUIDE.md              # Quick start guide
├── COMPLETE_GUIDE.md                 # Detailed guide
└── FRONTEND_SETUP.md                 # Frontend setup guide
```

### Key Files Explained

**Backend:**
- `src/main.py` - FastAPI application entry point, defines all API routes
- `src/services/llm_service.py` - Handles communication with AI models (Azure OpenAI, OpenAI, Anthropic)
- `src/services/ontology_generator.py` - Core logic for generating ontologies from transcripts
- `src/services/knowledge_graph_service.py` - Neo4j database operations
- `config/settings.py` - Application configuration using Pydantic Settings

**Frontend:**
- `src/App.jsx` - Main React component, manages application state
- `src/components/OntologyViewer.jsx` - Graph visualization using react-force-graph-2d
- `src/components/UploadSection.jsx` - File upload with drag & drop
- `src/components/FeedbackModal.jsx` - Feedback form for ontology refinement
- `src/services/api.js` - Axios-based API client

**Configuration:**
- `.env` - Environment variables (API keys, database credentials)
- `docker-compose.yml` - Defines PostgreSQL, Neo4j, and Redis services
- `vite.config.js` - Frontend build configuration


---

## ⚙️ Configuration

### Environment Variables

#### LLM Provider Settings

**Azure OpenAI:**
```env
LLM_PROVIDER=azure_openai
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**OpenAI:**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4-turbo-preview
```

**Anthropic Claude:**
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key
ANTHROPIC_MODEL=claude-3-opus-20240229
```

#### Database Settings

**PostgreSQL:**
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=ontology_kb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

**Neo4j:**
```env
NEO4J_URI=bolt://localhost:7688
NEO4J_USER=neo4j
NEO4J_PASSWORD=ontology123
NEO4J_DATABASE=neo4j
```

**Redis:**
```env
REDIS_HOST=localhost
REDIS_PORT=6380
REDIS_DB=0
```

#### Application Settings

```env
ENVIRONMENT=development  # or production
DEBUG=true              # or false
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
API_HOST=0.0.0.0
API_PORT=8000
```

### Docker Configuration

Edit `docker-compose.yml` to customize service settings:

```yaml
services:
  postgres:
    ports:
      - "5433:5432"  # Change external port
    environment:
      POSTGRES_PASSWORD: your-password  # Change password
  
  neo4j:
    ports:
      - "7475:7474"  # HTTP
      - "7688:7687"  # Bolt
    environment:
      NEO4J_AUTH: neo4j/your-password  # Change password
      NEO4J_server_memory_heap_max__size: 2G  # Adjust memory
  
  redis:
    ports:
      - "6380:6379"  # Change external port
```

### Frontend Configuration

Edit `frontend/vite.config.js`:

```javascript
export default defineConfig({
  server: {
    port: 3000,  // Change frontend port
    host: true,  // Expose to network
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Backend URL
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',  // Output directory
    sourcemap: true,  // Generate source maps
  }
})
```

### Graph Visualization Settings

Edit `frontend/src/components/OntologyViewer.jsx`:

```javascript
// Adjust physics simulation
<ForceGraph2D
  cooldownTicks={150}        // Simulation duration
  d3AlphaDecay={0.01}       // Cooling rate
  d3VelocityDecay={0.2}     // Friction
  linkDistance={180}         // Distance between nodes
  chargeStrength={-600}      // Repulsion force
/>

// Change entity colors
const getColorByType = (type) => {
  const colors = {
    'concept': '#667eea',    // Blue
    'entity': '#10b981',     // Green
    'attribute': '#f59e0b',  // Yellow
    'process': '#8b5cf6',    // Purple
  }
  return colors[type] || '#6b7280'
}
```


---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Backend Issues

**Problem: Backend won't start**
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Check for port conflicts
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # macOS/Linux
```

**Problem: Cannot connect to databases**
```bash
# Check Docker services
docker ps

# Restart services
docker-compose down
docker-compose up -d

# Check service logs
docker logs ontology-postgres
docker logs ontology-neo4j
docker logs ontology-redis
```

**Problem: LLM API errors**
```bash
# Verify API key in .env
cat .env | grep API_KEY

# Test API connection
curl -X GET http://localhost:8000/health

# Check backend logs for detailed error messages
```

#### Frontend Issues

**Problem: Frontend won't start**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Try different port
# Edit vite.config.js and change port to 3001
```

**Problem: Graph not rendering**
```
1. Open browser console (F12)
2. Check for JavaScript errors
3. Verify backend is running (http://localhost:8000/health)
4. Clear browser cache (Ctrl+Shift+Delete)
5. Try different browser (Chrome recommended)
6. Disable browser extensions
```

**Problem: Upload fails**
```
1. Check file format (.txt, .md, .json only)
2. Verify file size (< 50MB)
3. Check file encoding (should be UTF-8)
4. Verify backend is accessible
5. Check browser console for errors
```

#### Docker Issues

**Problem: Docker services won't start**
```bash
# Check Docker is running
docker --version
docker ps

# Restart Docker Desktop

# Remove old containers and volumes
docker-compose down -v
docker-compose up -d

# Check disk space
docker system df
docker system prune  # Clean up unused resources
```

**Problem: Port already in use**
```bash
# Find process using port
netstat -ano | findstr :5433  # Windows
lsof -i :5433  # macOS/Linux

# Kill process or change port in docker-compose.yml
```

#### Performance Issues

**Problem: Slow graph rendering**
```
1. Use production build: npm run build && npm run preview
2. Reduce number of nodes (< 100 recommended)
3. Close other browser tabs
4. Use Chrome for best performance
5. Check CPU and memory usage
6. Disable browser extensions
```

**Problem: Slow ontology generation**
```
1. Check internet connection
2. Verify LLM API is responding
3. Use smaller transcripts for testing
4. Check backend logs for bottlenecks
5. Consider using faster LLM model
```

### Getting Help

If you're still experiencing issues:

1. **Check logs:**
   - Backend: Terminal where uvicorn is running
   - Frontend: Browser console (F12)
   - Docker: `docker logs <container-name>`

2. **Verify system status:**
   ```bash
   # Backend health
   curl http://localhost:8000/health
   
   # System status
   curl http://localhost:8000/system/status
   ```

3. **Review documentation:**
   - `QUICK_START_GUIDE.md` - Quick setup
   - `COMPLETE_GUIDE.md` - Detailed guide
   - `FRONTEND_SETUP.md` - Frontend details

4. **Check GitHub Issues:**
   - Search existing issues
   - Create new issue with:
     - Error messages
     - Steps to reproduce
     - System information
     - Logs


---

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_ontology_generator.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_ontology_generator.py::test_generate_ontology
```

### Test Categories

**Unit Tests:**
- `test_domain_models.py` - Pydantic model validation
- `test_llm_service.py` - LLM service functionality
- `test_ontology_generator.py` - Ontology generation logic
- `test_transcript_processor.py` - Text processing

**Integration Tests:**
- `test_integration_e2e.py` - End-to-end workflow
- `test_knowledge_graph_e2e.py` - Neo4j integration

**Robustness Tests:**
- `test_edge_cases_comprehensive.py` - Edge cases
- `test_robustness_advanced.py` - Stress testing

### Frontend Testing

```bash
cd frontend

# Run tests (if configured)
npm test

# Run with coverage
npm test -- --coverage
```

### Manual Testing

Use the provided test scripts:

```bash
# Test all APIs
python test_all_apis.py

# Test specific API
python test_api.py

# Test ontology generation
python test_ontology_direct.py

# Test fresh upload workflow
python test_fresh_upload.py
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Update `.env` with production values
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=false`
- [ ] Use strong database passwords
- [ ] Configure CORS properly
- [ ] Set up SSL/TLS certificates
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Test all endpoints
- [ ] Build frontend for production

### Docker Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### Frontend Production Build

```bash
cd frontend

# Create optimized build
npm run build

# Output will be in dist/ directory
# Serve with nginx, Apache, or any static file server
```

### Environment-Specific Configuration

**Development:**
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

**Production:**
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
```

---

## 📊 Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# System status
curl http://localhost:8000/system/status

# Database statistics
curl http://localhost:8000/knowledge-graph/statistics
```

### Logs

**Backend logs:**
```bash
# View live logs
tail -f logs/app.log

# Docker logs
docker logs -f ontology-api
```

**Database logs:**
```bash
# PostgreSQL
docker logs ontology-postgres

# Neo4j
docker logs ontology-neo4j

# Redis
docker logs ontology-redis
```

### Metrics

Access Neo4j Browser for graph metrics:
- URL: http://localhost:7475
- Username: neo4j
- Password: ontology123

Run Cypher queries:
```cypher
// Count all nodes
MATCH (n) RETURN count(n)

// Count all relationships
MATCH ()-[r]->() RETURN count(r)

// View all node labels
CALL db.labels()

// View all relationship types
CALL db.relationshipTypes()
```


---

## 🎓 Best Practices

### Creating Better Ontologies

**1. Write Clear Transcripts**
- Use descriptive language
- Mention entities explicitly
- Describe relationships clearly
- Include attributes and properties
- Use consistent terminology

**2. Structure Your Content**
```
Good Example:
"The Customer entity has properties: name (string), email (string), 
and phone (string). Customers can place Orders, which contain Products."

Bad Example:
"People buy stuff and we track it."
```

**3. Iterative Refinement**
- Start with a basic ontology
- Review the generated graph
- Provide specific feedback
- Regenerate and refine
- Confirm when satisfied

### Graph Organization Tips

**1. Visual Layout**
- Drag important nodes to center
- Group related entities together
- Use zoom to focus on sections
- Click "Fit View" to reset layout

**2. Understanding Relationships**
- Follow arrow directions
- Read relationship labels carefully
- Check cardinality (one-to-many, many-to-many)
- View node details for full context

**3. Feedback Guidelines**
```
Effective Feedback:
✅ "Add a Payment entity with amount, method, and status properties"
✅ "Create relationship: Order --paid_by--> Payment"
✅ "Remove the duplicate Product entity"
✅ "Update Customer to include loyalty_points property"

Ineffective Feedback:
❌ "Fix the graph"
❌ "Make it better"
❌ "Add more stuff"
❌ "This is wrong"
```

### Performance Optimization

**Backend:**
- Use caching for repeated queries
- Batch process large transcripts
- Optimize Neo4j queries with indexes
- Monitor memory usage
- Use async operations

**Frontend:**
- Limit graph size (< 100 nodes for best performance)
- Use production build for deployment
- Enable code splitting
- Optimize images and assets
- Use lazy loading

### Security Best Practices

**1. API Keys**
- Never commit `.env` files
- Use environment variables
- Rotate keys regularly
- Use different keys for dev/prod

**2. Database Security**
- Use strong passwords
- Enable authentication
- Restrict network access
- Regular backups
- Update regularly

**3. Application Security**
- Validate all inputs
- Sanitize user data
- Enable CORS properly
- Use HTTPS in production
- Implement rate limiting
- Add authentication/authorization

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/ontology-knowledge-base.git
   cd ontology-knowledge-base
   ```
3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes**
5. **Test your changes**
   ```bash
   pytest
   npm test
   ```
6. **Commit your changes**
   ```bash
   git commit -m "Add: your feature description"
   ```
7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request**

### Contribution Guidelines

**Code Style:**
- Follow PEP 8 for Python
- Use ESLint for JavaScript
- Write clear comments
- Add docstrings to functions

**Testing:**
- Write tests for new features
- Ensure all tests pass
- Maintain test coverage > 80%

**Documentation:**
- Update README if needed
- Add inline comments
- Update API documentation
- Include examples

**Commit Messages:**
```
Add: New feature
Fix: Bug fix
Update: Existing feature improvement
Docs: Documentation changes
Test: Test additions or changes
Refactor: Code refactoring
```

### Areas for Contribution

- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🧪 Additional tests
- 🎨 UI/UX enhancements
- ⚡ Performance optimizations
- 🌐 Internationalization
- ♿ Accessibility improvements

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework for Python
- **React** - UI library
- **Neo4j** - Graph database
- **OpenAI** - AI models
- **react-force-graph** - Graph visualization library
- **Vite** - Build tool

---

## 📞 Support

### Documentation
- [Quick Start Guide](QUICK_START_GUIDE.md)
- [Complete Guide](COMPLETE_GUIDE.md)
- [Frontend Setup](FRONTEND_SETUP.md)
- [API Documentation](http://localhost:8000/docs)

### Resources
- **GitHub Issues** - Report bugs or request features
- **Discussions** - Ask questions and share ideas
- **Wiki** - Additional documentation and guides

### Contact
- **Email:** support@example.com
- **Twitter:** @example
- **Discord:** [Join our server](https://discord.gg/example)

---

## 🎉 Quick Links

- 🌐 **Frontend:** http://localhost:3000
- 🔧 **Backend API:** http://localhost:8000
- 📚 **API Docs:** http://localhost:8000/docs
- 🗄️ **Neo4j Browser:** http://localhost:7475
- 📊 **Health Check:** http://localhost:8000/health

---

## 🚀 What's Next?

After getting started, explore these advanced features:

1. **Custom Entity Types** - Define your own entity categories
2. **Advanced Queries** - Use Cypher to query the knowledge graph
3. **Export Options** - Export ontologies as JSON, GraphML, or images
4. **Batch Processing** - Process multiple transcripts at once
5. **API Integration** - Integrate with other systems
6. **Custom Visualizations** - Create custom graph layouts
7. **Collaborative Editing** - Share and collaborate on ontologies

---

**Built with ❤️ by the Ontology Knowledge Base Team**

**Star ⭐ this repo if you find it useful!**

