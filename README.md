# 🎯 SERP Master

AI-Powered SEO Intelligence Platform built with React TypeScript, FastAPI, CopilotKit, and DataForSEO APIs.

## Features

- 🤖 **Conversational SEO Assistant** - Chat with AI to analyze keywords, track rankings, and get SEO insights
- 🔍 **Keyword Research** - Real-time keyword analysis with search volume and competition data
- 📊 **SERP Analysis** - Analyze search engine results pages for any query
- 🎯 **Competitor Intelligence** - Track and analyze competitor SEO strategies
- 📈 **Rankings Tracker** - Monitor your keyword rankings over time

## Tech Stack

### Frontend
- React 18 with TypeScript
- Vite for fast development
- CopilotKit for AI chat interface
- Lucide React for icons

### Backend
- FastAPI for high-performance API
- CopilotKit SDK for AI agent orchestration
- LangGraph for agent workflow
- DataForSEO APIs for SEO data

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- OpenAI API key
- DataForSEO account (optional - mock data available)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd serp-master
   ```

2. **Set up the frontend:**
   ```bash
   cd frontend
   npm install
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Set up the backend:**
   ```bash
   cd ../backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Running the Application

1. **Start the backend (from backend directory):**
   ```bash
   python main.py
   # API will run on http://localhost:8000
   ```

2. **Start the frontend (from frontend directory):**
   ```bash
   npm run dev
   # App will run on http://localhost:3000
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000` and start chatting with the SEO assistant!

## Environment Variables

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
VITE_COPILOTKIT_API_URL=http://localhost:8000/api/copilotkit
```

### Backend (.env)
```
OPENAI_API_KEY=your_openai_api_key_here
DATAFORSEO_LOGIN=your_dataforseo_login
DATAFORSEO_PASSWORD=your_dataforseo_password
CORS_ORIGINS=http://localhost:3000
```

## Usage Examples

Try asking the AI assistant:
- "Analyze the keyword 'react tutorials'"
- "Show me SERP results for 'best seo tools 2024'"
- "Compare competitor example.com"
- "What are the top keywords I should target?"
- "Switch to the keywords view"

## Project Structure

```
serp-master/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── SERPMasterDashboard.tsx
│   │   │   └── SERPMasterDashboard.css
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── agents/
│   │   └── seo_agent.py
│   ├── tools/
│   │   └── dataforseo_tools.py
│   ├── main.py
│   └── requirements.txt
└── README.md
```

## Architecture

SERP Master follows a modern architecture pattern inspired by successful commercial platforms:

- **CopilotKit Integration**: Seamless AI chat interface with action handlers
- **LangGraph Agents**: Structured AI workflows for SEO tasks
- **FastAPI Backend**: High-performance async API with automatic docs
- **React Frontend**: Modern, responsive UI with real-time updates

## Development

### Frontend Development
```bash
cd frontend
npm run dev    # Start dev server
npm run build  # Build for production
npm run lint   # Run linter
```

### Backend Development
```bash
cd backend
python main.py           # Start development server
# API docs available at http://localhost:8000/docs
```

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
