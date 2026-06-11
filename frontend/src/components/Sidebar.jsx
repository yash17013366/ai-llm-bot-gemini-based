import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../api/axios";

export default function Sidebar({ chats, onChatsUpdate, onChatCreated }) {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [deletingId, setDeletingId] = useState(null);

  const handleNewChat = async () => {
    setCreating(true);
    try {
      const response = await api.post("/chat/new");
      const newChat = {
        id: response.data.chat_id,
        title: response.data.title,
        created_at: response.data.created_at,
        updated_at: response.data.created_at,
      };
      onChatCreated(newChat);
      navigate(`/chat/${newChat.id}`);
      setIsOpen(false);
    } catch {
      alert("Failed to create a new chat. Please try again.");
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteChat = async (id, event) => {
    event.preventDefault();
    event.stopPropagation();

    if (!window.confirm("Delete this chat?")) {
      return;
    }

    setDeletingId(id);
    try {
      await api.delete(`/chat/${id}`);
      const updatedChats = chats.filter((chat) => chat.id !== id);
      onChatsUpdate(updatedChats);

      if (chatId === id) {
        if (updatedChats.length > 0) {
          navigate(`/chat/${updatedChats[0].id}`);
        } else {
          navigate("/dashboard");
        }
      }
    } catch {
      alert("Failed to delete chat. Please try again.");
    } finally {
      setDeletingId(null);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const sidebarContent = (
    <div className="flex h-full flex-col">
      <div className="border-b border-gray-200 p-4">
        <h1 className="text-lg font-bold text-gray-900">LLM Chatbot</h1>
        <p className="text-xs text-gray-500">Powered by Gemini</p>
      </div>

      <div className="p-3">
        <button
          type="button"
          onClick={handleNewChat}
          disabled={creating}
          className="w-full rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {creating ? "Creating..." : "+ New Chat"}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin px-2 pb-2">
        {chats.length === 0 ? (
          <p className="px-3 py-4 text-center text-sm text-gray-400">No chats yet</p>
        ) : (
          <ul className="space-y-1">
            {chats.map((chat) => (
              <li key={chat.id}>
                <Link
                  to={`/chat/${chat.id}`}
                  onClick={() => setIsOpen(false)}
                  className={`group flex items-center justify-between rounded-lg px-3 py-2.5 text-sm transition ${
                    chatId === chat.id
                      ? "bg-primary-50 text-primary-700"
                      : "text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  <span className="truncate pr-2">{chat.title}</span>
                  <button
                    type="button"
                    onClick={(e) => handleDeleteChat(chat.id, e)}
                    disabled={deletingId === chat.id}
                    className="shrink-0 rounded p-1 text-gray-400 opacity-0 transition hover:bg-red-50 hover:text-red-500 group-hover:opacity-100"
                    aria-label="Delete chat"
                  >
                    {deletingId === chat.id ? "..." : "\u00d7"}
                  </button>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="border-t border-gray-200 p-3">
        <button
          type="button"
          onClick={handleLogout}
          className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
        >
          Logout
        </button>
      </div>
    </div>
  );

  return (
    <>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="fixed left-4 top-4 z-40 rounded-lg border border-gray-200 bg-white p-2 shadow-md lg:hidden"
        aria-label="Open sidebar"
      >
        <svg className="h-5 w-5 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 w-72 transform border-r border-gray-200 bg-white transition-transform duration-200 lg:static lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
