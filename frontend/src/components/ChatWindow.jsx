import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu } from "@headlessui/react";
import {
  FiX,
  FiMaximize2,
  FiMinimize2,
  FiMoreVertical,
  FiPaperclip,
  FiSend,
} from "react-icons/fi";

// Optional: import from src/assets instead of public
// import headerAvatar from "../assets/chatbot-avatar.png";
// import bubbleAvatar from "../assets/bot-bubble-avatar.png";

// Fallbacks in public (ensure these exist)
const HEADER_AVATAR_SRC = "/chatbot-avatar.png";
const BUBBLE_AVATAR_SRC = "/bot-bubble-avatar.png";
const BUBBLE_AVATAR_FALLBACK = "/fallback-bot.png"; // add a small placeholder to public

export default function ChatWindow({ onClose }) {
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi! 👋 Welcome to CBK Assistant." },
  ]);
  const [input, setInput] = useState("");
  const [expanded, setExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const endRef = useRef(null);
  const [headerAvatarSrc, setHeaderAvatarSrc] = useState(HEADER_AVATAR_SRC);
  const [bubbleAvatarSrc, setBubbleAvatarSrc] = useState(BUBBLE_AVATAR_SRC);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;

    setMessages((msgs) => [...msgs, { role: "user", text }]);
    setInput("");
    setIsLoading(true);

    try {
      const url = import.meta.env.VITE_API_URL;
      const key = import.meta.env.VITE_API_KEY;

      if (!url) throw new Error("VITE_API_URL is missing");
      const resp = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(key ? { "X-API-Key": key } : {}),
        },
        body: JSON.stringify({ text }),
      });

      // Capture non-2xx responses
      const contentType = resp.headers.get("content-type") || "";
      let payload = null;
      if (contentType.includes("application/json")) {
        payload = await resp.json();
      } else {
        const raw = await resp.text();
        console.error("Non-JSON response:", raw);
        throw new Error(`Unexpected content-type: ${contentType}`);
      }

      if (!resp.ok) {
        console.error("Backend error:", resp.status, payload);
        throw new Error(`Backend status ${resp.status}`);
      }

      // Map reply safely
      const reply =
        payload?.reply ??
        payload?.message ??
        payload?.content ??
        payload?.data?.reply ??
        "...";

      setMessages((msgs) => [...msgs, { role: "bot", text: reply }]);
    } catch (err) {
      console.error("Fetch error:", err);
      setMessages((msgs) => [
        ...msgs,
        { role: "system", text: "Error contacting server." },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  function handleRestart() {
    setMessages([{ role: "bot", text: "Conversation restarted. 👋" }]);
  }

  function handleDownload() {
    const blob = new Blob([JSON.stringify(messages, null, 2)], {
      type: "application/json",
    });
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
          {/* Header avatar with fallback */}
          <img
            src={headerAvatarSrc}
            alt="Bot"
            className="w-8 h-8 rounded-full border border-white"
            onError={() => setHeaderAvatarSrc(BUBBLE_AVATAR_FALLBACK)}
          />
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
            <Menu.Items className="absolute right-0 mt-2 w-52 bg-white text-gray-800 rounded-md shadow-lg z-50 py-1">
              <Menu.Item>
                {({ active }) => (
                  <button
                    onClick={handleRestart}
                    className={`block w-full text-left px-4 py-2 ${active ? "bg-gray-100" : ""}`}
                  >
                    Restart Conversation
                  </button>
                )}
              </Menu.Item>
              <Menu.Item>
                {({ active }) => (
                  <button
                    onClick={handleDownload}
                    className={`block w-full text-left px-4 py-2 ${active ? "bg-gray-100" : ""}`}
                  >
                    Download Conversation
                  </button>
                )}
              </Menu.Item>
              <Menu.Item>
                {({ active }) => (
                  <button
                    onClick={handleChangeLanguage}
                    className={`block w-full text-left px-4 py-2 ${active ? "bg-gray-100" : ""}`}
                  >
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
              className={`flex items-start gap-2 ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {/* Bot bubble avatar (different from header) */}
              {m.role === "bot" && (
                <img
                  src={bubbleAvatarSrc}
                  alt="Bot"
                  className="w-7 h-7 rounded-full border border-gray-300 shadow-sm"
                  onError={() => setBubbleAvatarSrc(BUBBLE_AVATAR_FALLBACK)}
                />
              )}

              {/* Message bubble */}
              <div
                className={`p-3 rounded-2xl max-w-[75%] text-sm leading-relaxed ${
                  m.role === "user"
                    ? "bg-blue-600 text-white rounded-br-none"
                    : m.role === "bot"
                    ? "bg-gray-200 text-gray-900 rounded-bl-none"
                    : "text-red-600 text-sm text-center w-full"
                }`}
              >
                {m.text}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <div className="flex items-center gap-2 text-gray-500 text-sm italic">
            <img
              src={bubbleAvatarSrc}
              alt="Bot typing"
              className="w-6 h-6 rounded-full border border-gray-300"
              onError={() => setBubbleAvatarSrc(BUBBLE_AVATAR_FALLBACK)}
            />
            …typing
          </div>
        )}
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
