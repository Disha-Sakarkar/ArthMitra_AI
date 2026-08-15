# ArthMitra AI

> Your AI financial voice assistant for Bharat.

ArthMitra AI is a voice-first financial education assistant built for the **Murf AI – 10 Days of Voice Agents: VoiceForBharat Edition**, under the **Financial Services** track.

It is designed to make financial information easier to understand through natural voice conversations, especially for users who may face language, digital-literacy, or financial-complexity barriers.

ArthMitra can explain government schemes, banking services, digital payments, financial concepts, exchange rates, and fraud awareness while maintaining strict safety and privacy boundaries.

---

## What ArthMitra Does

ArthMitra combines voice AI, financial tools, consent-based memory, human escalation, outbound calling, analytics, and specialist handoffs into one conversational financial assistant.

### Core capabilities

- Voice-based financial conversations
- English, Hindi, and Hindi-English code-mixed conversations
- Government scheme information and document guidance
- Live exchange-rate lookup
- Banking and digital-payment literacy
- Financial fraud awareness
- Consent-based caller memory
- Outbound scheme-deadline reminder calls
- Human escalation for sensitive or account-specific situations
- Privacy-safe call analytics
- Specialist handoff for government-scheme questions
- Graceful handling of API, transcription, audio, and data-source failures

---

## Voice Conversation

The core interaction follows a simple voice pipeline:

```text
User speaks
     ↓
Deepgram Speech-to-Text
     ↓
Conversation Manager
     ↓
Gemini
     ↓
Murf AI Text-to-Speech
     ↓
User hears response
```
The browser communicates with the FastAPI backend through WebSockets so the conversation can remain interactive.

ArthMitra also maintains the current conversation context so follow-up questions feel like part of the same conversation rather than isolated requests.

### Multilingual Conversations

ArthMitra is designed for Bharat's multilingual environment.

It can handle:

- English
- Hindi
- Hindi-English code mixing

The assistant is instructed to mirror the user's language and communication style instead of forcing every conversation into English.

For example:
```
User:
"PMJJBY ke liye documents kya chahiye?"


ArthMitra:
"PMJJBY ke liye aapko..."
```
This is particularly important for a financial assistant because complicated financial terminology can become a barrier when users are more comfortable communicating in their local language.

### Financial Safety Guardrails

ArthMitra is an educational financial assistant, not a bank or financial institution.

It cannot:

- Access bank accounts
- Perform transactions
- Approve loans or schemes
- Verify account ownership
- Make investment decisions
- Provide account-specific approvals

It also never asks users for sensitive credentials such as:

- OTP
- PIN
- Password
- CVV
- Account numbers
- Card numbers
- Aadhaar
- PAN
- IFSC-related sensitive information

For account-specific situations, the assistant directs users toward official bank customer care or their nearest branch.

### Consent-Based Caller Memory

ArthMitra can remember useful, non-sensitive information across browser voice sessions, but memory is **opt-in**.

Each browser receives a persistent anonymous caller ID through localStorage. When a new WebSocket session starts, that identifier allows the backend to identify a returning caller without exposing their identity.

```
Browser
   ↓
Anonymous caller ID
   ↓
WebSocket session
   ↓
Gemini memory tool
   ↓
SQLite
   ↓
Approved caller context
```

###  What can be remembered

Memory is intentionally limited to useful conversational context such as:

Name
Language preference
Scheme interests
Scheme/eligibility answers
Follow-up topic

ArthMitra must explain what it wants to remember and receive explicit permission before saving it.

The backend also rejects memory operations that contain sensitive information or restricted keys.

This allows returning users to receive a more personalised experience without turning the system into a repository of financial credentials.

### Government Scheme Intelligence

ArthMitra includes a controlled government-scheme lookup tool.

The local dataset currently contains information for:

- PMJDY
- PMSBY
- PMJJBY
- APY
- PMMY

The dataset is clearly treated as **local, not live data**, and includes an as-of date and official portal references for final verification.

The lookup can provide information such as:

- Eligibility
- Benefits
- Required documents
- Enrolment
- Ministry
- Official portal

If a scheme is not present in the local dataset, ArthMitra does not invent the information.

