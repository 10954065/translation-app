import { createContext, useCallback, useContext, useEffect, useReducer } from "react";
import { socket } from "../lib/socket";
import { clearSession, loadSession, saveSession } from "../lib/session";
import { useToast } from "./ToastContext";

const RoomContext = createContext(null);

const initialState = {
  connectionStatus: "connecting", // connecting | connected | reconnecting | disconnected
  view: "home", // home | room
  restoringSession: loadSession() !== null,
  creating: false,
  joining: false,
  sendingMessage: false,
  uploadingPdf: false,
  room: null, // { code, you, participants, pdfDocument }
  messages: [], // kind: "message" | "system" | "pdf"
};

function reducer(state, action) {
  switch (action.type) {
    case "CONNECTION_STATUS":
      return { ...state, connectionStatus: action.status };
    case "SET_CREATING":
      return { ...state, creating: action.value };
    case "SET_JOINING":
      return { ...state, joining: action.value };
    case "SET_SENDING":
      return { ...state, sendingMessage: action.value };
    case "SET_UPLOADING":
      return { ...state, uploadingPdf: action.value };
    case "ROOM_JOINED":
      return {
        ...state,
        view: "room",
        restoringSession: false,
        creating: false,
        joining: false,
        room: {
          code: action.payload.roomCode,
          you: action.payload.you,
          participants: action.payload.participants,
          pdfDocument: action.payload.pdfDocument,
        },
      };
    case "PARTICIPANTS_UPDATED":
      if (!state.room) return state;
      return { ...state, room: { ...state.room, participants: action.participants } };
    case "SYSTEM_MESSAGE": {
      const entry = {
        id: `sys-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        kind: "system",
        text: action.message,
        timestamp: Date.now() / 1000,
      };
      return { ...state, messages: [...state.messages, entry] };
    }
    case "MESSAGE_RECEIVED": {
      const entry = { kind: "message", ...action.payload };
      return { ...state, messages: [...state.messages, entry], sendingMessage: false };
    }
    case "PDF_UPLOAD_STARTED": {
      const entry = {
        id: "pdf-pending",
        kind: "pdf",
        filename: action.filename,
        status: "uploading",
        sharedBy: state.room?.you?.name,
        timestamp: Date.now() / 1000,
      };
      return { ...state, uploadingPdf: true, messages: [...state.messages, entry] };
    }
    case "PDF_SHARED": {
      const hasPending = state.messages.some((m) => m.kind === "pdf" && m.status === "uploading");
      if (hasPending) {
        return {
          ...state,
          messages: state.messages.map((m) =>
            m.kind === "pdf" && m.status === "uploading"
              ? { ...m, filename: action.filename, sharedBy: action.uploadedBy, status: "processing" }
              : m,
          ),
        };
      }
      const entry = {
        id: `pdf-${Date.now()}`,
        kind: "pdf",
        filename: action.filename,
        sharedBy: action.uploadedBy,
        status: "processing",
        timestamp: Date.now() / 1000,
      };
      return { ...state, messages: [...state.messages, entry] };
    }
    case "PDF_TRANSLATION_COMPLETE":
      return {
        ...state,
        uploadingPdf: false,
        messages: state.messages.map((m) =>
          m.kind === "pdf" && (m.status === "uploading" || m.status === "processing")
            ? { ...m, ...action.payload, status: "done", id: m.id === "pdf-pending" ? `pdf-${Date.now()}` : m.id }
            : m,
        ),
      };
    case "PDF_ERROR":
      return {
        ...state,
        uploadingPdf: false,
        messages: state.messages.filter((m) => !(m.kind === "pdf" && (m.status === "uploading" || m.status === "processing"))),
      };
    case "LEAVE_ROOM":
      return { ...initialState, connectionStatus: state.connectionStatus, restoringSession: false };
    case "RESET_FOR_REJOIN_FAILURE":
      return { ...initialState, connectionStatus: state.connectionStatus, restoringSession: false };
    case "STOP_RESTORING":
      return { ...state, restoringSession: false };
    default:
      return state;
  }
}

export function RoomProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const toast = useToast();

  useEffect(() => {
    if (!state.restoringSession) return undefined;
    // Safety net: don't strand the user on the splash forever if the
    // backend is unreachable - socket.io keeps retrying in the background,
    // and a successful rejoin still fires ROOM_JOINED whenever it connects.
    const timeout = setTimeout(() => dispatch({ type: "STOP_RESTORING" }), 8000);
    return () => clearTimeout(timeout);
  }, [state.restoringSession]);

  useEffect(() => {
    socket.connect();

    const onConnect = () => {
      dispatch({ type: "CONNECTION_STATUS", status: "connected" });
      // Fires both on a fresh page load (state.room is still null, but a
      // prior tab may have saved a session) and after a transient network
      // drop (state.room still holds the pre-disconnect room). Either way,
      // the server already dropped our old socket id from the room's
      // participant list on disconnect, so we must re-join, not just resume.
      const session = loadSession();
      if (session) {
        socket.emit("join_room", session);
      }
    };
    const onDisconnect = () => dispatch({ type: "CONNECTION_STATUS", status: "disconnected" });
    const onReconnectAttempt = () => dispatch({ type: "CONNECTION_STATUS", status: "reconnecting" });

    const onRoomJoined = (payload) => {
      dispatch({ type: "ROOM_JOINED", payload });
      saveSession({ name: payload.you.name, language: payload.you.language, roomCode: payload.roomCode });
    };

    const onUserJoined = (payload) => {
      dispatch({ type: "PARTICIPANTS_UPDATED", participants: payload.participants });
      dispatch({ type: "SYSTEM_MESSAGE", message: payload.message });
    };

    const onUserLeft = (payload) => {
      dispatch({ type: "PARTICIPANTS_UPDATED", participants: payload.participants });
      dispatch({ type: "SYSTEM_MESSAGE", message: payload.message });
    };

    const onMessageReceived = (payload) => dispatch({ type: "MESSAGE_RECEIVED", payload });

    const onPdfShared = (payload) => dispatch({ type: "PDF_SHARED", filename: payload.filename, uploadedBy: payload.uploadedBy });

    const onPdfTranslationComplete = (payload) => {
      dispatch({ type: "PDF_TRANSLATION_COMPLETE", payload });
      if (payload.hasExtractableText === false) {
        toast.warning(payload.message || "This PDF has no extractable text.");
      }
    };

    const onTranslationError = (payload) => {
      toast.warning(payload.message || "Translation temporarily unavailable. Showing original text instead.");
    };

    const onError = (payload) => {
      dispatch({ type: "SET_CREATING", value: false });
      dispatch({ type: "SET_JOINING", value: false });
      dispatch({ type: "SET_SENDING", value: false });
      if (payload.code === "invalid_pdf") {
        dispatch({ type: "PDF_ERROR" });
      }
      if (payload.code === "room_not_found" && loadSession()) {
        // room_not_found only reaches here with a saved session when it came
        // from the automatic rejoin-on-connect attempt (manual joins from
        // JoinRoomModal never have a saved session yet) - the room was
        // cleaned up while we were disconnected.
        clearSession();
        dispatch({ type: "RESET_FOR_REJOIN_FAILURE" });
        toast.error("Your room closed while you were disconnected.");
        return;
      }
      toast.error(payload.message || "Something went wrong.");
    };

    socket.on("connect", onConnect);
    socket.on("disconnect", onDisconnect);
    socket.on("reconnect_attempt", onReconnectAttempt);
    socket.on("room_joined", onRoomJoined);
    socket.on("user_joined", onUserJoined);
    socket.on("user_left", onUserLeft);
    socket.on("message_received", onMessageReceived);
    socket.on("pdf_shared", onPdfShared);
    socket.on("pdf_translation_complete", onPdfTranslationComplete);
    socket.on("translation_error", onTranslationError);
    socket.on("error", onError);

    return () => {
      socket.off("connect", onConnect);
      socket.off("disconnect", onDisconnect);
      socket.off("reconnect_attempt", onReconnectAttempt);
      socket.off("room_joined", onRoomJoined);
      socket.off("user_joined", onUserJoined);
      socket.off("user_left", onUserLeft);
      socket.off("message_received", onMessageReceived);
      socket.off("pdf_shared", onPdfShared);
      socket.off("pdf_translation_complete", onPdfTranslationComplete);
      socket.off("translation_error", onTranslationError);
      socket.off("error", onError);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const createRoom = useCallback((name, language) => {
    dispatch({ type: "SET_CREATING", value: true });
    socket.emit("create_room", { name, language });
  }, []);

  const joinRoom = useCallback((name, language, roomCode) => {
    dispatch({ type: "SET_JOINING", value: true });
    socket.emit("join_room", { name, language, roomCode });
  }, []);

  const leaveRoom = useCallback(() => {
    socket.emit("leave_room", {});
    clearSession();
    dispatch({ type: "LEAVE_ROOM" });
  }, []);

  const sendMessage = useCallback((text) => {
    dispatch({ type: "SET_SENDING", value: true });
    socket.emit("send_message", { text });
  }, []);

  const uploadPdf = useCallback((file) => {
    dispatch({ type: "PDF_UPLOAD_STARTED", filename: file.name });
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result.split(",")[1] || "";
      socket.emit("upload_pdf", { filename: file.name, mimeType: file.type, data: base64 });
    };
    reader.onerror = () => {
      dispatch({ type: "PDF_ERROR" });
      toast.error("Could not read the selected file.");
    };
    reader.readAsDataURL(file);
  }, [toast]);

  const value = { state, createRoom, joinRoom, leaveRoom, sendMessage, uploadPdf };

  return <RoomContext.Provider value={value}>{children}</RoomContext.Provider>;
}

export function useRoom() {
  const ctx = useContext(RoomContext);
  if (!ctx) throw new Error("useRoom must be used within RoomProvider");
  return ctx;
}
