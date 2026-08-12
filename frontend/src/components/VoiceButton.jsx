import { useRef, useState } from "react";
import { sendAudio, getSocket } from "../services/websocket";

export default function VoiceButton({
    active,
    status,
    onStatusChange,
    onMicrophoneError
}) {

    const recorderRef = useRef(null);
    const chunksRef = useRef([]);
    const timerRef = useRef(null);

    const [recording, setRecording] = useState(false);


    const startRecording = async () => {

        const socket = getSocket();

        if (!socket || socket.readyState !== WebSocket.OPEN) {

            console.log("WebSocket is not connected");

            return;
        }


        try {

            const stream = await navigator.mediaDevices.getUserMedia({
                audio: true
            });


            const recorder = new MediaRecorder(
                stream,
                {
                    mimeType: "audio/webm;codecs=opus"
                }
            );


            recorderRef.current = recorder;

            chunksRef.current = [];


            recorder.ondataavailable = (event) => {

                if (event.data.size > 0) {

                    chunksRef.current.push(event.data);

                }

            };


            recorder.onstop = async () => {

                clearTimeout(timerRef.current);


                const blob = new Blob(
                    chunksRef.current,
                    {
                        type: recorder.mimeType
                    }
                );


                console.log("MIME:", recorder.mimeType);

                console.log("Audio size:", blob.size);


                const arrayBuffer = await blob.arrayBuffer();


                const sent = sendAudio(arrayBuffer);


                if (!sent) {

                    console.error("Failed to send audio");

                }


                stream
                    .getTracks()
                    .forEach(track => track.stop());


                setRecording(false);

            };


            recorder.onerror = (event) => {

                console.error("Recorder error:", event);

                stream
                    .getTracks()
                    .forEach(track => track.stop());

                setRecording(false);

                onStatusChange("listening");

            };


            recorder.start();


            setRecording(true);

            onStatusChange("listening");


            console.log("🎤 Recording started");


            // Current backend expects a complete recording.
            // Keep the existing 5-second recording behaviour.
            timerRef.current = setTimeout(() => {

                if (recorder.state !== "inactive") {

                    recorder.stop();

                    onStatusChange("speaking");

                }

            }, 7000);


        } catch (error) {

            console.error("Microphone error:", error);


            setRecording(false);


            if (
                error.name === "NotAllowedError" ||
                error.name === "PermissionDeniedError"
            ) {

                onMicrophoneError(
                    "Microphone access was blocked. Please allow microphone permission in your browser settings and try again."
                );

            } else if (error.name === "NotFoundError") {

                onMicrophoneError(
                    "No microphone was found. Please connect a microphone and try again."
                );

            } else {

                onMicrophoneError(
                    "We couldn't access your microphone. Please check your browser permissions and try again."
                );

            }

            onStatusChange("ready");
        }

    };


    const stopRecording = () => {

        clearTimeout(timerRef.current);


        if (
            recorderRef.current &&
            recorderRef.current.state !== "inactive"
        ) {

            recorderRef.current.stop();

        }

    };


    if (!active) {

        return null;

    }


    return (

        <div className="flex flex-col items-center gap-5">


            <button

                onClick={
                    recording
                        ? stopRecording
                        : startRecording
                }

                disabled={
                    status === "connecting" ||
                    status === "speaking"
                }

                className={`
                    relative
                    w-28
                    h-28
                    rounded-full
                    text-white
                    text-5xl
                    shadow-xl
                    transition-all
                    duration-300

                    ${
                        recording

                            ? "bg-red-500 scale-110 shadow-red-300 animate-pulse"

                            : status === "speaking"

                            ? "bg-emerald-500"

                            : "bg-indigo-600 hover:bg-indigo-700 hover:scale-105"
                    }

                    disabled:opacity-60
                    disabled:cursor-not-allowed
                `}
            >

                {recording ? "⏹" : "🎙️"}

            </button>


            <div className="text-center">

                <p className="text-gray-800 font-semibold">

                    {recording

                        ? "Listening to you..."

                        : status === "speaking"

                        ? "ArthMitra is speaking..."

                        : "Tap to speak"

                    }

                </p>


                <p className="text-gray-500 text-sm mt-1">

                    {recording

                        ? "Speak naturally"

                        : status === "speaking"

                        ? "Please wait for the response"

                        : "Your microphone is ready"

                    }

                </p>

            </div>


            {recording && (

                <div className="flex items-end gap-1 h-8">

                    <span className="w-1 bg-indigo-500 rounded-full animate-pulse h-3"></span>

                    <span className="w-1 bg-indigo-500 rounded-full animate-pulse h-6"></span>

                    <span className="w-1 bg-indigo-500 rounded-full animate-pulse h-8"></span>

                    <span className="w-1 bg-indigo-500 rounded-full animate-pulse h-5"></span>

                    <span className="w-1 bg-indigo-500 rounded-full animate-pulse h-3"></span>

                </div>

            )}

        </div>

    );
}