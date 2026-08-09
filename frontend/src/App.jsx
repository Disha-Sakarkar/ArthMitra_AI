import { useState } from "react";

import Header from "./components/Header";
import StatusBadge from "./components/StatusBadge";
import ChatBubble from "./components/ChatBubble";
import VoiceButton from "./components/VoiceButton";

import {
    connectSocket,
    disconnectSocket
} from "./services/websocket";

import backgroundImage from "./assets/financial-bg.jpg";


function App() {

    const [messages, setMessages] = useState([]);

    const [status, setStatus] = useState("ready");

    const [errorMessage, setErrorMessage] = useState("");

    const [callActive, setCallActive] = useState(false);

    const callerId = (() => {
        const storedId = localStorage.getItem("arthmitra_caller_id");
        if (storedId) return storedId;

        const newId = crypto.randomUUID();
        localStorage.setItem("arthmitra_caller_id", newId);
        return newId;
    })();


    // --------------------------------------------------
    // Start Call
    // --------------------------------------------------

    const startCall = () => {

        setErrorMessage("");

        setStatus("connecting");

        setCallActive(true);


        connectSocket(

            // Message received
            (message) => {

                console.log("📩", message);

                setMessages(prev => [
                    ...prev,
                    message
                ]);

            },


            // WebSocket connected
            () => {

                console.log("🟢 Call connected");

            },


            // WebSocket closed
            () => {

                console.log("🔴 Call closed");

                setStatus("ended");

                setCallActive(false);

            },


            // WebSocket error
            () => {

                console.error("WebSocket connection error");

                setStatus("ended");

                setCallActive(false);

                setErrorMessage(
                    "We couldn't connect to ArthMitra. Please try again."
                );

            },


            // Audio started
            () => {

                setStatus("speaking");

            },


            // Audio finished
            () => {

                setStatus("listening");

            },

            callerId

        );

    };


    // --------------------------------------------------
    // End Call
    // --------------------------------------------------

    const endCall = () => {

        disconnectSocket();

        setCallActive(false);

        setStatus("ended");

    };


    // --------------------------------------------------
    // Restart
    // --------------------------------------------------

    const restartCall = () => {

        setMessages([]);

        setErrorMessage("");

        setStatus("ready");

        setCallActive(false);

    };


    // --------------------------------------------------
    // Microphone Error
    // --------------------------------------------------

    const handleMicrophoneError = (message) => {

        setErrorMessage(message);

        setStatus("error");

    };


    return (

        <div
            className="
                min-h-screen
                w-full
                relative
                bg-slate-950
                overflow-hidden
            "
            style={{
                backgroundImage: `url(${backgroundImage})`,
                backgroundSize: "cover",
                backgroundPosition: "center"
            }}
        >

            {/* Background overlay */}

            <div className="
                absolute
                inset-0
                bg-slate-950/75
                backdrop-blur-[2px]
            " />


            {/* Main application */}

            <div className="
                relative
                z-10
                min-h-screen
                w-full
                flex
                flex-col
                lg:flex-row
            ">


                {/* ==================================================
                    LEFT 30% — PRODUCT / CAPABILITIES
                ================================================== */}

                <aside className="
                    w-full
                    lg:w-[30%]
                    min-h-[360px]
                    lg:min-h-screen
                    px-7
                    py-8
                    lg:px-10
                    lg:py-12
                    flex
                    flex-col
                    justify-between
                    bg-gradient-to-b
                    from-indigo-950/90
                    via-blue-950/85
                    to-slate-950/90
                    border-r
                    border-white/10
                ">


                    {/* Branding */}

                    <div>

                        <div className="
                            flex
                            items-center
                            gap-3
                            mb-8
                        ">

                            <div className="
                                w-12
                                h-12
                                rounded-2xl
                                bg-gradient-to-br
                                from-indigo-400
                                to-blue-600
                                flex
                                items-center
                                justify-center
                                text-2xl
                                shadow-lg
                            ">
                                💰
                            </div>


                            <div>

                                <h1 className="
                                    text-white
                                    text-2xl
                                    font-bold
                                    tracking-tight
                                ">
                                    ArthMitra AI
                                </h1>

                                <p className="
                                    text-indigo-200
                                    text-xs
                                    mt-0.5
                                ">
                                    Financial Voice Assistant
                                </p>

                            </div>

                        </div>


                        {/* Main message */}

                        <div className="mb-8">

                            <p className="
                                text-indigo-200
                                text-sm
                                font-medium
                                mb-2
                            ">
                                VOICE FOR BHARAT
                            </p>


                            <h2 className="
                                text-white
                                text-3xl
                                lg:text-4xl
                                font-bold
                                leading-tight
                            ">
                                Financial guidance,
                                <span className="text-blue-300">
                                    {" "}made simple.
                                </span>
                            </h2>


                            <p className="
                                text-slate-300
                                mt-4
                                leading-relaxed
                                text-sm
                                lg:text-base
                            ">
                                Ask questions naturally and get
                                simple explanations about banking,
                                government schemes and financial safety.
                            </p>

                        </div>


                        {/* What ArthMitra can do */}

                        <div>

                            <p className="
                                text-white
                                font-semibold
                                mb-4
                            ">
                                What I can help with
                            </p>


                            <div className="space-y-3">


                                {/* Government schemes */}

                                <div className="
                                    flex
                                    items-center
                                    gap-4
                                    p-4
                                    rounded-2xl
                                    bg-white/10
                                    border
                                    border-white/10
                                    backdrop-blur-sm
                                ">

                                    <div className="
                                        w-11
                                        h-11
                                        rounded-xl
                                        bg-indigo-500/30
                                        flex
                                        items-center
                                        justify-center
                                        text-xl
                                        shrink-0
                                    ">
                                        🏛️
                                    </div>


                                    <div>

                                        <p className="
                                            text-white
                                            font-medium
                                        ">
                                            Government Schemes
                                        </p>

                                        <p className="
                                            text-slate-400
                                            text-xs
                                            mt-1
                                        ">
                                            Eligibility & benefits
                                        </p>

                                    </div>

                                </div>


                                {/* Banking */}

                                <div className="
                                    flex
                                    items-center
                                    gap-4
                                    p-4
                                    rounded-2xl
                                    bg-white/10
                                    border
                                    border-white/10
                                    backdrop-blur-sm
                                ">

                                    <div className="
                                        w-11
                                        h-11
                                        rounded-xl
                                        bg-blue-500/30
                                        flex
                                        items-center
                                        justify-center
                                        text-xl
                                        shrink-0
                                    ">
                                        🏦
                                    </div>


                                    <div>

                                        <p className="
                                            text-white
                                            font-medium
                                        ">
                                            Banking Literacy
                                        </p>

                                        <p className="
                                            text-slate-400
                                            text-xs
                                            mt-1
                                        ">
                                            Accounts, KYC & payments
                                        </p>

                                    </div>

                                </div>


                                {/* Fraud */}

                                <div className="
                                    flex
                                    items-center
                                    gap-4
                                    p-4
                                    rounded-2xl
                                    bg-white/10
                                    border
                                    border-white/10
                                    backdrop-blur-sm
                                ">

                                    <div className="
                                        w-11
                                        h-11
                                        rounded-xl
                                        bg-emerald-500/30
                                        flex
                                        items-center
                                        justify-center
                                        text-xl
                                        shrink-0
                                    ">
                                        🛡️
                                    </div>


                                    <div>

                                        <p className="
                                            text-white
                                            font-medium
                                        ">
                                            Fraud Awareness
                                        </p>

                                        <p className="
                                            text-slate-400
                                            text-xs
                                            mt-1
                                        ">
                                            UPI & digital safety
                                        </p>

                                    </div>

                                </div>

                            </div>

                        </div>

                    </div>


                    {/* Safety note */}

                    <div className="
                        mt-8
                        pt-6
                        border-t
                        border-white/10
                    ">

                        <div className="
                            flex
                            items-start
                            gap-3
                        ">

                            <span className="text-lg">
                                🔒
                            </span>

                            <div>

                                <p className="
                                    text-white
                                    text-sm
                                    font-medium
                                ">
                                    Your safety comes first
                                </p>

                                <p className="
                                    text-slate-400
                                    text-xs
                                    leading-relaxed
                                    mt-1
                                ">
                                    Never share your OTP, PIN,
                                    password or card details.
                                </p>

                            </div>

                        </div>

                    </div>

                </aside>


                {/* ==================================================
                    RIGHT 70% — VOICE / CHAT
                ================================================== */}

                <main className="
                    w-full
                    lg:w-[70%]
                    min-h-screen
                    flex
                    flex-col
                    bg-white/95
                    backdrop-blur-xl
                ">


                    {/* Top bar */}

                    <div className="
                        shrink-0
                        px-6
                        md:px-10
                        py-5
                        border-b
                        border-slate-200
                        bg-white/90
                        flex
                        flex-col
                        sm:flex-row
                        sm:items-center
                        sm:justify-between
                        gap-4
                    ">

                        <div>

                            <p className="
                                text-xs
                                text-indigo-500
                                font-semibold
                                uppercase
                                tracking-wider
                            ">
                                Financial Assistant
                            </p>

                            <h2 className="
                                text-xl
                                font-bold
                                text-slate-800
                                mt-1
                            ">
                                Talk to ArthMitra
                            </h2>

                        </div>


                        <StatusBadge status={status} />

                    </div>


                    {/* Error */}

                    {errorMessage && (

                        <div className="
                            shrink-0
                            mx-6
                            md:mx-10
                            mt-5
                            rounded-2xl
                            border
                            border-red-200
                            bg-red-50
                            px-5
                            py-4
                        ">

                            <p className="
                                text-red-700
                                font-medium
                                text-sm
                            ">
                                ⚠️ {errorMessage}
                            </p>

                            <p className="
                                text-red-600
                                text-xs
                                mt-1
                            ">
                                Check your browser microphone
                                permissions and try again.
                            </p>

                        </div>

                    )}


                    {/* ==================================================
                        READY
                    ================================================== */}

                    {status === "ready" && (

                        <div className="
                            flex-1
                            flex
                            items-center
                            justify-center
                            px-6
                            py-10
                        ">

                            <div className="
                                text-center
                                max-w-lg
                            ">

                                <div className="
                                    w-24
                                    h-24
                                    mx-auto
                                    rounded-full
                                    bg-gradient-to-br
                                    from-indigo-100
                                    to-blue-100
                                    flex
                                    items-center
                                    justify-center
                                    text-5xl
                                    shadow-inner
                                    mb-6
                                ">
                                    🎙️
                                </div>


                                <h2 className="
                                    text-3xl
                                    font-bold
                                    text-slate-800
                                ">
                                    Ready to talk?
                                </h2>


                                <p className="
                                    text-slate-500
                                    mt-3
                                    leading-relaxed
                                ">
                                    Ask about government schemes,
                                    banking, UPI, or how to stay
                                    safe from financial fraud.
                                </p>


                                <button
                                    onClick={startCall}
                                    className="
                                        mt-7
                                        px-9
                                        py-4
                                        rounded-2xl
                                        bg-indigo-600
                                        hover:bg-indigo-700
                                        text-white
                                        font-semibold
                                        shadow-lg
                                        hover:shadow-xl
                                        hover:-translate-y-0.5
                                        transition-all
                                    "
                                >
                                    🎙️ Start Voice Call
                                </button>


                                <p className="
                                    text-slate-400
                                    text-xs
                                    mt-4
                                ">
                                    Your microphone will be used
                                    for the conversation.
                                </p>

                            </div>

                        </div>

                    )}


                    {/* ==================================================
                        CONNECTING
                    ================================================== */}

                    {status === "connecting" && (

                        <div className="
                            flex-1
                            flex
                            items-center
                            justify-center
                            px-6
                        ">

                            <div className="text-center">

                                <div className="
                                    w-20
                                    h-20
                                    mx-auto
                                    rounded-full
                                    bg-indigo-100
                                    flex
                                    items-center
                                    justify-center
                                    text-4xl
                                    animate-pulse
                                ">
                                    🔄
                                </div>


                                <h2 className="
                                    text-2xl
                                    font-bold
                                    text-slate-800
                                    mt-6
                                ">
                                    Connecting...
                                </h2>


                                <p className="
                                    text-slate-500
                                    mt-2
                                ">
                                    Please wait while we connect
                                    you to ArthMitra AI.
                                </p>

                            </div>

                        </div>

                    )}


                    {/* ==================================================
                        CHAT AREA
                    ================================================== */}

                    {(callActive || status === "ended") && (

                        <div className="
                            flex-1
                            min-h-0
                            flex
                            flex-col
                            px-4
                            md:px-8
                            py-5
                        ">


                            {/* Conversation panel now fills
                                the entire available right area */}

                            <div className="
                                flex-1
                                min-h-0
                                overflow-y-auto
                                rounded-3xl
                                bg-slate-50
                                border
                                border-slate-200
                                p-5
                                md:p-7
                            ">


                                {messages.length === 0 && (

                                    <div className="
                                        h-full
                                        flex
                                        items-center
                                        justify-center
                                        text-center
                                    ">

                                        <div>

                                            <div className="
                                                text-5xl
                                                mb-4
                                            ">
                                                💬
                                            </div>

                                            <p className="
                                                text-slate-500
                                                font-medium
                                            ">
                                                Your conversation
                                                will appear here.
                                            </p>

                                            <p className="
                                                text-slate-400
                                                text-sm
                                                mt-1
                                            ">
                                                Start speaking naturally
                                                with ArthMitra.
                                            </p>

                                        </div>

                                    </div>

                                )}


                                <div className="
                                    max-w-4xl
                                    mx-auto
                                ">

                                    {messages.map((msg, index) => {

                                        if (
                                            msg.type === "transcript"
                                        ) {

                                            return (

                                                <ChatBubble
                                                    key={index}
                                                    sender="user"
                                                    message={msg.text}
                                                />

                                            );

                                        }


                                        if (
                                            msg.type === "reply"
                                        ) {

                                            return (

                                                <ChatBubble
                                                    key={index}
                                                    sender="assistant"
                                                    message={msg.text}
                                                />

                                            );

                                        }


                                        return null;

                                    })}

                                </div>

                            </div>


                            {/* Voice controls */}

                            {callActive &&
                                status !== "connecting" && (

                                <div className="
                                    shrink-0
                                    pt-5
                                    flex
                                    flex-col
                                    items-center
                                ">

                                    <VoiceButton
                                        active={callActive}
                                        status={status}
                                        onStatusChange={setStatus}
                                        onMicrophoneError={
                                            handleMicrophoneError
                                        }
                                    />


                                    <button
                                        onClick={endCall}
                                        className="
                                            mt-4
                                            px-6
                                            py-2.5
                                            rounded-xl
                                            border
                                            border-red-200
                                            text-red-600
                                            hover:bg-red-50
                                            font-medium
                                            text-sm
                                            transition
                                        "
                                    >
                                        📞 End Call
                                    </button>

                                </div>

                            )}


                            {/* Call ended */}

                            {status === "ended" && (

                                <div className="
                                    shrink-0
                                    text-center
                                    py-5
                                ">

                                    <span className="
                                        inline-flex
                                        w-12
                                        h-12
                                        rounded-full
                                        bg-emerald-100
                                        items-center
                                        justify-center
                                        text-xl
                                    ">
                                        ✓
                                    </span>


                                    <h3 className="
                                        text-lg
                                        font-bold
                                        text-slate-800
                                        mt-2
                                    ">
                                        Call ended
                                    </h3>


                                    <p className="
                                        text-slate-500
                                        text-sm
                                        mt-1
                                    ">
                                        Thank you for using
                                        ArthMitra AI.
                                    </p>


                                    <button
                                        onClick={restartCall}
                                        className="
                                            mt-4
                                            px-7
                                            py-3
                                            rounded-xl
                                            bg-indigo-600
                                            hover:bg-indigo-700
                                            text-white
                                            font-semibold
                                            transition
                                        "
                                    >
                                        🔄 Start Again
                                    </button>

                                </div>

                            )}

                        </div>

                    )}

                </main>

            </div>

        </div>
    );
}


export default App;
