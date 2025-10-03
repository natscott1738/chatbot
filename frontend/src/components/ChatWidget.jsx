import { useState } from "react";
import ChatWindow from "./ChatWindow";

export default function ChatWidget() {
  const [open, setOpen] = useState(false);

  return (
    <div>
      <button
        onClick={() => setOpen(!open)}
        className="fixed bottom-6 right-6 bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-4 rounded-full shadow-xl hover:scale-110 transition transform"
        aria-label="Open chat"
      >
        💬
      </button>

      {open && (
        <div className="fixed bottom-20 right-6 w-[450px] h-[650px] bg-white border rounded-xl shadow-2xl flex flex-col animate-slide-up overflow-hidden">
          {/* Header is pinned */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-3 rounded-t-xl flex justify-between items-center shrink-0">
            <span className="font-semibold">CBK Chatbot</span>
            <button
              onClick={() => setOpen(false)}
              className="hover:scale-110 transition"
              aria-label="Close chat"
            >
              ✖
            </button>
          </div>

          {/* Chat window fills remaining height */}
          <div className="flex-1 min-h-0">
            <ChatWindow />
          </div>
        </div>
      )}
    </div>
  );
}
