import { useEffect, useRef, useState } from "react";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import api from "../api/axios";

export default function ChatWindow({ chatId, initialMessages = [], onTitleUpdate }) {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [inputError, setInputError] = useState("");
  const [networkError, setNetworkError] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    setMessages(initialMessages);
    setInput("");
    setInputError("");
    setNetworkError("");
  }, [chatId, initialMessages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (event) => {
    event.preventDefault();
    const trimmed = input.trim();

    if (!trimmed) {
      setInputError("Message cannot be empty");
      return;
    }

    setInputError("");
    setNetworkError("");
    setLoading(true);

    const optimisticUserMessage = {
      role: "user",
      content: trimmed,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, optimisticUserMessage]);
    setInput("");

    try {
      const response = await api.post("/chat/message", {
        chat_id: chatId,
        content: trimmed,
      });

      const { user_message, assistant_message, title } = response.data;

      setMessages((prev) => {
        const withoutOptimistic = prev.slice(0, -1);
        return [...withoutOptimistic, user_message, assistant_message];
      });

      if (title && onTitleUpdate) {
        onTitleUpdate(title);
      }
    } catch (err) {
      setMessages((prev) => prev.slice(0, -1));
      setInput(trimmed);

      if (!err.response) {
        setNetworkError("Network error. Please check your connection and try again.");
      } else {
        const detail = err.response?.data?.detail;
        setNetworkError(
          typeof detail === "string"
            ? detail
            : "Failed to send message. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto scrollbar-thin px-4 py-6 sm:px-6">
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <p className="text-lg font-medium text-gray-700">Start a conversation</p>
              <p className="mt-1 text-sm text-gray-400">
                Send a message to begin chatting with the AI assistant.
              </p>
            </div>
          </div>
        ) : (
          <div className="mx-auto max-w-3xl space-y-4">
            {messages.map((message, index) => (
              <MessageBubble
                key={`${message.created_at}-${index}`}
                message={message}
              />
            ))}
            {loading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="border-t border-gray-200 bg-white px-4 py-4 sm:px-6">
        <form onSubmit={handleSend} className="mx-auto max-w-3xl">
          {networkError && (
            <p className="mb-2 text-sm text-red-500">{networkError}</p>
          )}
          {inputError && (
            <p className="mb-2 text-sm text-red-500">{inputError}</p>
          )}
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                if (inputError) setInputError("");
              }}
              placeholder="Type your message..."
              disabled={loading}
              className="flex-1 rounded-xl border border-gray-300 px-4 py-3 text-sm outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-200 disabled:bg-gray-50 disabled:text-gray-400"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="rounded-xl bg-primary-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
