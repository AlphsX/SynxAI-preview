"use client";

import { useState, useEffect } from "react";

export type ChatStyle = "default" | "chatgpt";

export const useChatStyle = () => {
  const [chatStyle, setChatStyle] = useState<ChatStyle>("default");

  // Load saved preference
  useEffect(() => {
    const saved = localStorage.getItem("chatStyle") as ChatStyle;
    if (saved) {
      setChatStyle(saved);
    }
  }, []);

  // Save preference
  const setStyle = (style: ChatStyle) => {
    setChatStyle(style);
    localStorage.setItem("chatStyle", style);
  };

  return {
    chatStyle,
    setChatStyle: setStyle,
    isChatGPTStyle: chatStyle === "chatgpt",
    isDefaultStyle: chatStyle === "default",
  };
};
