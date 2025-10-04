import { motion, AnimatePresence } from "framer-motion";
import { useState, useRef, useEffect } from "react";

export default function ChatWindow({ onClose }) {
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi! 👋 Welcome to CBK Assistant." },
    { role: "bot", text: "Choose below:", type: "options", options: [
      { label: "Know more about CBK", icon: "ℹ️" },
      { label: "Schedule a meeting", icon: "📅" },
      { label: "Client Support", icon: "🎧" }
    ]}
  ]);
  const [input, setInput] = useState("");
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 50, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 50, scale: 0.95 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col bg-white rounded-none sm:rounded-xl shadow-2xl
                 w-full h-full sm:w-[400px] sm:h-[600px] overflow-hidden"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-3 flex justify-between items-center">
        <h2 className="font-semibold">💬 CBK Assistant</h2>
        <button onClick={onClose} className="hover:text-gray-200">✖</button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
        <AnimatePresence>
          {messages.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className={`max-w-[80%] ${
                m.role === "user"
                  ? "bg-blue-600 text-white self-end ml-auto rounded-lg p-3"
                  : m.role === "bot"
                  ? "bg-gray-200 text-gray-900 self-start mr-auto rounded-lg p-3"
                  : "text-red-600 text-sm text-center w-full"
              }`}
            >
              {m.text}
              {m.type === "options" && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {m.options.map((opt, idx) => (
                    <button
                      key={idx}
                      className="flex items-center gap-1 px-3 py-1 bg-white border rounded-full text-sm shadow-sm hover:bg-blue-50 transition"
                    >
                      <span>{opt.icon}</span> {opt.label}
                    </button>
                  ))}
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="p-3 border-t flex items-center gap-2 bg-white">
        <input
          className="flex-1 border rounded-lg p-2 text-sm focus:ring focus:ring-blue-300"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-md transform transition hover:scale-105 active:scale-95">
          Send
        </button>
      </div>

      {/* Footer branding */}
      <div className="text-xs text-gray-400 text-center py-1 border-t bg-gray-50">
        Powered by CBK
      </div>
    </motion.div>
  );
}
