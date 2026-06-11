import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import api from "../api/axios";

export default function Dashboard() {
  const navigate = useNavigate();
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await api.get("/chat/history");
        setChats(response.data.chats);
      } catch {
        setChats([]);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  const handleChatCreated = (newChat) => {
    setChats((prev) => [newChat, ...prev]);
  };

  const handleNewChatFromWelcome = async () => {
    try {
      const response = await api.post("/chat/new");
      const newChat = {
        id: response.data.chat_id,
        title: response.data.title,
        created_at: response.data.created_at,
        updated_at: response.data.created_at,
      };
      handleChatCreated(newChat);
      navigate(`/chat/${newChat.id}`);
    } catch {
      alert("Failed to create a new chat. Please try again.");
    }
  };

  return (
    <div className="flex h-full">
      <Sidebar
        chats={chats}
        onChatsUpdate={setChats}
        onChatCreated={handleChatCreated}
      />

      <main className="flex flex-1 flex-col">
        <div className="flex flex-1 items-center justify-center px-4 pt-14 lg:pt-0">
          {loading ? (
            <p className="text-sm text-gray-400">Loading...</p>
          ) : (
            <div className="max-w-lg text-center">
              <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-100">
                <svg
                  className="h-8 w-8 text-primary-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900">
                Welcome to LLM Chatbot
              </h2>
              <p className="mt-3 text-gray-500">
                Start a new conversation with your AI assistant powered by Google Gemini.
                Your chats are saved automatically.
              </p>
              <button
                type="button"
                onClick={handleNewChatFromWelcome}
                className="mt-8 rounded-xl bg-primary-600 px-6 py-3 text-sm font-medium text-white transition hover:bg-primary-700"
              >
                Start New Chat
              </button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
