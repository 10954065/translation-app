import { RoomProvider, useRoom } from "./context/RoomContext";
import { ToastProvider } from "./context/ToastContext";
import { ToastViewport } from "./components/ui/ToastViewport";
import { HomePage } from "./pages/home/HomePage";
import { RoomPage } from "./pages/room/RoomPage";
import { LoaderIcon, TranslateArrowsIcon } from "./components/icons/Icon";

function RestoringSessionSplash() {
  return (
    <div className="session-splash">
      <TranslateArrowsIcon size={28} />
      <p>
        <LoaderIcon size={16} /> Reconnecting to your room…
      </p>
    </div>
  );
}

function Screens() {
  const { state } = useRoom();
  if (state.restoringSession) return <RestoringSessionSplash />;
  return state.view === "room" && state.room ? <RoomPage /> : <HomePage />;
}

export default function App() {
  return (
    <ToastProvider>
      <RoomProvider>
        <Screens />
        <ToastViewport />
      </RoomProvider>
    </ToastProvider>
  );
}
