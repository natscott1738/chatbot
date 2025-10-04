import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu } from "@headlessui/react"; // for dropdown menu
import { FiX, FiMaximize2, FiMinimize2, FiMoreVertical, FiPaperclip, FiSend } from "react-icons/fi";

export default function ChatWindow({ onClose }) {
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi! 👋 Welcome to CBK Assistant." }
  ]);
  const [input, setInput] = useState("");
  const [expanded, setExpanded] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSend(e) {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages((msgs) => [...msgs, { role: "user", text: input }]);
    setInput("");
  }

  function handleRestart() {
    setMessages([{ role: "bot", text: "Conversation restarted. 👋" }]);
  }

  function handleDownload() {
    const blob = new Blob([JSON.stringify(messages, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "conversation.json";
    a.click();
    URL.revokeObjectURL(url);
  }

  function handleChangeLanguage() {
    alert("Language change feature coming soon!");
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 50, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 50, scale: 0.95 }}
      transition={{ duration: 0.3 }}
      className={`flex flex-col bg-white shadow-2xl overflow-hidden
        ${expanded ? "fixed inset-0 rounded-none" : "w-full h-full sm:w-[400px] sm:h-[600px] rounded-xl"}`}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-3 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <img src="/chatbot-avatar.png" alt="Bot" className="w-8 h-8 rounded-full border border-white" />
          <h2 className="font-semibold">CBK Assistant</h2>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setExpanded(!expanded)} className="hover:text-gray-200">
            {expanded ? <FiMinimize2 /> : <FiMaximize2 />}
          </button>
          <Menu as="div" className="relative">
            <Menu.Button className="hover:text-gray-200">
              <FiMoreVertical />
            </Menu.Button>
            <Menu.Items className="absolute right-0 mt-2 w-48 bg-white text-gray-700 rounded-md shadow-lg z-50">
              <Menu.Item>
                {({ active }) => (
                  <button onClick={handleRestart} className={`block w-full text-left px-4 py-2 ${active && "bg-gray-100"}`}>
                    Restart Conversation
                  </button>
                )}
              </Menu.Item>
              <Menu.Item>
                {({ active }) => (
                  <button onClick={handleDownload} className={`block w-full text-left px-4 py-2 ${active && "bg-gray-100"}`}>
                    Download Conversation
                  </button>
                )}
              </Menu.Item>
              <Menu.Item>
                {({ active }) => (
                  <button onClick={handleChangeLanguage} className={`block w-full text-left px-4 py-2 ${active && "bg-gray-100"}`}>
                    Change Language
                  </button>
                )}
              </Menu.Item>
            </Menu.Items>
          </Menu>
          <button onClick={onClose} className="hover:text-gray-200">
            <FiX />
          </button>
        </div>
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
              className={`max-w-[80%] p-3 rounded-lg ${
                m.role === "user"
                  ? "bg-blue-600 text-white self-end ml-auto"
                  : "bg-gray-200 text-gray-900 self-start mr-auto"
              }`}
            >
              {m.text}
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={endRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="p-3 border-t flex items-center gap-2 bg-white">
        <input
          className="flex-1 border rounded-lg p-2 text-sm focus:ring focus:ring-blue-300"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button type="button" className="p-2 text-gray-500 hover:text-blue-600">
          <FiPaperclip />
        </button>
        <button type="submit" className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          <FiSend />
        </button>
      </form>
    </motion.div>
  );
}
