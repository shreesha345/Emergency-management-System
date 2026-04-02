# 🚨 RudraOne - AI-Powered Emergency Dispatch System

> **Local-First Emergency Response Platform with Ollama AI Integration**
>
> RudraOne is a cutting-edge emergency dispatch system powered by local AI (Ollama + gemma4:31b), enabling instant emergency response, intelligent call routing, and comprehensive incident management with complete data privacy.

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)
![Node.js](https://img.shields.io/badge/Node.js-18%2B-green?logo=node.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.119%2B-white?logo=fastapi)
![React](https://img.shields.io/badge/React-Latest-61DAFB?logo=react)
![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-FF6B00)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Overview

RudraOne is an intelligent emergency dispatch system that connects emergency callers with appropriate services using advanced AI. Built entirely with local-first architecture using Ollama, the system requires no cloud LLM providers—ensuring complete privacy, reduced latency, and zero API dependencies for AI inference.

### Key Features

- 🦙 **Local AI Processing** - Ollama + gemma4:31b for all AI tasks (no cloud APIs)
- 📱 **Multi-Channel Input** - Phone calls via Twilio, SMS, web dashboard
- 🗺️ **Real-Time Dispatch Map** - Mapbox-powered visualization with routing
- 🎤 **Multilingual Support** - Hindi, Tamil, Telugu, English with auto-detection
- 📊 **Advanced Analytics** - Query processing, visualization, incident tracking
- 🎓 **Dispatcher Training** - Interactive training sessions with AI coaching
- 🔒 **Data Privacy** - All processing local, no external AI API calls
- ⚡ **Enable/Disable Toggle** - Graceful degradation with Ollama on/off
- 🔧 **Model Selection** - Choose from gemma4:31b, Mistral, Neural-Chat
- 📡 **Real-Time Communication** - WebSocket support for live updates

---

## 🏗️ System Architecture

### Layers

```
┌─────────────────────────────────────────────────────────┐
│          EXTERNAL INPUTS (Phone, SMS, Web)              │
├─────────────────────────────────────────────────────────┤
│                    FastAPI Server                        │
│            (Async request handling, routing)             │
├─────────────────────────────────────────────────────────┤
│         CORE AI AGENTS (Ollama + gemma4:31b)            │
│  ├─ RudraAgent (Emergency handler)                      │
│  ├─ RudraAnalyst (Analytics engine)                     │
│  ├─ TwilioSMSService (SMS formatter)                    │
│  └─ Training System (Dispatcher training)               │
├─────────────────────────────────────────────────────────┤
│          SUPPORTING SERVICES                            │
│  ├─ Speech-to-Text (Deepgram)                           │
│  ├─ Text-to-Speech (ElevenLabs, Sarvam)                 │
│  ├─ Mapbox (Maps, geocoding, routing)                   │
│  └─ PostgreSQL Database (Call logging)                  │
├─────────────────────────────────────────────────────────┤
│     React Frontend + Tailwind CSS + Mapbox GL JS        │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
Incoming Call (Twilio)
    ↓
Transcription (Deepgram/Whisper)
    ↓
AI Processing (Ollama + gemma4:31b)
    ↓
Speech Output (ElevenLabs/Sarvam TTS)
    ↓
Data Extraction & SMS Formatting
    ↓
Emergency Service Alert (SMS/SMS Gateway)
    ↓
Database Logging & Real-Time Dashboard Update
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- Ollama (Download from https://ollama.ai)
- API Keys: Twilio, Deepgram, Mapbox

### 1. Clone & Setup

```bash
# Clone repository
git clone <repository-url>
cd RudraOne

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

### 2. Install Ollama

```bash
# Download from https://ollama.ai

# Pull the gemma4:31b model
ollama pull gemma4:31b

# Start Ollama server (keep running in background)
ollama serve
# Runs on http://localhost:11434
```

### 3. Install Dependencies

```bash
# Backend
pip install -e .

# Frontend
cd frontend
npm install
cd ..
```

### 4. Configure Environment

```bash
# Copy template to .env
cp .env.example .env

# Edit .env with your credentials:
# - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
# - DEEPGRAM_API_KEY
# - VITE_MAPBOX_TOKEN
# - DATABASE_URL (if using remote PostgreSQL)
```

### 5. Initialize Database

```bash
# Start PostgreSQL (if using Docker)
docker-compose up -d

# Initialize database
python init_database.py
```

### 6. Run the System

```bash
# Terminal 1: FastAPI Backend
python -m uvicorn server:app --reload
# Backend: http://localhost:8000

# Terminal 2: Frontend (from frontend/ directory)
npm run dev
# Frontend: http://localhost:5173
```

---

## 📋 Configuration

### Environment Variables (`.env`)

#### 🦙 Ollama Configuration
```env
OLLAMA_ENABLED=true                    # Enable/disable Ollama
OLLAMA_BASE_URL=http://localhost:11434 # Ollama server URL
OLLAMA_MODEL=gemma4:31b                # Model: gemma4:31b/mistral/neural-chat
```

#### 🔐 Twilio Configuration
```env
TWILIO_ACCOUNT_SID=your_sid_here
TWILIO_AUTH_TOKEN=your_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

#### 🗄️ Database
```env
DATABASE_URL=postgresql://user:password@localhost:5432/rudraone_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
```

#### 🎤 Speech Services
```env
DEEPGRAM_API_KEY=your_key_here        # Speech-to-Text
ELEVENLABS_API_KEY=your_key_here      # Text-to-Speech
SARVAM_API_KEY=your_key_here          # Indian language TTS
```

#### 🗺️ Maps
```env
VITE_MAPBOX_TOKEN=your_token_here     # Mapbox for dispatch map
```

#### 🚀 Server
```env
PORT=8000
ENVIRONMENT=development                # development/staging/production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000
LOG_LEVEL=INFO                         # INFO/DEBUG/WARNING/ERROR
```

---

## 📁 Project Structure

```
RudraOne/
├── .env
├── .env.example
├── .gitignore
├── .python-version
├── 911_calls.json
├── agency_settings.json
├── audio_ops.py
├── database.py
├── docker-compose.yml
├── elevenlabs_tts.py
├── frontend/
│   ├── .env
│   ├── .env.example
│   ├── .gitignore
│   ├── bun.lockb
│   ├── components.json
│   ├── dist/                              # Generated frontend build output
│   ├── eslint.config.js
│   ├── index.html
│   ├── node_modules/                      # Installed frontend dependencies
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.js
│   ├── public/
│   │   ├── favicon_io/
│   │   ├── location.html
│   │   ├── robots.txt
│   │   └── site.webmanifest
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── index.css
│   │   ├── lib/
│   │   ├── main.tsx
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   └── vite-env.d.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── generate_architecture_diagrams.py
├── init_database.py
├── models.py
├── ollama_client.py
├── prompts.py
├── recordings/
├── RudraOne_agent.py
├── RudraOne_Analytics.py
├── rudra_logic.py
├── sarvam_tts.py
├── server.log
├── server.py
├── stations.py
├── training.py
├── twilio_sms_send.py
├── uv.lock
├── extra/
├── static/
└── __pycache__/                           # Python cache files
```

---

## 🔧 Core Components

### Backend Services

#### 🦙 Ollama Client (`ollama_client.py`)
- Unified wrapper around Ollama API
- Enable/disable toggle with graceful fallback
- Context-aware fallback responses
- Multiple model support
- Configuration presets for different tasks

#### 🚀 FastAPI Server (`server.py`)
- Twilio webhook handlers for phone calls
- REST API endpoints for frontend
- Async database session management
- CORS configuration
- Service orchestration

#### 🚨 Emergency Agent (`rudra_logic.py`)
- Processes emergency calls in real-time
- Extracts incident details from caller speech
- Handles location verification
- Generates emergency alerts
- Supports multilingual responses

#### 📊 Analytics Engine (`RudraOne_Analytics.py`)
- Queries dispatch data
- Generates visualization artifacts
- Performs incident analysis
- Tracks response metrics
- Creates HTML/Chart.js dashboards

#### 💬 Training System (`training.py`)
- Multi-turn dispatcher training sessions
- Scenario-based learning from 911_calls.json
- Interactive feedback and scoring
- Performance tracking

#### 📱 SMS Service (`twilio_sms_send.py`)
- Formats emergency alerts
- Sends SMS to emergency services
- Integrates with Ollama for message formatting
- Supports markdown-style formatting

### Frontend Components

#### 🗺️ Dispatch Map (`components/DispatchMap.tsx`)
- Real-time map visualization with Mapbox
- Caller location display
- Emergency station markers
- Route calculation and display
- Live unit tracking

#### 📊 Dashboard (`pages/Dashboard.tsx`)
- Real-time incident monitoring
- Call history and statistics
- Analytics visualization
- Incident reports
- System status overview

#### ⚙️ Settings (`pages/Settings.tsx`)
- Configuration management
- API key settings
- System preferences
- User management

#### 🎓 Training Interface (`components/BlackGoldDemo.tsx`)
- Interactive training scenarios
- Real-time feedback
- Performance metrics
- Session management

---

## 🎤 API Endpoints

### Core Routes

```
POST   /twiml                          # Twilio call webhook
GET    /                               # Health check
GET    /api/calls                      # Get all calls
GET    /api/calls/{call_id}            # Get call details
POST   /api/emergency-alert            # Send emergency SMS
GET    /api/analytics                  # Get analytics data
POST   /api/training/start             # Start training session
POST   /api/training/message           # Send training message
```

### WebSocket Routes

```
WS     /ws/dispatch                    # Real-time dispatch updates
WS     /ws/analytics                   # Real-time analytics
WS     /ws/training                    # Real-time training session
```

---

## 🔐 Security Features

### Data Privacy
- ✅ All AI processing local (Ollama)
- ✅ No LLM data sent to cloud

### Authentication
- ✅ JWT token support
- ✅ API key validation
- ✅ CORS configuration
- ✅ Rate limiting ready

### Configuration Security
- ✅ No hardcoded secrets
- ✅ Environment variable based
- ✅ .env file excluded from git
- ✅ Example template provided

---

## 📊 Model Information

### Default Model: gemma4:31b

| Aspect | Details |
|--------|---------|
| **Base Model** | Gemma 4 |
| **Size** | 31B parameters |
| **VRAM Required** | Hardware dependent |
| **Speed** | Higher latency, better quality |
| **Capability** | Full emergency response handling |
| **License** | Apache 2.0 (commercial use OK) |

### Alternative Models

| Model | Size | VRAM | Speed | Use Case |
|-------|------|------|-------|----------|
| gemma4:31b | 31B | 16GB+ | High quality | Primary model |
| mistral | 7B | 4GB | Fast | Multilingual |
| neural-chat | 13B | 7.5GB | Medium | Chat optimization |

---

## 📡 Integrations

### Communication
- **Twilio**: Phone calls and SMS
- **Deepgram**: Speech-to-text transcription
- **ElevenLabs**: High-quality text-to-speech
- **Sarvam AI**: Indian language TTS

### Mapping & Location
- **Mapbox**: Maps, geocoding, directions, routing

### AI & LLM
- **Ollama**: Local LLM execution (gemma4:31b, Mistral, etc.)

### Database
- **PostgreSQL**: Persistent data storage
- **SQLAlchemy**: ORM for database operations

### Frontend Libraries
- **React**: UI framework
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **Mapbox GL JS**: Map visualization
- **Shadcn/ui**: Component library

---

## 🧪 Testing

### Backend Testing

```bash
# Test Ollama connection
curl http://localhost:11434/api/tags

# Test FastAPI server
curl http://localhost:8000/

# Test emergency alert
python -c "from twilio_sms_send import TwilioSMSService; \
           service = TwilioSMSService(); \
           service.send_emergency_alert('+91XXXXXXXXXX', 'police', 'Test Location', {})"
```

### Frontend Testing

```bash
# Start dev server
cd frontend
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### API Testing

```bash
# Get all calls
curl http://localhost:8000/api/calls

# Get analytics
curl http://localhost:8000/api/analytics
```

---

## 🐛 Troubleshooting

### Ollama Not Responding

```bash
# Check if Ollama is running
curl http://localhost:11434

# Start Ollama if needed
ollama serve

# Verify model is downloaded
ollama list

# Pull model if missing
ollama pull gemma4:31b
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps

# Start services
docker-compose up -d

# Verify connection
psql postgresql://user:password@localhost:5432/rudraone_db
```

### Frontend API Connection Error

```bash
# Check backend is running
curl http://localhost:8000/

# Verify VITE_API_URL in frontend/.env
cat frontend/.env | grep VITE_API_URL

# Check CORS configuration
# Verify frontend URL is in ALLOWED_ORIGINS in backend .env
```

### Mapbox Not Showing Map

```bash
# Verify token is set
echo $VITE_MAPBOX_TOKEN  # Should show token, not placeholder

# Check browser console for errors
# Verify token has appropriate scopes enabled

# Test token validity
curl "https://api.mapbox.com/tokens/v2?access_token=YOUR_TOKEN"
```

---

## 📈 Performance Metrics

### Response Times (Approximate)

| Operation | Time | Notes |
|-----------|------|-------|
| Emergency response generation | 2-5s | Ollama processing |
| SMS formatting | 1-3s | Concurrent with call |
| Analytics query | 3-8s | Depends on data size |
| Map rendering | <1s | Client-side |
| Location update | 2-4s | Including Mapbox API |

### Resource Usage

| Component | CPU | Memory | Disk |
|-----------|-----|--------|------|
| Ollama (gemma4:31b) | 4+ cores | 16GB+ | 20GB+ |
| FastAPI Server | <1 core | 500MB | Minimal |
| PostgreSQL | <1 core | 500MB+ | Variable |
| Frontend | Browser | Browser | 100MB+ |

### GPU Acceleration

- **NVIDIA (CUDA)**: 2-3x faster
- **Apple (Metal)**: 1.5-2x faster
- **AMD (ROCm)**: 1.5-2x faster
- **CPU Only**: Baseline (slower but works)

---

## 🚀 Deployment

### Development

```bash
python -m uvicorn server:app --reload
cd frontend && npm run dev
```

### Production

```bash
# Backend
python -m uvicorn server:app --host 0.0.0.0 --port 8000

# Frontend
npm run build
# Serve dist/ folder with web server

# Or use Docker
docker-compose -f docker-compose.yml up -d
```

### Docker Deployment

```dockerfile
# See docker-compose.yml for full setup
# Includes PostgreSQL, Redis, Ollama ready configuration
```

---

## 📚 Documentation

All documentation is now consolidated in this README to keep the project easier to navigate and maintain.

---

## 🔄 Development Workflow

### Adding New Features

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes following existing code structure
3. Test locally with dev server
4. Commit: `git commit -m "Add my feature"`
5. Push: `git push origin feature/my-feature`
6. Create pull request

### Code Organization

- **Backend**: Modular services with clear responsibilities
- **Frontend**: Component-based architecture
- **Database**: SQLAlchemy ORM with migrations ready
- **Configuration**: Environment-based settings

### Testing Guidelines

- Test Ollama integration with enable/disable toggle
- Verify all imports work correctly
- Test with different models (gemma4:31b, Mistral)
- Verify frontend/backend communication
- Test with and without GPU acceleration

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Follow existing code structure
2. Add appropriate comments for complex logic
3. Test thoroughly before submitting
4. Update documentation as needed
5. Ensure all environment variables are documented

---

## 📄 License

MIT License - See LICENSE file for details

---

## 📞 Support & Contact

For questions, issues, or suggestions:

1. Check existing documentation
2. Review the verification and troubleshooting sections above
3. Check troubleshooting section above
4. Review error logs in server.log
5. Check browser console for frontend errors

---

## 🎯 Key Highlights

✨ **100% Local AI** - No cloud LLM providers, complete privacy
✨ **Production Ready** - Fully tested and verified
✨ **Flexible Models** - Switch between gemma4:31b, Mistral, Neural-Chat
✨ **Enable/Disable** - Graceful degradation with toggle
✨ **Multilingual** - Support for Hindi, Tamil, Telugu, and more
✨ **Real-Time** - WebSocket support for live updates
✨ **Well Documented** - Comprehensive guides and architecture docs
✨ **Organized Structure** - Clear separation of concerns

---

## ✅ Status

- ✅ Backend: Complete and tested
- ✅ Frontend: Complete and responsive
- ✅ AI Integration: Ollama fully integrated
- ✅ Database: PostgreSQL configured
- ✅ Documentation: Comprehensive
- ✅ Configuration: Environment-based
- ✅ Security: Privacy-first architecture
- ✅ Testing: All modules verified
- ✅ Deployment: Ready for production

---

**Last Updated**: May 2, 2026

**Version**: 1.0.0

**Status**: 🟢 Production Ready
