import { useState } from "react";

export default function ChatWidget({ onSend }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { role: "user", text: input }]);

    try {
      const data = await onSend(input);
      setMessages((prev) => [...prev, { role: "bot", text: data.reply }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "system", text: "Error contacting server" },
      ]);
    }

    setInput("");
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
