import { useEffect, useState } from "react";
import Header from "./components/Header";
import StatusBadge from "./components/StatusBadge";
import ChatBubble from "./components/ChatBubble";
import VoiceButton from "./components/VoiceButton";
import { connectSocket } from "./services/websocket";

function App() {

    const [messages, setMessages] = useState([]);

    useEffect(() => {

        connectSocket((message) => {

            console.log(message);

            setMessages(prev => [...prev, message]);

        });

    }, []);

    return (

    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100 flex justify-center items-center">

    <div className="w-[800px] bg-white rounded-3xl shadow-2xl p-10">

    <Header/>

    <StatusBadge status="connected"/>

    <div className="bg-slate-100 rounded-2xl p-6 h-[350px] overflow-y-auto mb-8">

    {messages.map((msg,index)=>{

    if(msg.type==="transcript"){

    return(

    <ChatBubble

    key={index}

    sender="user"

    message={msg.text}

    />

    )

    }

    if(msg.type==="reply"){

    return(

    <ChatBubble

    key={index}

    sender="assistant"

    message={msg.text}

    />

    )

    }

    return null

    })}

    </div>

    <div className="flex justify-center">

    <VoiceButton/>

    </div>

    </div>

    </div>

    );

}

export default App;