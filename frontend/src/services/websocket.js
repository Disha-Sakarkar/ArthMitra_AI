let socket = null;
let isConnecting = false;
let currentAudio = null;

export const connectSocket = (
    onMessage,
    onOpen,
    onClose,
    onError,
    onAudioStart,
    onAudioEnd
) => {

    if (socket && socket.readyState === WebSocket.OPEN) {
        return;
    }

    if (isConnecting) {
        return;
    }

    isConnecting = true;

    socket = new WebSocket("ws://localhost:8000/ws");

    socket.binaryType = "arraybuffer";

    socket.onopen = () => {

        console.log("✅ WebSocket Connected");

        isConnecting = false;

        if (onOpen) {
            onOpen();
        }
    };

    socket.onclose = () => {

        console.log("❌ WebSocket Closed");

        isConnecting = false;

        socket = null;

        if (onClose) {
            onClose();
        }
    };

    socket.onerror = (err) => {

        console.error("WebSocket Error:", err);

        isConnecting = false;

        if (onError) {
            onError(err);
        }
    };

    socket.onmessage = (event) => {

        try {

            const data = JSON.parse(event.data);

            // Every assistant reply has audio
            if (data.type === "reply" && data.audio) {

                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }

                currentAudio = new Audio(data.audio);

                currentAudio.onplay = () => {

                    console.log("🔊 Assistant speaking");

                    if (onAudioStart) {
                        onAudioStart();
                    }
                };

                currentAudio.onended = () => {

                    console.log("🔇 Assistant finished speaking");

                    if (onAudioEnd) {
                        onAudioEnd();
                    }

                    currentAudio = null;
                };

                currentAudio.onerror = () => {

                    console.error("Audio playback failed");

                    if (onAudioEnd) {
                        onAudioEnd();
                    }

                    currentAudio = null;
                };

                currentAudio.play().catch((error) => {

                    console.error("Audio playback blocked:", error);

                    if (onAudioEnd) {
                        onAudioEnd();
                    }

                });
            }

            if (onMessage) {
                onMessage(data);
            }

        } catch {

            console.log("Non-JSON WebSocket message:", event.data);

        }
    };
};


export const disconnectSocket = () => {

    if (currentAudio) {

        currentAudio.pause();

        currentAudio.currentTime = 0;

        currentAudio = null;
    }

    if (socket) {

        if (
            socket.readyState === WebSocket.OPEN ||
            socket.readyState === WebSocket.CONNECTING
        ) {

            socket.close();

        }

        socket = null;
    }

    isConnecting = false;

    console.log("📞 Call ended");
};


export const getSocket = () => socket;


export const sendJSON = (data) => {

    if (!socket) {
        return false;
    }

    if (socket.readyState !== WebSocket.OPEN) {
        return false;
    }

    socket.send(JSON.stringify(data));

    return true;
};


export const sendAudio = (buffer) => {

    if (!socket) {
        return false;
    }

    if (socket.readyState !== WebSocket.OPEN) {
        return false;
    }

    socket.send(buffer);

    return true;
};