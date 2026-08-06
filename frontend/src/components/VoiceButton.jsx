import { useRef, useState } from "react";
import { sendAudio, getSocket } from "../services/websocket";

export default function VoiceButton() {

    const recorderRef = useRef(null);
    const chunksRef = useRef([]);

    const [recording, setRecording] = useState(false);

    const startRecording = async () => {

        const socket = getSocket();

        if (!socket || socket.readyState !== WebSocket.OPEN) {
            alert("WebSocket is still connecting.\nWait 2 seconds and try again.");
            return;
        }

        const stream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });

        const recorder = new MediaRecorder(stream, {
            mimeType: "audio/webm;codecs=opus"
        });
        recorderRef.current = recorder;
        chunksRef.current = [];

        recorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                chunksRef.current.push(event.data);
            }
        };

        recorder.onstop = async () => {

            const blob = new Blob(chunksRef.current, {
                type: recorder.mimeType
            });

            console.log("MIME:", recorder.mimeType);
            console.log("Size:", blob.size);

            const arrayBuffer = await blob.arrayBuffer();

            sendAudio(arrayBuffer);

            stream.getTracks().forEach(track => track.stop());

            setRecording(false);
        };

        console.log("Recorder MIME:", recorder.mimeType);

        recorder.start();

        setRecording(true);

        setTimeout(() => {

            recorder.stop();

        }, 5000);
    };

    return (

        <div className="flex flex-col items-center gap-4">

        <button

        onClick={startRecording}

        disabled={recording}

        className={`
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
        ? "bg-red-500 animate-pulse scale-110"
        : "bg-indigo-600 hover:scale-105"
        }
        `}
        >

        🎤

        </button>

        <p className="text-gray-600 font-medium">

        {recording ? "Listening..." : "Tap to Speak"}

        </p>

        </div>

        );
        }