# 🎨 MT4 Risk Management Calculator Frontend

A modern, responsive frontend for the MT4 Risk Management Calculator.

## 📋 Overview

This frontend provides a user-friendly interface for:
- Uploading MT4 HTML statements
- Viewing comprehensive trading analysis
- Analyzing individual trade R-Multiple metrics
- Using the risk calculator for position sizing

## 🎯 Features

- **Modern Dark Theme**: Tradezella-inspired professional design
- **Responsive Layout**: Works on desktop and mobile devices
- **Interactive Cards**: Collapsible result sections
- **Trade Analysis Table**: Detailed view of individual trades
- **Risk Calculator**: Interactive position sizing tool
- **Toast Notifications**: User-friendly status messages

## 🧩 Components

### 1. File Upload Section
- Drag-and-drop file upload
- File type validation
- Progress indicator

### 2. Analysis Results Section
- Account information card
- Trading summary card
- Financial summary card
- Performance metrics card
- R-Multiple analysis card
- Individual trade analysis table

### 3. Risk Calculator
- Trade setup inputs
- Position sizing calculator
- Risk level indicator
- Recommendations

## 🎨 Design Elements

### Color Palette
- Primary Background: `#0d1421`
- Secondary Background: `#1a1f2e`
- Card Background: `#1e2329`
- Border Color: `#2e3339`
- Text Primary: `#ffffff`
- Text Secondary: `#b7bdc6`
- Accent Blue: `#2196f3`
- Accent Green: `#00c851`
- Accent Red: `#ff4444`

### Typography
- Primary Font: 'Inter', sans-serif
- Monospace Font: 'SF Mono', 'Monaco', monospace
- Base Font Size: 14px

## 🔧 Technical Implementation

### HTML Structure
- Semantic HTML5 elements
- Responsive grid layout
- Accessible form controls

### CSS Features
- CSS Variables for theming
- Flexbox and Grid layouts
- Responsive design with media queries
- Animations and transitions
- Dark theme optimization

### JavaScript Functionality
- Modular class-based architecture
- Asynchronous API communication
- Dynamic content generation
- Form validation and submission
- Error handling and notifications

## 📱 Responsive Behavior

The frontend is fully responsive and adapts to different screen sizes:
- **Desktop**: Multi-column grid layout
- **Tablet**: Reduced columns, optimized spacing
- **Mobile**: Single column layout, touch-friendly controls

## 🔄 API Integration

The frontend communicates with the backend API for:
- File uploads and analysis
- Risk calculator calculations
- Health checks and status updates

## 🚀 Getting Started

The frontend is served directly by the FastAPI backend at `http://localhost:5501`.

To make changes to the frontend:
1. Edit the HTML, CSS, or JavaScript files
2. Restart the server to see your changes
3. For development, you can use browser developer tools to test changes