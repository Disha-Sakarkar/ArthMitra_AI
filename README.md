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

### Day 5 - Live financial-data tool

ArthMitra now has a Gemini function tool, `get_live_exchange_rate`, for questions that need current financial data, such as “What is today’s USD to INR rate?” The model is instructed to call it for live/current exchange-rate or conversion requests, rather than guessing from its training data.

- **Data is live:** the backend fetches the public ExchangeRate-API open-access feed at request time; it is not a hand-built local dataset.
- Every successful tool result includes the provider’s **last-updated timestamp**, which ArthMitra must speak naturally along with the reference rate.
- Rates are reference market rates only; a bank or authorised money changer may quote a different customer rate.
- The lookup uses a five-second timeout. If the source is unavailable, the tool returns an explicit unavailable result and the assistant says it cannot fetch the live rate right now—it does not invent one.

Try it after connecting to the agent: **“What is today’s USD to INR exchange rate?”** The agent should call the tool without being explicitly told to do so. To exercise the failure path, disconnect the backend from the internet or temporarily set `EXCHANGE_RATE_URL` in `backend/app/services/exchange_rate_service.py` to an invalid address; the spoken reply should say the live rate is temporarily unavailable.

### Local central-government scheme lookup

ArthMitra also has a `lookup_government_scheme` function tool for named Indian central-government schemes. It uses the hand-built local dataset at `backend/app/data/government_schemes.json`; it is **not live data**. The dataset covers PMJDY, PMSBY, PMJJBY, APY, and PMMY, is labelled with an as-of date, and links each result to an official portal for final verification.

The function description tells Gemini to call it only for questions about a named scheme’s eligibility, benefits, documents, enrolment, ministry, or official portal. It must not guess a scheme’s details when the lookup does not find it.

Failure handling is visible in the conversation: transcription failures, Gemini/backend failures, and Murf audio failures all preserve the WebSocket session and send a readable fallback reply to the frontend. If audio generation fails, the response remains visible as text; if the assistant service is unavailable, the UI also shows a status message above the conversation.

Try: **“What are the eligibility rules for PMSBY?”** To test the local-data failure path, temporarily rename `backend/app/data/government_schemes.json`; the assistant should say that the local scheme information is unavailable rather than inventing an answer.

### Day 6 – Outbound scheme-deadline reminder

ArthMitra can now make an outbound reminder call to someone who was already found eligible for a government scheme. The call opens with who is calling, why, and an immediate opt-out: **“Hello, this is ArthMitra, a financial guidance assistant calling because [scheme] has an approaching application deadline of [date]. To stop future reminder calls, say stop or press 9.”**

Twilio dials the phone number and posts call events to FastAPI. The call uses speech/DTMF gathering, Gemini for the short follow-up, and Murf audio where available (with Twilio TTS as a fallback). Saying **stop**, **opt out**, **unsubscribe**, **do not call**, or pressing **9** writes a durable do-not-call record; later call attempts to that number are rejected.

Configure `backend/.env` from `backend/.env.example`:

```env
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
PUBLIC_BASE_URL=https://your-public-https-url
OUTBOUND_API_KEY=choose-a-long-secret
```

`PUBLIC_BASE_URL` must be public HTTPS URL Twilio can reach (a deployed backend or temporary HTTPS tunnel). Start the API, then place one controlled test call:

```bash
curl -X POST http://127.0.0.1:8000/outbound/call \
  -H "Content-Type: application/json" \
  -H "X-Outbound-Api-Key: your-secret" \
  -d '{"to_number":"+919876543210","scheme_name":"Pradhan Mantri Suraksha Bima Yojana","deadline":"31 August 2026"}'
```

Use only a number you control while recording the demonstration. The response contains the Twilio Call SID, which you can track in the Twilio Console.

### Day 7 – Human help with privacy and consent

ArthMitra now escalates only two kinds of browser-agent conversations: a caller reporting possible fraud, and a caller who needs an approval or account-specific decision ArthMitra cannot make. Normal scheme, literacy, and exchange-rate questions stay with the agent.

Before it creates a request, ArthMitra explains that it will share only a short summary (caller name if known, what happened, checks already completed, urgency, language, and preferred follow-up method) and asks for explicit permission. A refusal never creates a request. The backend rejects summaries containing credentials or sensitive identifiers, including OTPs, PINs, passwords, account/card numbers, Aadhaar, PAN, CVV, and IFSC.

Approved requests are stored in the local SQLite help queue with a generated `ESC-...` reference ID. The agent gives this ID to the caller and honestly says that a human will review the request and use the requested follow-up method, without promising an immediate response. View the real local dashboard at [http://127.0.0.1:8000/escalations](http://127.0.0.1:8000/escalations), or consume the queue as JSON at `/api/escalations`.

Test paths:

- Escalation: say that you saw an unfamiliar transaction or need a decision the agent cannot make; approve the requested summary sharing; confirm a reference ID is returned and appears in the dashboard.
- Normal: ask about PMSBY eligibility or financial literacy; confirm that no request is created.

### Day 8 – Call analytics dashboard

ArthMitra records a privacy-safe outcome for every completed browser voice call. A call is **successful** when the caller receives a scheme document list or an eligibility answer; an ended call that did not reach either outcome is **failed**. The record contains only the channel, timestamps, outcome, and completion category—never a caller ID, transcript, credentials, or account details.

Open [http://127.0.0.1:8000/analytics](http://127.0.0.1:8000/analytics) to see real aggregate **Total calls**, **Successful calls**, and **Failed calls**. The same aggregate data is available at `/api/call-analytics`.

To exercise the success path, start a browser voice call and ask a named-scheme document question, for example: **“What documents do I need for PMSBY?”** End the call after ArthMitra answers; total and successful calls will each increase by one.

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

## Vision

ArthMitra AI aims to make financial information easier to understand for people who face language, digital-literacy, or complexity barriers. It is an accessible conversational layer—not a replacement for banks or financial institutions.

Built for **Murf AI – 10 Days of Voice Agents, VoiceForBharat Edition**.
Track: **Financial Services**
