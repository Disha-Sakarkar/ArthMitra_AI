# 💰 ArthMitra AI

> **Your AI Financial Voice Assistant for Bharat 🇮🇳**

ArthMitra AI is an AI-powered voice agent built for the **Murf AI – 10 Days of Voice Agents: VoiceForBharat Edition** challenge.

**Track:** Financial Services

ArthMitra AI is designed to make financial information easier to access through voice, helping users understand government schemes, banking concepts, digital payments, and financial fraud awareness.

---

# 🚀 Challenge Progress

## ✅ Day 1 – Voice Agent Foundation

Built the initial voice conversation pipeline.

### Completed

- React frontend
- FastAPI backend
- WebSocket communication
- Speech-to-Text using Deepgram
- AI responses using Gemini 2.5 Flash
- Text-to-Speech using Murf AI
- Indian English voice
- Initial voice conversation interface

### Initial Pipeline

```text
User Speech
     ↓
Deepgram STT
     ↓
Gemini
     ↓
Murf AI TTS
     ↓
Voice Response
```

### Voice Choice

An Indian English voice was selected because financial guidance should sound calm, trustworthy, and easy to understand for users across Bharat.

### Day 1 Baseline Latency

**End of user speech → first audio response: approximately 10–12 seconds.**

This latency is being treated as the baseline for future optimization.

---

# ✅ Day 2 – Personality, Job & Guardrails

ArthMitra AI was given a defined role, objectives, conversation memory, language behavior, and safety boundaries.

## 🧑 Identity

ArthMitra AI is a trustworthy Financial Voice Assistant built for Bharat.

It helps users understand:

- Government schemes
- Banking services
- Digital payments
- Financial literacy
- Fraud awareness

---

## 🎯 Call Objectives

A successful conversation should help the user:

1. Understand government schemes in simple language.
2. Improve their understanding of banking and digital payments.
3. Recognize and avoid common financial frauds.

---

## 🧠 Conversation History

Implemented session-based conversation history.

ArthMitra AI can now:

- Remember previous turns within a session.
- Handle follow-up questions.
- Maintain context across multiple turns.
- Preserve its persona throughout the conversation.

The conversation history is managed separately for each WebSocket session.

---

## 👋 Automatic Greeting

When a client connects, ArthMitra AI automatically introduces itself.

The greeting:

- Appears in the frontend.
- Is converted to speech using Murf AI.
- Is played automatically to the user.

Example:

> Hello! I'm ArthMitra AI, your Financial Voice Assistant for Bharat. I can help you understand government schemes, banking services, digital payments, and financial fraud awareness. How may I help you today?

---

## 🌏 Language & Code-Mixed Support

ArthMitra AI is designed to mirror the user's language.

It can handle:

- English
- Hindi
- Hindi + English code-mixed conversations

Example:

```text
User:
Mujhe PM Jan Dhan account open karna hai.
```

The assistant responds in a similar conversational register.

---

## 🛡 Financial Safety Guardrails

ArthMitra AI must never ask users for:

- OTP
- PIN
- Password
- CVV
- Debit/Credit Card number

It must never claim that it can:

- Access a bank account
- Perform a banking transaction
- Approve a government scheme
- Approve a loan
- Verify Aadhaar
- Recover money
- Act as a bank employee

### Escalation

For account-specific or banking-operation requests, the assistant directs users to their bank's official customer care or nearest branch.

It also reminds users:

> Never share your OTP, PIN, or password with anyone.

---

# ✅ Day 3 – Personalised Frontend

Day 3 focused on creating a frontend specifically designed for the **Financial Services** track.

The interface was redesigned around ArthMitra AI rather than using a generic voice-agent layout.

---

## 🎨 Financial Services UI

The frontend now uses a financial-services visual identity with:

- Deep indigo and blue tones
- Professional financial styling
- Financial-themed background imagery
- High-contrast chat interface
- Dedicated capability panel
- Voice-focused interaction controls

The layout is divided into two primary areas:

```text
┌──────────────────────┬─────────────────────────────────────┐
│                      │                                     │
│    ArthMitra AI      │       Voice / Conversation          │
│                      │                                     │
│  What I can help     │       Chat History                  │
│  you with            │                                     │
│                      │                                     │
│  🏛 Government       │                                     │
│     Schemes          │                                     │
│                      │                                     │
│  🏦 Banking          │                                     │
│     Literacy         │                                     │
│                      │                                     │
│  🛡 Fraud Awareness  │       🎙 Voice Controls              │
│                      │                                     │
└──────────────────────┴─────────────────────────────────────┘

        30%                         70%
```

The left section explains the agent's purpose and capabilities, while the right section provides the complete conversation experience.

---

# 🎛 Agent States

The frontend now clearly communicates the current state of the voice agent.

### 🟢 Ready

The agent has not started yet.

The user sees a clear:

> 🎙️ Start Voice Call

button.

---

