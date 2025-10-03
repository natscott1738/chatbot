import { useState } from "react";
import ChatWidget from "./components/ChatWidget";
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
          className="fixed bottom-4 right-4 bg-blue-600 text-white p-4 rounded-full shadow-lg"
        >
          💬
        </button>
      )}

      {/* Chat widget overlay */}
      {isOpen && (
        <div className="fixed bottom-16 right-4 w-96 h-[500px] shadow-xl rounded-lg overflow-hidden">
          <ChatWidget />
          <button
            onClick={() => setIsOpen(false)}
            className="absolute top-2 right-2 text-gray-500 hover:text-gray-800"
          >
            ✖
          </button>
        </div>
      )}
    </div>
  );
}
