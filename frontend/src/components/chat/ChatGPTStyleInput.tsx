"use client";

import React, { useRef, useEffect } from "react";
import { Plus, Mic, Send } from "lucide-react";

interface ChatGPTStyleInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  onVoiceClick?: () => void;
  onPlusClick?: () => void;
  isListening?: boolean;
  isLoading?: boolean;
  placeholder?: string;
}

export const ChatGPTStyleInput: React.FC<ChatGPTStyleInputProps> = ({
  value,
  onChange,
  onSubmit,
  onVoiceClick,
  onPlusClick,
  isListening = false,
  isLoading = false,
  placeholder = "Ask anything",
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !isLoading) {
        onSubmit();
      }
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4">
      <div className="chatgpt-input-container">
        {/* Plus button */}
        <button
          className="chatgpt-plus-button"
          onClick={onPlusClick}
          aria-label="Add attachment"
          data-plus-button
        >
          <Plus size={20} />
        </button>

        {/* Text input */}
        <textarea
          ref={textareaRef}
          className="chatgpt-input"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          rows={1}
          disabled={isLoading}
        />

        {/* Voice button */}
        {onVoiceClick && (
          <button
            className={`chatgpt-voice-button ${isListening ? "active" : ""}`}
            onClick={onVoiceClick}
            aria-label="Voice input"
          >
            <Mic size={20} />
          </button>
        )}

        {/* Send button (only show when there's text) */}
        {value.trim() && (
          <button
            className="chatgpt-voice-button"
            onClick={onSubmit}
            disabled={isLoading}
            aria-label="Send message"
          >
            <Send size={20} />
          </button>
        )}
      </div>

      {/* Disclaimer */}
      <div className="chatgpt-disclaimer">
        AI can make mistakes. Check important info.
      </div>
    </div>
  );
};