### 🟡 Connecting

After starting the call:

> 🔄 Connecting...

The interface tells the user to wait while the WebSocket connection is established.

---

### 🔴 Listening

When the agent is ready to receive the user's voice:

> 🎙️ Listening to you

The interface provides a visual voice indicator so the user knows the microphone is active.

---

### 🟢 Speaking

When ArthMitra AI is responding:

> 🔊 ArthMitra is speaking

The interface changes its status while the Murf-generated response is playing.

---

### ⚪ Call Ended

When the conversation ends:

> ✅ Call ended

The user receives a clear option to:

> 🔄 Start Again

---

# 🎙 Speaker & Voice Feedback

The interface makes it clear who is currently speaking.

It uses:

- Listening status
- Speaking status
- Animated microphone indicator
- Voice waveform-style animation
- Different chat bubbles for the user and ArthMitra AI

This makes the voice interaction easier to understand without relying only on audio.

---

# 🎤 Microphone Permission Handling

The frontend now handles microphone permission failures.

If microphone access is denied, the user receives a clear message explaining that microphone access was blocked and is instructed to enable microphone permissions in the browser before trying again.

Other microphone failures, such as no microphone being detected, also produce an appropriate error message.

---

# 💬 Conversation Interface

The conversation area now occupies the full available right-side workspace instead of appearing as a small centered chat box.

The interface displays:

- User transcripts
- ArthMitra AI responses
- Conversation history
- Voice interaction controls

---

# 📱 Responsive Design

The frontend is designed to adapt to smaller screens.

On larger screens:

```text
30% Capability Panel | 70% Conversation
```

On smaller screens, the sections stack vertically to keep the important controls readable and accessible.

---

# 🏗 Current Architecture

```text
                        Browser
                           │
                           ▼
                    React Frontend
                           │
                     WebSocket
                           │
                           ▼
                    FastAPI Backend
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          Deepgram      Gemini        Murf AI
             STT          AI            TTS
              │            │            │
              └────────────┼────────────┘
                           ▼
                     Voice Response
```

---

# 🛠 Tech Stack

## Frontend

- React
- Tailwind CSS
- WebSocket

## Backend

- Python
- FastAPI
- WebSocket

## AI

- Google Gemini 2.5 Flash

## Speech

- Deepgram Speech-to-Text
- Murf AI Text-to-Speech
- Murf Falcon

---

# 📂 Project Structure

```text
ArthMitra-AI/
│
├── backend/
│   │
│   ├── app/
│   │   ├── prompts/
│   │   │   ├── greeting.py
│   │   │   └── system_prompt.py
│   │   │
│   │   └── services/
│   │       ├── conversation_manager.py
│   │       ├── deepgram_service.py
│   │       ├── gemini_service.py
│   │       └── murf_service.py
│   │
│   └── main.py
│
├── frontend/
│   │
│   └── src/
│       ├── assets/
│       ├── components/
│       │   ├── ChatBubble.jsx
│       │   ├── Header.jsx
│       │   ├── StatusBadge.jsx
│       │   └── VoiceButton.jsx
│       │
│       ├── services/
│       │   └── websocket.js
│       │
│       └── App.jsx
│
├── .gitignore
└── README.md
```

---

# ⏱ Current Latency Baseline

Current baseline:

**Approximately 10–12 seconds from end of user speech to first audio response.**

The current implementation waits for:

```text
Complete Recording
       ↓
Deepgram
       ↓
Complete Transcript
       ↓
Gemini Response
       ↓
Complete Murf Audio
       ↓
Playback
```

This is the primary performance limitation currently being tracked.

---

# ⚠️ Known Limitations

- Speech input currently uses a fixed recording window.
- STT is not yet continuously streamed.
- Gemini response generation is not yet streamed to the frontend.
- Murf audio is currently generated before playback rather than being streamed progressively.
- End-to-end latency is therefore higher than the target experience.
- Conversation history currently exists only for the active session.
- Financial information should be treated as educational guidance, not personalized financial advice.

---

# 📅 Development Roadmap

The project is being developed incrementally throughout the 10-day challenge.

Future improvements will focus on:

- Real-time streaming Speech-to-Text
- Streaming Murf Falcon TTS
- Lower perceived latency
- More natural voice conversations
- Improved multilingual support
- Financial scheme information
- Fraud-awareness workflows
- Real-world voice accessibility
- Deployment for users

---

# 🇮🇳 Vision

Many people in India face barriers when accessing financial information because of language, digital literacy, and the complexity of banking systems.

**ArthMitra AI** aims to make financial information easier to understand through a simple voice-first interface.

The goal is not to replace banks or financial institutions, but to provide an accessible conversational layer that helps users understand financial services and recognize potential fraud.

---

# 🏆 Challenge

Built as part of:

**Murf AI – 10 Days of Voice Agents**  
**VoiceForBharat Edition**

**Track:** Financial Services

#VoiceForBharat