import ChatWidget from "./components/ChatWidget";
import bgImage from "/cbk-bg.png"; // ensure file exists in frontend/public/

export default function App() {
  return (
    <div
      className="h-screen w-screen bg-cover bg-center"
      style={{ backgroundImage: `url(${bgImage})` }}
    >
      <div className="h-full w-full flex flex-col">
       
        <ChatWidget />
      </div>
    </div>
  );
}