For example, if a user asks about a scheme that has not been included in the dataset, the assistant can explain that it currently does not have verified information rather than hallucinating an answer.

### Live Exchange Rates

For questions requiring current financial data, ArthMitra uses a Gemini function tool:
```
get_live_exchange_rate
```
For example:
```
"What is today's USD to INR exchange rate?"
```
The backend retrieves the current reference rate from the public ExchangeRate-API feed instead of relying on the model's training data.

Each successful result includes the provider's last-updated timestamp.

The assistant also explains that the returned value is a reference market rate and that banks or authorised money changers may provide different customer rates.

###Failure handling

The exchange-rate lookup has a five-second timeout.

If the external source is unavailable, ArthMitra does not guess a number. It returns a clear response explaining that the live rate is temporarily unavailable.

###Outbound Calling

ArthMitra can initiate outbound calls for controlled financial-service use cases such as government-scheme deadline reminders.

The outbound call clearly communicates:

Who is calling
Why the user is being contacted
How the user can opt out

Example:
```
Hello, this is ArthMitra, a financial guidance assistant
calling because [scheme] has an approaching application deadline.

To stop future reminder calls, say stop or press 9.
```
Twilio handles the outbound telephony connection.

Opt-out phrases such as:
```
stop
opt out
unsubscribe
do not call
```
and pressing ```9``` create a durable do-not-call record.

Future outbound attempts to that number are rejected.

For testing, outbound calls should only be made to numbers controlled by the developer or explicitly authorised recipients.

### Human Escalation

ArthMitra does not attempt to solve every financial problem itself.

It can create a human-help request when:

- A caller reports possible financial fraud
- A caller needs an account-specific decision or approval that ArthMitra cannot provide

Before creating an escalation, the assistant explains what information will be shared and asks for explicit permission.

Only a short summary is sent, containing useful context such as:

- Caller name, if known
- What happened
- Checks already completed
- Urgency
- Language
- Preferred follow-up method

Sensitive information is rejected by the backend.

Approved requests are stored in SQLite and receive a reference ID such as:
```
ESC-...
```
The caller receives the reference ID and an honest explanation that a human will review the request.

No immediate response is promised unless one is actually available.

Escalation dashboard

Local escalation requests can be viewed at:
```
http://127.0.0.1:8000/escalations
```
The queue is also available through:
```
/api/escalations
```

### Privacy-Safe Call Analytics

ArthMitra records the outcome of completed browser voice calls without exposing caller information.

A call is considered **successful** when the caller receives:

- A government-scheme document list, or
- A scheme eligibility answer

Calls that end without reaching one of these outcomes are recorded as failed.

The analytics record contains only information such as:

- Channel
- Timestamp
- Outcome
- Completion category

It does ```not``` store:

- Caller IDs
- Full transcripts
- Passwords
- OTPs
- PINs
- Account details
- Sensitive financial information

### Analytics dashboard

Open:
```
http://127.0.0.1:8000/analytics
```
The dashboard provides:
```
Total Calls
Successful Calls
Failed Calls
```
Aggregate analytics are also available through:
```
/api/call-analytics
```

### Specialist Agent Handoff

ArthMitra uses a specialist-agent architecture instead of forcing one agent to handle every type of financial question.

There are two distinct conversational roles:

###Main ArthMitra Agent

Handles:

- Financial literacy
- Banking questions
- Digital payments
- Exchange rates
- Fraud awareness
- General financial guidance

### Government Scheme Specialist

Handles only:
- Named government scheme eligibility
- Benefits
- Required documents
- Enrolment
- Ministry information
- Official portals

The main agent has a controlled handoff tool:
```
transfer_to_government_scheme_specialist
```
When a user asks a question that requires the specialist, ArthMitra clearly announces the handoff:
```
I will connect you to our government schemes specialist.
```
The specialist then continues with the existing conversation context.

The user does not need to repeat their original question.

For example:
```
User:
"What documents do I need for PMSBY?"


Main Agent:
"I will connect you to our government schemes specialist."


Specialist:
"Government Schemes Specialist here..."
```
Normal financial questions remain with the main agent.

