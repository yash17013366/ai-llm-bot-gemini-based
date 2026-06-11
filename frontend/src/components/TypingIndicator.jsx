export default function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="flex items-center gap-1 rounded-2xl rounded-bl-md border border-gray-200 bg-white px-4 py-3 shadow-sm">
        <span
          className="h-2 w-2 rounded-full bg-gray-400"
          style={{ animation: "bounce-dot 1.4s infinite ease-in-out both", animationDelay: "0s" }}
        />
        <span
          className="h-2 w-2 rounded-full bg-gray-400"
          style={{ animation: "bounce-dot 1.4s infinite ease-in-out both", animationDelay: "0.16s" }}
        />
        <span
          className="h-2 w-2 rounded-full bg-gray-400"
          style={{ animation: "bounce-dot 1.4s infinite ease-in-out both", animationDelay: "0.32s" }}
        />
      </div>
    </div>
  );
}
