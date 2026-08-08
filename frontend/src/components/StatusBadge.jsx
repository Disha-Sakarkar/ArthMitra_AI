export default function StatusBadge({ status }) {

    const config = {

        ready: {
            label: "Ready",
            color: "bg-gray-100 text-gray-700",
            dot: "bg-gray-400"
        },

        connecting: {
            label: "Connecting...",
            color: "bg-yellow-100 text-yellow-700",
            dot: "bg-yellow-500"
        },

        listening: {
            label: "Listening to you",
            color: "bg-red-100 text-red-700",
            dot: "bg-red-500"
        },

        speaking: {
            label: "ArthMitra is speaking",
            color: "bg-emerald-100 text-emerald-700",
            dot: "bg-emerald-500"
        },

        ended: {
            label: "Call ended",
            color: "bg-gray-100 text-gray-600",
            dot: "bg-gray-400"
        },

        error: {
            label: "Microphone unavailable",
            color: "bg-red-100 text-red-700",
            dot: "bg-red-500"
        }

    };


    const current = config[status] || config.ready;


    return (

        <div className="flex justify-center mb-6">

            <div
                className={`
                    rounded-full
                    px-5
                    py-2
                    flex
                    items-center
                    gap-3
                    ${current.color}
                `}
            >

                <div
                    className={`
                        w-2.5
                        h-2.5
                        rounded-full
                        ${current.dot}
                        ${
                            status === "connecting" ||
                            status === "listening" ||
                            status === "speaking"
                                ? "animate-pulse"
                                : ""
                        }
                    `}
                />

                <span className="font-medium text-sm">

                    {current.label}

                </span>

            </div>

        </div>

    );
}