### Failure Handling

Voice systems depend on multiple external services, so failures are treated as part of the design rather than unexpected exceptions.

ArthMitra handles failures from:

- Speech-to-text
- Gemini
- Exchange-rate API
- Government-scheme data
- Murf audio generation
- Backend services
- WebSocket communication

The goal is to keep the conversation alive whenever possible.

For example, if Murf audio generation fails, the assistant can still return the response as text instead of losing the entire conversation.

If an external data source is unavailable, ArthMitra explains that the information cannot currently be fetched instead of inventing an answer.

### Architecture
```
                         ┌─────────────────────┐
                         │     React Frontend  │
                         │                     │
                         │  Microphone / UI    │
                         │  Caller ID          │
                         └──────────┬──────────┘
                                    │
                                WebSocket
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │                     │
                         │ Conversation Layer  │
                         │ Tool Orchestration  │
                         │ Session Management  │
                         └───────┬─────┬───────┘
                                 │     │
              ┌──────────────────┘     └──────────────────┐
              ▼                                           ▼
       ┌──────────────┐                            ┌──────────────┐
       │   Deepgram   │                            │    Gemini    │
       │     STT      │                            │  Reasoning   │
       └──────────────┘                            └──────┬───────┘
                                                         │
                          ┌──────────────────────────────┼────────────────────┐
                          │                              │                    │
                          ▼                              ▼                    ▼
                  ┌──────────────┐              ┌──────────────┐     ┌──────────────┐
                  │ Memory Tools │              │ Financial    │     │ Specialist   │
                  │              │              │ Tools        │     │ Handoff      │
                  └──────┬───────┘              └──────────────┘     └──────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │    SQLite    │
                  │ Memory /     │
                  │ Escalations  │
                  │ Analytics    │
                  └──────────────┘
                                 Gemini Response
                                       │
                                       ▼
                               ┌────────────────┐
                               │    Murf AI     │
                               │     TTS        │
                               └───────┬────────┘
                                       │
                                       ▼
                                 Voice Response
 ```
### Technology Stack
| Layer |	Technology| 
| --- | --- |  
| Frontend | React, Vite, Tailwind CSS | 
| Real-time communication | WebSocket | 
| Backend | Python, FastAPI | 
| Database | SQLite | 
| LLM | Google Gemini | 
| Speech-to-Text | Deepgram | 
| Text-to-Speech | Murf AI | 
| Telephony | Twilio | 
| Live financial data | ExchangeRate-API | 
| Browser memory |	localStorage | 

###Project Structure
```
ArthMitra-AI/
│
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   └── config.py
│   │   │
│   │   ├── data/
│   │   │   └── government_schemes.json
│   │   │
│   │   ├── prompts/
│   │   │   ├── greeting.py
│   │   │   └── system_prompt.py
│   │   │
│   │   ├── services/
│   │   │   ├── conversation_manager.py
│   │   │   ├── deepgram_service.py
│   │   │   ├── exchange_rate_service.py
│   │   │   ├── gemini_service.py
│   │   │   └── murf_service.py
│   │   │
│   │   └── memory.py
│   │
│   ├── main.py
│   ├── test_memory.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── services/
│       │   └── websocket.js
│       └── App.jsx
│
└── README.md
```
### Running Locally
1. Clone the repository
```
git clone <your-repository-url>
cd ArthMitra-AI
```
2. Configure environment variables

Create:
```
backend/.env
```
Add the required API credentials:
```
GEMINI_API_KEY=your_key
DEEPGRAM_API_KEY=your_key
MURF_API_KEY=your_key
```
For outbound calling, configure the Twilio credentials and public backend URL as required:
```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number
PUBLIC_BASE_URL=https://your-public-https-url
OUTBOUND_API_KEY=your_secret
```
Never commit .env files or API keys to the repository.

3. Start the backend
```
cd backend
uvicorn main:app --reload
```
4. Start the frontend

Open another terminal:
```
cd frontend
npm install
npm run dev
```
Open the local frontend URL shown by Vite and allow microphone access.

### Testing Caller Memory

From the backend directory:
```
python -m unittest test_memory.py
```
The memory tests cover:
- Permitted memory storage
- Missing consent
- Sensitive-data rejection

