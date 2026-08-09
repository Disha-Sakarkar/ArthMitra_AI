# ArthMitra AI

> Your AI financial voice assistant for Bharat.

ArthMitra AI is a voice-first financial education assistant built for the **Murf AI – 10 Days of Voice Agents: VoiceForBharat Edition** challenge, Financial Services track. It explains government schemes, banking, digital payments, financial literacy, and fraud awareness in clear, conversational language.

## Challenge progress

### Day 1 – Voice agent foundation

- React + Vite frontend and FastAPI backend
- WebSocket voice-conversation pipeline
- Deepgram speech-to-text
- Gemini-powered responses
- Murf AI text-to-speech with an Indian English voice

```text
User speech → Deepgram STT → Gemini → Murf TTS → voice response
```

### Day 2 – Personality, context, and guardrails

- Defined ArthMitra as a trustworthy financial assistant for Bharat.
- Added session-based conversation history for natural follow-up questions.
- Added an automatic spoken greeting when a voice call begins.
- Supports English, Hindi, and Hindi–English code-mixed conversations by mirroring the user’s language.
- Added financial-safety guardrails: ArthMitra never asks for an OTP, PIN, password, CVV, card number, or account number, and cannot access accounts or perform transactions.

### Day 3 – Personalised financial-services frontend

- Built a financial-services visual identity with a dedicated capability panel and conversation workspace.
- Added clear voice-agent states: Ready, Connecting, Listening, Speaking, and Call Ended.
- Added user and assistant chat bubbles, audio feedback, microphone permission errors, call controls, and restart flow.
- Made the experience responsive: the capability panel and conversation area stack on smaller screens.


```text
New / returning caller
        ↓
Browser caller ID (localStorage)
        ↓
WebSocket session_init
        ↓
Gemini lookup_caller tool
        ↓
SQLite consented memory
        ↓
Personalised, safety-bounded greeting or follow-up
```

## Current architecture

```text
Browser (React)
  ├─ microphone recording
  ├─ persistent anonymous caller ID
  └─ WebSocket
          ↓
FastAPI
  ├─ Deepgram: speech → transcript
  ├─ ConversationManager: current-call context
  ├─ Gemini: response + controlled memory tools
  ├─ SQLite: consented caller memory
  └─ Murf AI: response → audio URL
          ↓
Browser playback and chat history
```

## Tech stack

| Area | Technology |
| --- | --- |
| Frontend | React, Vite, Tailwind CSS, WebSocket |
| Backend | Python, FastAPI, SQLite |
| AI | Google Gemini |
| Speech | Deepgram STT, Murf AI TTS |

## Project structure

```text
ArthMitra-AI/
├── backend/
│   ├── app/
│   │   ├── core/config.py
│   │   ├── memory.py                 # Consent-gated SQLite caller memory
│   │   ├── prompts/
│   │   │   ├── greeting.py
│   │   │   └── system_prompt.py
│   │   └── services/
│   │       ├── conversation_manager.py
│   │       ├── deepgram_service.py
│   │       ├── gemini_service.py     # Gemini + memory function tools
│   │       └── murf_service.py
│   ├── main.py                       # FastAPI REST and WebSocket entry point
│   ├── test_memory.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/
│       ├── services/websocket.js
│       └── App.jsx
└── README.md
```

## Run locally

Create `backend/.env` with the required credentials:

```env
GEMINI_API_KEY=your_key
DEEPGRAM_API_KEY=your_key
MURF_API_KEY=your_key
```

Start the backend:

```bash
cd backend
uvicorn main:app --reload
```

Start the frontend in another terminal:

```bash
cd frontend
npm install
npm run dev
```

Run caller-memory tests:

```bash
cd backend
python -m unittest test_memory.py
```

## Safety and privacy

ArthMitra provides educational financial guidance, not personalised financial, legal, or investment advice. It never impersonates a bank and directs account-specific requests to official bank customer care or a branch. Never share OTPs, PINs, passwords, card details, or other credentials with anyone.

Persistent memory is opt-in. The implementation stores only a narrow, approved set of non-sensitive conversation details and rejects sensitive financial or identity information.

## Current limitations

- Recording uses a fixed audio window; speech is not yet continuously streamed.
- Gemini and Murf responses are generated before playback rather than streamed progressively.
- This produces an end-to-end baseline latency of roughly 10–12 seconds after the user stops speaking.
- Caller memory is local to the current backend’s SQLite database and is not yet accompanied by a user-facing memory-management or deletion screen.
- Scheme guidance should be verified against official sources when users need current eligibility or policy details.

## Next steps

- Stream speech-to-text and Murf Falcon audio to reduce perceived latency.
- Improve multilingual voice quality and language detection.
- Add official scheme-information workflows and source-backed responses.
- Add caller-facing controls to view, update, or delete saved memory.
- Deploy the voice experience for broader access.

## Vision

ArthMitra AI aims to make financial information easier to understand for people who face language, digital-literacy, or complexity barriers. It is an accessible conversational layer—not a replacement for banks or financial institutions.

Built for **Murf AI – 10 Days of Voice Agents, VoiceForBharat Edition**.  
Track: **Financial Services**
