export default function StatusBadge({ status }) {

  const colors = {
    connected: "bg-green-500",
    listening: "bg-red-500",
    thinking: "bg-yellow-500",
    speaking: "bg-blue-500",
  };

  return (

    <div className="flex justify-center mb-6">

      <div className="bg-white rounded-full shadow-md px-5 py-2 flex items-center gap-3">

        <div className={`w-3 h-3 rounded-full ${colors[status]}`}></div>

        <span className="font-medium capitalize">

          {status}

        </span>

      </div>

    </div>

  );

}