### Testing the Voice Agen
After starting the frontend and backend:
- Allow microphone access.
- Start a voice session.
- Ask a general financial question.
- Ask a named government-scheme question.
- Test a live exchange-rate question.
- Test the consent flow for caller memory.
- Test the human-escalation flow.
- Check the analytics dashboard after ending the call.

Example questions:
```
"What is the difference between a debit card and a credit card?"

"What documents do I need for PMSBY?"

"What is today's USD to INR exchange rate?"

"I saw an unfamiliar transaction."

"Can you remember my name?"
```
### Important Environment Variables
| Variable | Purpose | 
| --- | --- |   
| GEMINI_API_KEY | Gemini model access | 
| DEEPGRAM_API_KEY | Speech-to-text | 
| MURF_API_KEY | Text-to-speech | 
| TWILIO_ACCOUNT_SID | Twilio authentication | 
| TWILIO_AUTH_TOKEN | Twilio authentication | 
| TWILIO_PHONE_NUMBER | Outbound caller number | 
| PUBLIC_BASE_URL | Public HTTPS backend URL for Twilio | 
| OUTBOUND_API_KEY | Protects outbound-call API | 
| EXCHANGE_RATE_URL | Optional exchange-rate source override | 

Keep all credentials private.

### Privacy and Security

Privacy is a core design principle of ArthMitra.

### Caller memory

Memory is saved only after explicit user consent.

### Sensitive information

The system is designed to reject sensitive information such as:
```
OTP
PIN
Password
CVV
Account Number
Card Number
Aadhaar
PAN
IFSC
```
### Analytics

Analytics are aggregate and privacy-safe. Caller identifiers and conversation transcripts are not displayed on the analytics dashboard.

### Human escalation

Escalation summaries are intentionally limited to the information required for a human to understand and follow up on the issue.

### Outbound calls

Outbound calling includes an explicit opt-out mechanism and a durable do-not-call record.

### Design Principles
**1. Voice first**

Financial information should be accessible through conversation, not only through complex interfaces.

**2. Explain, don't transact**

ArthMitra helps users understand financial services but never pretends to be a bank or perform financial transactions.

**3. Consent before memory**

Personalisation should not come at the cost of user control.

**4. Fail safely**

When a tool or API fails, ArthMitra should communicate the limitation rather than hallucinate an answer.

**5. Specialist over generalisation**

Complex domains are handled through focused specialist agents instead of making one agent responsible for everything.

**6. Human help when necessary**

An AI assistant should know when it has reached the boundary of what it can safely handle.

### Current Limitations
- Voice recording currently uses a fixed audio window rather than continuous streaming.
- Gemini and Murf responses are generated before playback rather than being fully streamed.
- End-to-end response latency can be around 10–12 seconds after the user stops speaking.
- Caller memory currently uses a local SQLite database.
- There is no dedicated user-facing memory-management or deletion interface yet.
- The local government-scheme dataset is not a live government database.
- Scheme information should be verified against official government sources when current policy or eligibility details are important.
- Multilingual speech recognition and voice quality can still vary depending on pronunciation, audio quality, and language mixing.

### Future Improvements

Potential next steps include:
- Continuous streaming speech recognition
- Streaming TTS for lower perceived latency
- Improved Indian-language voice quality
- More official and source-backed government scheme information
- User-facing memory management and deletion
- More specialist financial agents
- Better analytics and latency monitoring
- Production-grade deployment
- Broader telephony support
- Stronger automated safety and privacy testing

### Vision

ArthMitra AI is built around a simple idea:

**Financial information should be understandable before it becomes actionable.**

The goal is not to replace banks, financial institutions, or human advisors.

The goal is to provide an accessible conversational layer that helps people understand financial services, discover relevant government schemes, recognise potential fraud, and know when to seek human assistance.

Built for **Murf AI – 10 Days of Voice Agents: VoiceForBharat Edition.**

**Track: Financial Services
**TTS:** Murf AI
**STT:** Deepgram
**LLM:** Google Gemini
**Backend:** FastAPI
**Frontend:** React + Vite
