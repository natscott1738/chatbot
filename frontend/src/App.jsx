import ChatWidget from "./components/ChatWidget";
import bgImage from "/cbk-bg.png";
import { sendMessage } from "./services/api";

export default function App() {
  // App is just responsible for layout and wiring the API call into ChatWidget
  return (
    <div
      className="h-screen w-screen bg-cover bg-center"
      style={{ backgroundImage: `url(${bgImage})` }}
    >
      <div className="h-full w-full flex flex-col">
        {/* Pass sendMessage down so ChatWidget can call the backend */}
        <ChatWidget onSend={sendMessage} />
      </div>
    </div>
  );
}
