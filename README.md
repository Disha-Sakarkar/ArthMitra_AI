# 💰 ArthMitra AI

> **Your AI Financial Voice Assistant for Bharat 🇮🇳**

An AI-powered multilingual voice agent built for the **Murf AI – 10 Days of Voice Agents (VoiceForBharat Edition)** challenge.

**Track:** Financial Services

ArthMitra AI helps users understand government schemes, improve banking literacy, and stay safe from financial fraud using natural voice conversations.

---

# 🚀 Challenge Progress

## ✅ Day 1 – Voice Agent Foundation

Completed:

- React + FastAPI project setup
- WebSocket communication
- Speech-to-Text using Deepgram
- AI responses using Gemini 2.5 Flash
- Murf AI Text-to-Speech integration
- Modern financial assistant UI
- Voice conversation pipeline

Pipeline:

```

User Speech
↓
Deepgram STT
↓
Gemini
↓
Murf AI
↓
Voice Response

```

---

## ✅ Day 2 – Personality, Job & Guardrails

Implemented:

### 🧑 Identity

ArthMitra AI is a trustworthy Financial Voice Assistant built for Bharat.

It helps users understand:

- Government schemes
- Banking services
- Digital payments
- Financial literacy
- Fraud awareness

---

### 🎯 Objectives

A successful conversation should:

- Explain financial concepts in simple language.
- Help users understand government welfare schemes.
- Educate users about safe digital banking.
- Protect users against financial fraud and scams.

---

### 💬 Conversation Memory

Implemented session-based conversation history.

The assistant now:

- remembers previous turns
- answers follow-up questions
- maintains conversation context
- preserves the system persona throughout the session

---

### 👋 Automatic Greeting

When a user connects, ArthMitra AI automatically:

- introduces itself
- explains what it can help with
- greets the user using Murf AI voice

---

### 🌏 Multilingual Support

Supports:

- English
- Hindi
- Code-mixed Hindi + English

The assistant mirrors the user's language naturally.

Example:

User:

> Mujhe PM Jan Dhan account open karna hai.

Assistant:

> Agar aap PM Jan Dhan account open karna chahte hain to Aadhaar ya kisi valid KYC document ki zarurat hogi.

---

### 🛡 Guardrails

The assistant will NEVER:

- Ask for OTP
- Ask for PIN
- Ask for Password
- Ask for CVV
- Ask for Debit/Credit Card number

The assistant will NEVER claim:

- Scheme approval
- Loan approval
- Account access
- Bank employee identity

---

### 📞 Escalation

Whenever an account-specific request is received:

> "I'm sorry, but I can't access your account or perform banking operations. Please contact your bank's official customer care or visit your nearest branch. Never share your OTP, PIN, or password with anyone."

---

# 🛠 Tech Stack

### Frontend

- React
- Tailwind CSS
- WebSockets

### Backend

- FastAPI
- Python

### AI

- Google Gemini 2.5 Flash

### Speech

- Deepgram STT
- Murf AI TTS

---

# 🏗 Current Architecture

```

Browser

↓

React

↓

WebSocket

↓

FastAPI

↓

Deepgram STT

↓

Conversation Manager

↓

Gemini

↓

Murf AI

↓

Browser Audio

```

---

# 🧠 Voice Choice

An Indian English voice was selected because financial guidance should sound calm, trustworthy, and easy to understand for users across Bharat.

---

# ⏱ Baseline Latency

Current latency (end of user speech → first audio response)

≈ 10–12 seconds

---

# ⚠ Current Limitations

- Fixed-length recording instead of streaming.
- Higher end-to-end latency.
- STT accuracy can be improved for noisy environments.
- TTS currently generates complete audio before playback.
- Conversation memory is limited to the current session.

---

# 📅 Upcoming Improvements

- Streaming Speech-to-Text
- Streaming Murf Falcon Text-to-Speech
- Real-time voice conversations
- Lower latency
- Voice interruption support
- Dynamic tool calling
- Government scheme knowledge base
- Fraud detection workflows
- Phone call support

---

# 📂 Project Structure

```

backend/
│
├── app/
│ ├── prompts/
│ │ ├── greeting.py
│ │ └── system_prompt.py
│ │
│ ├── services/
│ │ ├── conversation_manager.py
│ │ ├── deepgram_service.py
│ │ ├── gemini_service.py
│ │ └── murf_service.py
│ │
│ └── main.py

frontend/
│
├── components/
├── services/
└── App.jsx

```

---

# 📌 Challenge

Built as part of:

**Murf AI – 10 Days of Voice Agents**
**VoiceForBharat Edition**

---

# ❤️ Vision

Millions of Indians still struggle to access reliable financial guidance due to language barriers and digital complexity.

ArthMitra AI aims to bridge this gap through natural voice conversations, making banking services, government schemes, and fraud awareness accessible to everyone.