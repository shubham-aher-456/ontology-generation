# 🚀 Quick Start Guide - Ontology Knowledge Base

## Complete Setup in 5 Minutes

### ✅ Backend is Already Running!
Your backend API is running on `http://localhost:8000` with all services connected.

---

## 🎨 Frontend Setup

### Step 1: Install Node.js (if not installed)
Download from: https://nodejs.org/ (LTS version recommended)

### Step 2: Open New Terminal/Command Prompt
Navigate to your project directory:
```bash
cd C:\Users\DA15\Desktop\RR
```

### Step 3: Install Frontend Dependencies
```bash
cd frontend
npm install
```

**Note:** This may take 2-3 minutes. Wait for it to complete.

### Step 4: Start Frontend
```bash
npm run dev
```

### Step 5: Open Browser
Navigate to: `http://localhost:3000`

---

## 🎯 Alternative: Quick Start Script

Simply double-click: **`start-frontend.bat`**

This will:
1. Check for dependencies
2. Install if needed
3. Start the development server

---

## 📱 Using the Application

### 1️⃣ Upload Transcript
- Drag & drop a `.txt` file OR click to browse
- Click **"Upload Transcript"** button
- Wait for success message ✅

### 2️⃣ Generate Ontology
- Click **"Generate Ontology"** button
- Wait 10-30 seconds for AI processing
- Beautiful graph appears automatically! 🎨

### 3️⃣ Explore the Graph
**Interactive Controls:**
- 🖱️ **Mouse Wheel** - Zoom in/out
- 🖱️ **Click & Drag** - Pan around
- 🖱️ **Click Node** - View details
- 🖱️ **Drag Node** - Rearrange layout
- 🔍 **Zoom Buttons** - Top right corner
- 📐 **Fit View** - See all nodes

**Graph Features:**
- Color-coded entities (Blue=Concept, Green=Entity, Yellow=Attribute)
- Directional arrows showing relationships
- Labels on connections
- Node size based on properties
- Legend in top-right corner

### 4️⃣ Provide Feedback (Optional)
- Click **"Provide Feedback"** button
- Describe what needs to change:
  ```
  Example:
  - Add relationship between Customer and Payment
  - Remove duplicate Product entity
  - Add status attribute to Order
  ```
- Click **"Submit & Regenerate"**
- New ontology generated with your feedback! 🔄

### 5️⃣ Confirm Ontology
- Review the final graph
- Click **"Confirm Ontology"** button
- Saved to Neo4j knowledge graph! 💾

---

## 🎨 What You'll See

### Beautiful Modern UI
```
┌─────────────────────────────────────────────┐
│  🌐 Ontology Knowledge Base                 │
│  Transform transcripts into knowledge graphs│
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  📄 Upload Transcript                       │
│  ┌───────────────────────────────────────┐ │
│  │   📁 Drag & drop your transcript      │ │
│  │      or click to browse               │ │
│  │   Supported: .txt, .md, .json         │ │
│  └───────────────────────────────────────┘ │
│  [Upload Transcript] [Generate Ontology]   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  🌐 Generated Ontology Graph                │
│  [13 Entities] [12 Relationships]           │
│  [🔍+] [🔍-] [📐]                           │
│  ┌───────────────────────────────────────┐ │
│  │                                       │ │
│  │    🔵 Customer ──→ 🟢 Order          │ │
│  │         ↓              ↓              │ │
│  │    🟡 Database    🟣 Product         │ │
│  │                                       │ │
│  │  Interactive Force-Directed Graph    │ │
│  │  Click nodes • Drag to rearrange     │ │
│  │  Zoom & Pan • View relationships     │ │
│  │                                       │ │
│  └───────────────────────────────────────┘ │
│  [💬 Provide Feedback] [✅ Confirm]        │
└─────────────────────────────────────────────┘
```

---

## 🎯 Sample Workflow

### Example: Product Management System

**1. Create transcript file** (`product_system.txt`):
```
Meeting Notes: Product Management System

We need a system to manage products and orders.
Each product has a name, price, and category.
Customers can place orders containing multiple products.
Orders have a status: pending, shipped, or delivered.
Each customer has a name, email, and shipping address.
```

**2. Upload & Generate:**
- Upload the file
- Click "Generate Ontology"
- Wait for processing

**3. View Generated Graph:**
```
Customer ──places──→ Order ──contains──→ Product
   ↓                   ↓                    ↓
 name              status                 name
 email             date                   price
 address                                  category
```

