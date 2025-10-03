import ChatWidget from "./components/ChatWidget";
import bgImage from "/cbk-bg.png";
import { sendMessage } from "./services/api";

export default function App() {
  return (
    <div
      className="h-screen w-screen bg-cover bg-center"
      style={{ backgroundImage: `url(${bgImage})` }}
    >
      <div className="h-full w-full flex flex-col">
        <ChatWidget onSend={sendMessage} />
      </div>
    </div>
  );
}
