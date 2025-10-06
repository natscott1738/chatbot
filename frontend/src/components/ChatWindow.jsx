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

const HEADER_AVATAR_SRC = "/chatbot-avatar.png";
const BUBBLE_AVATAR_SRC = "/bot-bubble-avatar.png";
const BUBBLE_AVATAR_FALLBACK = "/fallback-bot.png";

export default function ChatWindow({ onClose }) {
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hi! 👋 Welcome to CBK Assistant.", timestamp: new Date() },
  ]);
  const [input, setInput] = useState("");
  const [expanded, setExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showBanner, setShowBanner] = useState(false);
  const [language, setLanguage] = useState("en"); // "en" or "sw"

  const endRef = useRef(null);
  const fileInputRef = useRef(null);

  const [headerAvatarSrc, setHeaderAvatarSrc] = useState(HEADER_AVATAR_SRC);
  const [bubbleAvatarSrc, setBubbleAvatarSrc] = useState(BUBBLE_AVATAR_SRC);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  // Send text message to backend
  async function handleSend(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;

    setMessages((msgs) => [...msgs, { role: "user", text, timestamp: new Date() }]);
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
        body: JSON.stringify({ text, lang: language }),
      });

      const payload = await resp.json();
      if (!resp.ok) throw new Error(`Backend error: ${resp.status}`);

      const reply =
        payload?.reply ??
        payload?.message ??
        payload?.content ??
        payload?.data?.reply ??
        "...";

      setMessages((msgs) => [...msgs, { role: "bot", text: reply, timestamp: new Date() }]);
    } catch (err) {
      console.error("Fetch error:", err);
      setMessages((msgs) => [
        ...msgs,
        { role: "system", text: "Error contacting server.", timestamp: new Date() },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  // Upload file to backend (/v1/upload)
  async function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    setMessages((msgs) => [
      ...msgs,
      { role: "user", text: `📎 Uploaded: ${file.name}`, timestamp: new Date() },
    ]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const base = import.meta.env.VITE_API_URL;
      const key = import.meta.env.VITE_API_KEY;
      if (!base) throw new Error("VITE_API_URL is missing");

      const url = `${base}/v1/upload`;
      const resp = await fetch(url, {
        method: "POST",
        headers: {
          ...(key ? { "X-API-Key": key } : {}),
        },
        body: formData,
      });

      const payload = await resp.json();
      if (!resp.ok) throw new Error(`Upload error: ${resp.status}`);

      const reply =
        payload?.reply ??
        payload?.message ??
        payload?.content ??
        payload?.data?.reply ??
        "File received.";

      setMessages((msgs) => [...msgs, { role: "bot", text: reply, timestamp: new Date() }]);
    } catch (err) {
      console.error("Upload error:", err);
      setMessages((msgs) => [
        ...msgs,
        { role: "system", text: "Error uploading file.", timestamp: new Date() },
      ]);
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  // Restart conversation
  function handleRestart() {
    setMessages([]); // clear conversation
    setShowBanner(true);
    setTimeout(() => setShowBanner(false), 4000);
    // Add fresh greeting in current language
    setTimeout(() => {
      setMessages([
        {
          role: "bot",
          text:
            language === "en"
              ? "Hi! 👋 Welcome to CBK Assistant."
              : "Habari! 👋 Karibu kwa CBK Assistant.",
          timestamp: new Date(),
        },
      ]);
    }, 600);
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
    const newLang = language === "en" ? "sw" : "en";
    setLanguage(newLang);

    // Reset conversation with new greeting
    setMessages([
      {
        role: "bot",
        text:
          newLang === "en"
            ? "Language switched to English. 👋"
            : "Lugha imebadilishwa kuwa Kiswahili. 👋",
        timestamp: new Date(),
      },
    ]);
  }

  // Format timestamp like 14:07
  function fmtTime(ts) {
    try {
      return new Date(ts).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch {
      return "";
    }
  }
  return (
    <motion.div
      initial={{ opacity: 0, y: 50, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 50, scale: 0.95 }}
      transition={{ duration: 0.3 }}
      className={`flex flex-col bg-white shadow-2xl overflow-hidden ${
        expanded ? "fixed inset-0 rounded-none" : "w-full h-full sm:w-[400px] sm:h-[600px] rounded-xl"
      }`}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-3 flex justify-between items-center">
        <div className="flex items-center gap-2">
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
        {/* Restart banner */}
        <AnimatePresence>
          {showBanner && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="mx-auto bg-gradient-to-r from-blue-500 to-indigo-500 text-white text-sm px-4 py-2 rounded-full shadow-md"
            >
              🔄 Conversation restarted — starting fresh!
            </motion.div>
          )}
        </AnimatePresence>

        {/* Chat messages */}
        <AnimatePresence>
          {messages.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className={`flex items-start gap-2 ${
                m.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {m.role === "bot" && (
                <img
                  src={bubbleAvatarSrc}
                  alt="Bot"
                  className="w-7 h-7 rounded-full border border-gray-300 shadow-sm"
                  onError={() => setBubbleAvatarSrc(BUBBLE_AVATAR_FALLBACK)}
                />
              )}

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
                {m.timestamp && (
                  <div
                    className={`text-[10px] mt-1 ${
                      m.role === "user"
                        ? "text-blue-200 text-right"
                        : "text-gray-400 text-right"
                    }`}
                  >
                    {fmtTime(m.timestamp)}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex items-center gap-2 text-gray-500 text-sm italic">
            <motion.img
              src={bubbleAvatarSrc}
              alt="Bot typing"
              className="w-6 h-6 rounded-full border border-gray-300"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ repeat: Infinity, duration: 1.2 }}
              onError={() => setBubbleAvatarSrc(BUBBLE_AVATAR_FALLBACK)}
            />
            <motion.span
              className="flex gap-1"
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
            >
              <span>•</span>
              <span>•</span>
              <span>•</span>
            </motion.span>
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
          placeholder={language === "en" ? "Type your message..." : "Andika ujumbe wako..."}
        />

        {/* Upload */}
        <label
          htmlFor="chat-file-upload"
          className="p-2 text-gray-500 hover:text-blue-600 cursor-pointer"
          title="Upload file"
        >
          <FiPaperclip />
        </label>
        <input
          id="chat-file-upload"
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.txt,.csv,.png,.jpg,.jpeg"
          onChange={handleFileUpload}
        />

        {/* Send */}
        <button
          type="submit"
          className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          title="Send message"
        >
          <FiSend />
        </button>
      </form>
    </motion.div>
  );
}

