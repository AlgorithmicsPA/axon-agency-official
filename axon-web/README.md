# Axon Core - Frontend Web App

Professional web application for controlling Axon 88 infrastructure. Built with Next.js 15, TypeScript, Tailwind CSS, and shadcn/ui.

## Features

- **Dashboard**: Real-time system metrics (CPU, RAM, Disk, GPU, Uptime)
- **Services**: Manage systemd and Docker services
- **Commands**: Execute whitelisted commands with live streaming logs
- **Files**: Browse and download files securely
- **Flows**: Trigger n8n workflows
- **LLM**: Multi-provider LLM playground (OpenAI, Gemini, DeepSeek, Ollama)
- **Chat & Voice**: Interactive chat with microphone support and TTS
- **Settings**: Configure backend URL and JWT authentication

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui (Radix)
- **Icons**: lucide-react
- **State**: Zustand
- **Data Fetching**: TanStack Query + Axios
- **WebSocket**: Socket.IO Client
- **Validation**: Zod
- **Charts**: Recharts

## Quick Start on Replit

### 1. Install Dependencies

```bash
cd axon-web
npm install
```

### 2. Configure Backend

Create `.env.local` file:

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_BACKEND_URL=https://your-backend.repl.co
```

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5000`

### 4. Configure JWT Token

1. Open the app in your browser
2. Navigate to **Settings** page
3. Paste your backend URL
4. Get a JWT token from your backend's `/api/token/dev` endpoint
5. Paste the token in the JWT Token field
6. Click **Save Settings**
7. Click **Test Connection** to verify

## Scripts

- `npm run dev` - Start development server on port 5000
- `npm run build` - Build for production
- `npm run start` - Start production server on port 5000
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run type-check` - Run TypeScript type checking

## Project Structure

```
axon-web/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Dashboard
│   ├── services/          # Services management
│   ├── commands/          # Command execution
│   ├── files/             # File browser
│   ├── flows/             # n8n workflows
│   ├── llm/               # LLM playground
│   ├── chat/              # Chat & Voice
│   └── settings/          # Settings
├── components/
│   ├── ui/                # shadcn/ui components
│   ├── layout/            # Sidebar, Topbar
│   ├── chat/              # Chat components
│   └── common/            # StatusPill, Copyable
├── lib/
│   ├── api.ts             # Axios client
│   ├── ws.ts              # WebSocket client
│   ├── store.ts           # Zustand store
│   ├── types.ts           # TypeScript types
│   └── schemas.ts         # Zod schemas
└── hooks/                 # Custom React hooks
```

## Chat & Voice Features

### Text Chat
- Real-time bidirectional communication via WebSocket
- Message history with timestamps
- Auto-scroll to latest messages

### Voice Input
- Uses Web Speech API for speech-to-text
- Visual feedback while listening
- Supports Spanish (es-ES) by default

### Text-to-Speech
- Automatic playback of assistant responses (toggle on/off)
- Supports backend-provided audio or browser SpeechSynthesis API
- Spanish language support

## API Integration

The frontend connects to Axon Core backend endpoints:

- `GET /api/health` - Health check
- `GET /api/catalog` - Available services/tools
- `GET /api/metrics` - System metrics
- `POST /api/services/list` - List services
- `POST /api/services/control` - Control services
- `POST /api/commands/run` - Execute commands
- `POST /api/files/list` - List files
- `POST /api/files/download` - Download files
- `POST /api/flows/trigger` - Trigger workflows
- `POST /api/llm/infer` - LLM inference
- WebSocket: `ws://<backend>/ws?token=<jwt>` - Real-time events

## Building for Production

```bash
npm run build
npm run start
```

## Development Notes

- The app uses dark theme by default with cyan/magenta neon accents
- WebSocket connection is established automatically on app load
- Settings are persisted in localStorage
- All API calls include JWT token from settings

## Browser Compatibility

- Modern browsers with ES2020+ support
- Web Speech API requires Chrome/Edge for best results
- WebSocket support required

## Troubleshooting

### Connection Issues
1. Check backend URL in Settings
2. Verify JWT token is valid
3. Check CORS settings on backend
4. Ensure WebSocket port is accessible

### Voice Not Working
- Enable microphone permissions
- Use Chrome/Edge browser
- Check Web Speech API availability

### TTS Not Playing
- Enable speaker/audio output
- Check browser audio permissions
- Toggle "Hablar respuesta" switch

## License

Proprietary - Axon 88
