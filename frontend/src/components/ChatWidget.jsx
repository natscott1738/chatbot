import { useState, useRef, useEffect } from "react";

export default function ChatWidget({ onSend }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const endRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const data = await onSend(input);
      const botMsg = { role: "bot", text: data.reply || "Okay." };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "system", text: "Error contacting server" },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col flex-1 p-4 bg-white/70 rounded">
      <div className="flex-1 overflow-y-auto space-y-2">
        {messages.map((m, i) => (
          <div
            key={i}
            className={
              m.role === "user"
                ? "text-right text-blue-600"
                : m.role === "bot"
                ? "text-left text-green-700"
                : "text-center text-red-500"
            }
          >
            {m.text}
          </div>
        ))}
        {isLoading && (
          <div className="text-left text-gray-500 italic">…typing</div>
        )}
        <div ref={endRef} />
      </div>
      <form onSubmit={handleSubmit} className="mt-2 flex">
        <input
          className="flex-1 border rounded-l px-2 py-1"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 rounded-r"
        >
          Send
        </button>
      </form>
    </div>
  );
}
