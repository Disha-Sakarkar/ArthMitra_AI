export default function Header() {
  return (
    <div className="text-center mb-8">

      <div className="w-24 h-24 mx-auto rounded-full bg-gradient-to-br from-indigo-600 to-blue-600 flex items-center justify-center text-5xl shadow-xl">
        💰
      </div>

      <h1 className="text-4xl font-bold text-gray-800 mt-5">
        ArthMitra AI
      </h1>

      <p className="text-gray-600 mt-2 text-lg">
        Your AI Financial Voice Assistant 🇮🇳
      </p>

      <div className="mt-4 inline-flex items-center gap-2 rounded-full bg-indigo-100 px-4 py-2">

        <div className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></div>

        <span className="text-sm font-medium text-indigo-700">
          Banking • Government Schemes • Fraud Awareness
        </span>

      </div>

    </div>
  );
}