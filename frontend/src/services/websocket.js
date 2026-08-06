let socket = null;
let isConnecting = false;

export const connectSocket = (onMessage) => {
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
    };

    socket.onclose = () => {
        console.log("❌ WebSocket Closed");
        isConnecting = false;
    };

    socket.onerror = (err) => {
        console.error("WebSocket Error:", err);
    };

    socket.onmessage = (event) => {
        try {
            
            const data = JSON.parse(event.data);
            if (data.type === "reply") {
                const audio = new Audio(data.audio);
                audio.play();

            }
            onMessage(data);
        } catch {
            console.log(event.data);
        }
    };
};

export const getSocket = () => socket;

export const sendJSON = (data) => {
    if (!socket) return false;

    if (socket.readyState !== WebSocket.OPEN) {
        return false;
    }

    socket.send(JSON.stringify(data));
    return true;
};

export const sendAudio = (buffer) => {
    if (!socket) return false;

    if (socket.readyState !== WebSocket.OPEN) {
        return false;
    }

    socket.send(buffer);
    return true;
};