**4. Provide Feedback (if needed):**
```
Add a Payment entity
Connect Order to Payment with "paid_by" relationship
Add payment_method attribute to Payment
```

**5. Confirm:**
- Review updated graph
- Click "Confirm Ontology"
- Done! ✅

---

## 🎨 Graph Color Legend

| Color | Type | Example |
|-------|------|---------|
| 🔵 Blue | Concept | Customer Management System |
| 🟢 Green | Entity | Customer, Order, Product |
| 🟡 Yellow | Attribute | name, email, price |
| 🟣 Purple | Process | Payment Processing |
| 🔴 Red | Relationship | places_order, contains |
| 🩷 Pink | Event | Order Placed, Payment Received |

---

## 🔧 Troubleshooting

### Frontend won't start
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules
npm install
```

### Port 3000 already in use
Edit `frontend/vite.config.js`:
```javascript
server: {
  port: 3001,  // Change to different port
  ...
}
```

### Can't connect to backend
1. Check backend is running: `http://localhost:8000/health`
2. Verify no firewall blocking
3. Check browser console for errors

### Graph not rendering
1. Try Chrome browser (best performance)
2. Clear browser cache
3. Check console for errors
4. Refresh page

---

## 📊 System Status Check

### Backend Health
Open: `http://localhost:8000/health`

Should see:
```json
{
  "status": "healthy",
  "service": "ontology-knowledge-base",
  "version": "1.0.0"
}
```

### Frontend Health
Open: `http://localhost:3000`

Should see: Beautiful landing page with upload section

### Services Status
- ✅ PostgreSQL: Port 5433
- ✅ Neo4j: Port 7688 (Bolt), 7475 (HTTP)
- ✅ Redis: Port 6380
- ✅ Backend API: Port 8000
- ⏳ Frontend: Port 3000 (after npm run dev)

---

## 🎓 Tips for Best Experience

### 1. Use Chrome Browser
Best performance for graph visualization

### 2. Start with Small Transcripts
Test with 100-500 words first

### 3. Be Specific in Feedback
Instead of: "Fix the graph"
Use: "Add relationship between Customer and Payment entity"

### 4. Explore Interactively
- Click every node to see details
- Drag nodes to organize layout
- Use zoom to focus on areas

### 5. Save Your Work
Click "Confirm Ontology" to save to Neo4j database

---

## 📁 Project Structure

```
RR/
├── backend/
│   ├── src/
│   │   ├── main.py              ✅ Running on :8000
│   │   ├── services/            ✅ All services working
│   │   └── domain/              ✅ Models defined
│   └── config/                  ✅ Configured
│
├── frontend/                    ⏳ Ready to start
│   ├── src/
│   │   ├── components/          ✅ All components created
│   │   │   ├── Header.jsx
│   │   │   ├── UploadSection.jsx
│   │   │   ├── OntologyViewer.jsx
│   │   │   └── FeedbackModal.jsx
│   │   ├── services/
│   │   │   └── api.js           ✅ API integration ready
│   │   ├── App.jsx              ✅ Main app
│   │   └── main.jsx             ✅ Entry point
│   ├── package.json             ✅ Dependencies defined
│   └── vite.config.js           ✅ Configured
│
├── docker-compose.yml           ✅ Services running
└── start-frontend.bat           ✅ Quick start script
```

---

## 🚀 Next Steps

1. **Install dependencies** (if not done):
   ```bash
   cd frontend
   npm install
   ```

2. **Start frontend**:
   ```bash
   npm run dev
   ```

3. **Open browser**:
   ```
   http://localhost:3000
   ```

4. **Upload a transcript** and see the magic! ✨

---

## 💡 Pro Tips

### Create Better Ontologies
- Use clear, descriptive language in transcripts
- Mention entities explicitly
- Describe relationships clearly
- Include attributes and properties

### Optimize Graph Layout
- Drag important nodes to center
- Group related entities together
- Use zoom to focus on sections
- Click "Fit View" to reset

### Iterate with Feedback
- Start with basic ontology
- Provide specific feedback
- Regenerate and refine
- Confirm when satisfied

---

## 🎉 You're All Set!

Your Ontology Knowledge Base is ready to transform transcripts into beautiful, interactive knowledge graphs!

**Questions?** Check the detailed guides:
- `FRONTEND_SETUP.md` - Detailed frontend setup
- `frontend/README.md` - Frontend documentation
- `API_TEST_RESULTS.md` - API test results

**Enjoy building knowledge graphs!** 🚀📊🎨
