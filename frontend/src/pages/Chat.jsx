import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import api from "../api/axios";

export default function Chat() {
  const { chatId } = useParams();
  const [chats, setChats] = useState([]);
  const [messages, setMessages] = useState([]);
  const [chatTitle, setChatTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchHistory = useCallback(async () => {
    try {
      const response = await api.get("/chat/history");
      setChats(response.data.chats);
    } catch {
      setChats([]);
    }
  }, []);

  const fetchChat = useCallback(async () => {
    if (!chatId) return;

    setLoading(true);
    setError("");

    try {
      const response = await api.get(`/chat/${chatId}`);
      setMessages(response.data.messages);
      setChatTitle(response.data.title);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === "string" ? detail : "Failed to load chat. Please try again."
      );
      setMessages([]);
    } finally {
      setLoading(false);
    }
  }, [chatId]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  useEffect(() => {
    fetchChat();
  }, [fetchChat]);

  const handleTitleUpdate = (newTitle) => {
    setChatTitle(newTitle);
    setChats((prev) =>
      prev.map((chat) =>
        chat.id === chatId ? { ...chat, title: newTitle } : chat
      )
    );
  };

  const handleChatCreated = (newChat) => {
    setChats((prev) => [newChat, ...prev]);
  };

  return (
    <div className="flex h-full">
      <Sidebar
        chats={chats}
        onChatsUpdate={setChats}
        onChatCreated={handleChatCreated}
      />

      <main className="flex flex-1 flex-col pt-14 lg:pt-0">
        <div className="border-b border-gray-200 bg-white px-4 py-3 sm:px-6">
          <h2 className="truncate text-sm font-semibold text-gray-800 sm:text-base">
            {chatTitle || "Chat"}
          </h2>
        </div>

        {loading ? (
          <div className="flex flex-1 items-center justify-center">
            <p className="text-sm text-gray-400">Loading chat...</p>
          </div>
        ) : error ? (
          <div className="flex flex-1 items-center justify-center px-4">
            <p className="text-sm text-red-500">{error}</p>
          </div>
        ) : (
          <ChatWindow
            chatId={chatId}
            initialMessages={messages}
            onTitleUpdate={handleTitleUpdate}
          />
        )}
      </main>
    </div>
  );
}
