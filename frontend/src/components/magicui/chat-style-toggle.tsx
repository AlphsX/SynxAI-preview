"use client";

import React from "react";
import { MessageSquare, Sparkles } from "lucide-react";
import { useChatStyle } from "@/hooks/useChatStyle";

export const ChatStyleToggle: React.FC = () => {
  const { chatStyle, setChatStyle } = useChatStyle();

  return (
    <div className="flex items-center gap-2 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg">
      <button
        onClick={() => setChatStyle("default")}
        className={`
          flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium
          transition-all duration-200
          ${
            chatStyle === "default"
              ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm"
              : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          }
        `}
        aria-label="Default style"
      >
        <Sparkles size={16} />
        <span>Default</span>
      </button>

      <button
        onClick={() => setChatStyle("chatgpt")}
        className={`
          flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium
          transition-all duration-200
          ${
            chatStyle === "chatgpt"
              ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm"
              : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
          }
        `}
        aria-label="ChatGPT style"
      >
        <MessageSquare size={16} />
        <span>ChatGPT</span>
      </button>
    </div>
  );
};
