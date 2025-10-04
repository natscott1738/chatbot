import { useState } from "react";
import ChatWindow from "./components/ChatWindow";
import { AnimatePresence } from "framer-motion";
import bgImage from "/cbk-bg.png";

export default function App() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div
      className="h-screen w-screen bg-cover bg-center"
      style={{ backgroundImage: `url(${bgImage})` }}
    >
      {/* Floating button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-4 right-4 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:scale-110 transition"
        >
          💬
        </button>
      )}

      {/* Chat overlay */}
      <AnimatePresence>
        {isOpen && (
          <div
            className="fixed inset-0 sm:inset-auto sm:bottom-16 sm:right-4
                       flex justify-center sm:justify-end items-end sm:items-end"
          >
            <ChatWindow onClose={() => setIsOpen(false)} />
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
