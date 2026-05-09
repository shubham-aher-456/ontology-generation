# Frontend Setup Guide

## Quick Start

### Prerequisites
- Node.js 16+ and npm installed
- Backend API running on `http://localhost:8000`

### Installation Steps

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```

4. **Open browser:**
Navigate to `http://localhost:3000`

---

## What You'll See

### 1. Beautiful Landing Page
- Modern gradient design
- Clean, professional interface
- Responsive layout

### 2. Upload Section
- Drag & drop file upload
- Support for .txt, .md, .json files
- Real-time feedback

### 3. Interactive Graph Visualization
- **Force-directed layout** - Nodes automatically arrange themselves
- **Color-coded entities** - Different colors for different entity types
- **Interactive controls:**
  - Zoom in/out with mouse wheel or buttons
  - Pan by dragging
  - Click nodes to see details
  - Drag nodes to rearrange

### 4. Node Details Panel
- Click any node to see:
  - Entity name and type
  - Description
  - Properties with data types
  - Required fields

### 5. Feedback System
- Provide specific feedback
- AI regenerates ontology based on your input
- Iterative improvement process

---

## Features Showcase

### 🎨 Visual Design
- **Gradient backgrounds** - Purple to blue gradient
- **Smooth animations** - Fade-in effects, hover states
- **Glass morphism** - Frosted glass effects
- **Shadows & depth** - Modern card-based layout

### 📊 Graph Visualization
- **Node sizing** - Larger nodes for entities with more properties
- **Directional arrows** - Show relationship direction
- **Relationship labels** - See connection types
- **Legend** - Understand entity types at a glance

### 🔄 User Flow
1. Upload transcript → Success notification
2. Generate ontology → Loading indicator
3. View graph → Interactive exploration
4. Provide feedback (optional) → Regeneration
5. Confirm → Save to database

---

## Graph Interaction Guide

### Zoom Controls
- **Mouse Wheel** - Scroll to zoom in/out
- **Zoom In Button** - Click + button
- **Zoom Out Button** - Click - button
- **Fit View** - Click maximize button to fit all nodes

### Node Interaction
- **Click** - View node details in side panel
- **Drag** - Move node to new position
- **Hover** - See node name tooltip

### Navigation
- **Pan** - Click and drag on empty space
- **Reset** - Click fit view button

---

## Color Coding

| Color | Type | Description |
|-------|------|-------------|
| 🔵 Blue (#667eea) | Concept | Abstract concepts and ideas |
| 🟢 Green (#10b981) | Entity | Concrete entities and objects |
| 🟡 Yellow (#f59e0b) | Attribute | Properties and attributes |
| 🟣 Purple (#8b5cf6) | Process | Processes and actions |
| 🔴 Red (#ef4444) | Relationship | Relationship types |
| 🩷 Pink (#ec4899) | Event | Events and occurrences |

---

## Example Workflow

### Step 1: Upload Transcript
```
1. Click the upload area or drag a file
2. Select a .txt file with meeting notes
3. Click "Upload Transcript"
4. See success message with transcript ID
```

### Step 2: Generate Ontology
```
1. Click "Generate Ontology" button
2. Wait for AI processing (10-30 seconds)
3. Graph appears automatically
4. See entity and relationship counts
```

### Step 3: Explore Graph
```
1. Zoom in to see details
2. Click on "Customer" node
3. View properties: name, email, phone
4. See relationships to other entities
5. Drag nodes to organize layout
```

### Step 4: Provide Feedback (Optional)
```
1. Click "Provide Feedback"
2. Type: "Add a relationship between Customer and Payment"
3. Click "Submit & Regenerate"
4. New graph appears with changes
```

### Step 5: Confirm
```
1. Review final ontology
2. Click "Confirm Ontology"
3. Data saved to Neo4j knowledge graph
4. Success notification appears
```

---

## Troubleshooting

### Issue: "Cannot connect to backend"
**Solution:**
- Ensure backend is running: `python -m uvicorn src.main:app --reload`
- Check backend URL: `http://localhost:8000`
- Verify CORS is enabled in backend

### Issue: "Graph not rendering"
**Solution:**
- Check browser console for errors
- Ensure ontology data is valid
- Try refreshing the page
- Clear browser cache

### Issue: "Upload fails"
**Solution:**
- Check file format (.txt, .md, .json only)
- Verify file size (max 50MB)
- Ensure file contains valid text
- Check backend logs for errors

### Issue: "Slow performance"
**Solution:**
- Use production build: `npm run build`
- Reduce graph complexity
- Close other browser tabs
- Use Chrome for best performance

---

## Advanced Configuration

### Change Backend URL
Edit `frontend/vite.config.js`:
```javascript
proxy: {
  '/api': {
    target: 'http://your-backend-url:8000',
    changeOrigin: true,
  }
}
```

### Customize Colors
Edit component CSS files:
- `Header.css` - Header colors
- `UploadSection.css` - Upload area colors
- `OntologyViewer.css` - Graph colors

### Adjust Graph Physics
Edit `OntologyViewer.jsx`:
```javascript
cooldownTicks={100}        // Simulation duration
d3AlphaDecay={0.02}       // Cooling rate
d3VelocityDecay={0.3}     // Friction
```

---

## Production Deployment

### Build for Production
```bash
npm run build
```

### Serve Static Files
```bash
npm run preview
```

### Deploy to Server
1. Copy `dist` folder to web server
2. Configure reverse proxy to backend
3. Set up SSL certificate
4. Configure CORS on backend

---

## Browser Compatibility

✅ **Fully Supported:**
- Chrome 90+
- Edge 90+
- Firefox 88+
- Safari 14+

⚠️ **Limited Support:**
- IE 11 (not recommended)
- Older mobile browsers

---

## Performance Tips

1. **Use production build** for better performance
2. **Limit graph size** to 100-200 nodes for smooth interaction
3. **Close unused tabs** to free up memory
4. **Use Chrome** for best WebGL performance
5. **Enable hardware acceleration** in browser settings

---

## Support

For issues or questions:
1. Check browser console for errors
2. Review backend logs
3. Verify API endpoints are accessible
4. Check network tab in browser DevTools

---

## Next Steps

After setup:
1. ✅ Upload a sample transcript
2. ✅ Generate your first ontology
3. ✅ Explore the interactive graph
4. ✅ Try the feedback system
5. ✅ Confirm and save to knowledge graph

Enjoy building knowledge graphs! 🚀
