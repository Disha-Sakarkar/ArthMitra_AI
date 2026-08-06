export default function ChatBubble({ sender, message }) {

  const user = sender === "user";

  return (
    <div className={`flex ${user ? "justify-end" : "justify-start"} mb-4`}>

      <div
        className={`max-w-[75%] rounded-2xl px-5 py-4 shadow-lg ${
          user
            ? "bg-blue-600 text-white"
            : "bg-white text-gray-800 border"
        }`}
      >
        <div className="font-semibold mb-2">
          {user ? "👤 You" : "💰 ArthMitra AI"}
        </div>

        <p className="leading-7 whitespace-pre-wrap">
          {message}
        </p>

      </div>

    </div>
  );
}