import ChatWindow from "./components/ChatWindow";
import bgImage from "/cbk-bg.png";

export default function App() {
  return (
    <div
      className="h-screen w-screen bg-cover bg-center"
      style={{ backgroundImage: `url(${bgImage})` }}
    >
      <div className="h-full w-full flex flex-col">
        <ChatWindow />
      </div>
    </div>
  );
}
