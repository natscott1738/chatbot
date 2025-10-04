import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function ChatWindow({ onClose }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    const text = input.trim();
    if (!text) return;

    setMessages((msgs) => [...msgs, { role: "user", text }]);
    setInput("");
    setIsLoading(true);

    try {
      const resp = await fetch(import.meta.env.VITE_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": import.meta.env.VITE_API_KEY,
        },
        body: JSON.stringify({ text }),
      });

      const data = await resp.json();
      setMessages((msgs) => [...msgs, { role: "bot", text: data.reply }]);
    } catch {
      setMessages((msgs) => [
        ...msgs,
        { role: "system", text: "Error contacting server." },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <motion.div
  initial={{ opacity: 0, y: 50, scale: 0.95 }}
  animate={{ opacity: 1, y: 0, scale: 1 }}
  exit={{ opacity: 0, y: 50, scale: 0.95 }}
  transition={{ duration: 0.3 }}
  className="flex flex-col bg-white rounded-none sm:rounded-xl shadow-2xl overflow-hidden
             w-full h-full sm:w-[400px] sm:h-[600px]"
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
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className={`p-3 rounded-lg max-w-[80%] break-words ${
                m.role === "user"
                  ? "bg-blue-600 text-white self-end ml-auto"
                  : m.role === "bot"
                  ? "bg-gray-200 text-gray-900 self-start mr-auto"
                  : "text-red-600 text-sm text-center w-full"
              }`}
            >
              {m.text}
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <div className="flex gap-1 text-gray-500 text-sm">
            <span className="animate-bounce">●</span>
            <span className="animate-bounce delay-150">●</span>
            <span className="animate-bounce delay-300">●</span>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          sendMessage();
        }}
        className="p-3 border-t flex items-center gap-2 bg-white"
      >
        <input
          className="flex-1 border rounded-lg p-2 text-sm focus:ring focus:ring-blue-300"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-md transform transition hover:scale-105 active:scale-95"
        >
          Send
        </button>
      </form>
    </motion.div>
  );
}
