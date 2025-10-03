import { useState, useEffect, useRef } from "react";

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [useRag, setUseRag] = useState(true);
  const endRef = useRef(null);

  // Auto-scroll when messages change
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    const text = input.trim();
    if (!text) return;

    // Add user message using functional update to avoid drops
    setMessages((msgs) => [...msgs, { role: "user", text }]);
    setInput("");

    try {
      const resp = await fetch(import.meta.env.VITE_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": import.meta.env.VITE_API_KEY,
        },
        body: JSON.stringify({ text, use_rag: useRag }),
      });

      const data = await resp.json();
      const reply = typeof data?.reply === "string" ? data.reply : "Okay.";

      // Append bot reply
      setMessages((msgs) => [...msgs, { role: "bot", text: reply }]);
    } catch {
      setMessages((msgs) => [
        ...msgs,
        { role: "bot", text: "Error contacting server." },
      ]);
    }
  }

  return (
    <div className="flex h-full flex-col">
      {/* Messages area: scrollable and allowed to shrink to enable overflow scroll */}
      <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-3 bg-white">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg max-w-[80%] break-words ${
              m.role === "user"
                ? "bg-blue-600 text-white self-end ml-auto"
                : "bg-gray-200 text-gray-900 self-start mr-auto"
            }`}
          >
            {m.text}
          </div>
        ))}
        <div ref={endRef} />
      </div>

      {/* Input bar: pinned */}
      <div className="p-3 border-t flex items-center gap-2 bg-white shrink-0">
        <input
          className="flex-1 border rounded p-2 text-sm"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button
          onClick={sendMessage}
          className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-md transform transition hover:scale-105 hover:shadow-lg active:scale-95"
        >
          🚀 Send
        </button>
      </div>

      {/* Toggle: pinned */}
      <div className="p-2 text-xs text-gray-600 flex items-center gap-2 bg-white border-t shrink-0">
        <label className="flex items-center gap-2">
          {/* <input
            type="checkbox"
            checked={useRag}
            onChange={(e) => setUseRag(e.target.checked)}
          /> */}
          {/* <span>Use RAG</span> */}
        </label>
      </div>
    </div>
  );
}
import { useState, useEffect, useRef } from "react";

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [useRag, setUseRag] = useState(true);
  const endRef = useRef(null);

  // Auto-scroll when messages change
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    const text = input.trim();
    if (!text) return;

    setMessages((msgs) => [...msgs, { role: "user", text }]);
    setInput("");

    try {
      const resp = await fetch(import.meta.env.VITE_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": import.meta.env.VITE_API_KEY,
        },
        body: JSON.stringify({ text, use_rag: useRag }),
      });

      if (!resp.ok) throw new Error("Network error");
      const data = await resp.json();
      const reply = typeof data?.reply === "string" ? data.reply : "Okay.";

      setMessages((msgs) => [...msgs, { role: "bot", text: reply }]);
    } catch (err) {
      setMessages((msgs) => [
        ...msgs,
        { role: "system", text: "Error contacting server." },
      ]);
    }
  }

  return (
    <div className="flex h-full flex-col">
      {/* Messages area */}
      <div className="flex-1 min-h-0 overflow-y-auto p-3 space-y-3 bg-white flex flex-col">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg max-w-[80%] break-words ${
              m.role === "user"
                ? "bg-blue-600 text-white self-end ml-auto"
                : m.role === "bot"
                ? "bg-gray-200 text-gray-900 self-start mr-auto"
                : "text-red-600 text-sm text-center w-full"
            }`}
          >
            {m.text}
          </div>
        ))}
        <div ref={endRef} />
      </div>

      {/* Input bar */}
      <div className="p-3 border-t flex items-center gap-2 bg-white shrink-0">
        <input
          className="flex-1 border rounded p-2 text-sm"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button
          onClick={sendMessage}
          className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-md transform transition hover:scale-105 hover:shadow-lg active:scale-95"
        >
          🚀 Send
        </button>
      </div>

      {/* Toggle (optional) */}
      <div className="p-2 text-xs text-gray-600 flex items-center gap-2 bg-white border-t shrink-0">
        {/* Uncomment if you want a visible toggle */}
        {/* <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={useRag}
            onChange={(e) => setUseRag(e.target.checked)}
          />
          <span>Use RAG</span>
        </label> */}
      </div>
    </div>
  );
}
