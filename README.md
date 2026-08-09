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

### Day 4 – Consent-based caller memory

ArthMitra can now remember useful, non-sensitive context across voice calls—but only with the caller’s explicit permission.

- Each browser receives a persistent anonymous caller ID stored in `localStorage` and sends it when a WebSocket session begins.
- Caller memory is stored locally in SQLite and initialised when the FastAPI app starts.
- Gemini has controlled function tools to look up the active caller and save memory after consent.
- On a returning caller’s greeting, ArthMitra can welcome them back by name and continue an approved follow-up topic.
- The assistant must explain what it wants to remember and receive an explicit “yes” before saving anything.
- Memory is limited to a name, language preference, scheme interests, scheme/eligibility answers, and a follow-up topic.
- The backend rejects memory saves without consent and blocks sensitive keys or long number strings, including account, card, Aadhaar, PAN, OTP, PIN, password, CVV, and IFSC-related data.
- Unit tests cover permitted storage, missing consent, and sensitive-data rejection.

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

## Vision

ArthMitra AI aims to make financial information easier to understand for people who face language, digital-literacy, or complexity barriers. It is an accessible conversational layer—not a replacement for banks or financial institutions.

Built for **Murf AI – 10 Days of Voice Agents, VoiceForBharat Edition**.
Track: **Financial Services**
