# Ontology Knowledge Base - Frontend

Beautiful, modern React frontend for the Ontology Knowledge Base system with interactive graph visualization.

## Features

✨ **Modern UI/UX**
- Clean, gradient-based design
- Smooth animations and transitions
- Responsive layout for all devices
- Toast notifications for user feedback

📤 **Transcript Upload**
- Drag & drop file upload
- Support for .txt, .md, .json files
- Real-time upload progress
- File validation

🎨 **Interactive Graph Visualization**
- Force-directed graph layout
- Color-coded entity types
- Zoom, pan, and drag interactions
- Node details on click
- Relationship labels
- Legend for entity types

💬 **Feedback System**
- Provide detailed feedback on generated ontology
- Automatic regeneration based on feedback
- Clear instructions and tips

✅ **Ontology Confirmation**
- Review generated ontology
- Confirm or request changes
- Save to knowledge graph

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **react-force-graph-2d** - Graph visualization
- **Axios** - HTTP client
- **Lucide React** - Beautiful icons
- **React Hot Toast** - Toast notifications

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Usage

### 1. Upload Transcript
- Click or drag & drop a transcript file (.txt, .md, .json)
- Click "Upload Transcript" button
- Wait for confirmation

### 2. Generate Ontology
- After successful upload, click "Generate Ontology"
- Wait for the AI to process and generate the ontology
- The graph will automatically appear

### 3. View & Interact with Graph
- **Zoom**: Use mouse wheel or zoom buttons
- **Pan**: Click and drag on empty space
- **Move nodes**: Click and drag individual nodes
- **View details**: Click on any node to see its properties
- **Fit view**: Click the maximize button to fit all nodes

### 4. Provide Feedback (Optional)
- Click "Provide Feedback" button
- Describe what needs to be changed
- Submit to regenerate ontology

### 5. Confirm Ontology
- Once satisfied, click "Confirm Ontology"
- The ontology will be saved to the knowledge graph

## Graph Legend

- 🔵 **Blue (Concept)** - Abstract concepts
- 🟢 **Green (Entity)** - Concrete entities
- 🟡 **Yellow (Attribute)** - Attributes
- 🟣 **Purple (Process)** - Processes/Actions

## API Integration

The frontend communicates with the backend API through a proxy configuration:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Proxy: `/api` → `http://localhost:8000`

All API calls are handled through the `src/services/api.js` service.

## Build for Production

```bash
npm run build
```

The production build will be in the `dist` directory.

## Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx              # App header
│   │   ├── UploadSection.jsx       # File upload component
│   │   ├── OntologyViewer.jsx      # Graph visualization
│   │   └── FeedbackModal.jsx       # Feedback modal
│   ├── services/
│   │   └── api.js                  # API service
│   ├── App.jsx                     # Main app component
│   ├── App.css                     # App styles
│   ├── main.jsx                    # Entry point
│   └── index.css                   # Global styles
├── index.html                      # HTML template
├── vite.config.js                  # Vite configuration
└── package.json                    # Dependencies
```

## Customization

### Colors
Edit the gradient colors in CSS files:
- Primary gradient: `#667eea` to `#764ba2`
- Success: `#10b981`
- Warning: `#f59e0b`

### Graph Appearance
Modify graph settings in `OntologyViewer.jsx`:
- Node sizes
- Link colors
- Force simulation parameters
- Label styles

## Troubleshooting

**Graph not rendering:**
- Check browser console for errors
- Ensure backend API is running
- Verify ontology data structure

**Upload failing:**
- Check file format (.txt, .md, .json)
- Verify file size (max 50MB)
- Ensure backend is accessible

**Slow performance:**
- Reduce number of nodes/links
- Adjust force simulation parameters
- Use production build

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Modern mobile browsers

## License

MIT
