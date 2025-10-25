"use client";

import React, { useState, useRef, useEffect } from "react";
import { SimpleMessageRenderer } from "./SimpleMessageRenderer";
import { SearchToolsDropdown } from "../magicui/search-tools-dropdown";

interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
  isStreaming?: boolean;
}

interface SocialChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
}

export const SocialChatInterface: React.FC<SocialChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isLoading = false,
}) => {
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [selectedTool, setSelectedTool] = useState<string | null>(null);
  const [showSearchTools, setShowSearchTools] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Detect dark mode
  useEffect(() => {
    const checkDarkMode = () => {
      setIsDarkMode(document.documentElement.classList.contains("dark"));
    };
    checkDarkMode();
    const observer = new MutationObserver(checkDarkMode);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });
    return () => observer.disconnect();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Check if user has scrolled up
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
      setShowScrollButton(!isNearBottom && messages.length > 0);
    };

    container.addEventListener("scroll", handleScroll);
    return () => container.removeEventListener("scroll", handleScroll);
  }, [messages.length]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
    }
  }, [inputValue]);

  const handleSend = () => {
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue("");
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Don't send message if dropdown is open
    if (e.key === "Enter" && !e.shiftKey && !showSearchTools) {
      e.preventDefault();
      handleSend();
    }

    // Close dropdown on Escape
    if (e.key === "Escape" && showSearchTools) {
      e.preventDefault();
      setShowSearchTools(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setInputValue(value);
    setIsTyping(value.length > 0);

    // Show search tools dropdown ONLY when input is exactly "/"
    if (value === "/") {
      setShowSearchTools(true);
    } else {
      setShowSearchTools(false);
    }
  };

  const handleToolSelect = (toolId: string) => {
    setSelectedTool(toolId);
    setShowSearchTools(false);
    // Replace "/" with the tool command
    setInputValue(`/${toolId} `);
    inputRef.current?.focus();
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-50 via-white to-indigo-50/30 dark:from-gray-900 dark:via-slate-900 dark:to-indigo-950/30 relative">
      {/* Chat Header */}
      <div className="flex-shrink-0 px-6 py-5 bg-white/90 dark:bg-gray-800/90 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50 shadow-sm">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-500 rounded-full flex items-center justify-center shadow-lg ring-2 ring-white/20">
            <span className="text-2xl">🤖</span>
          </div>
          <div>
            <h2 className="text-lg font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-200 bg-clip-text text-transparent">
              AI Assistant
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-300 font-medium">
              {isLoading ? (
                <span className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce"></div>
                    <div
                      className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    ></div>
                    <div
                      className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    ></div>
                  </div>
                  <span>Typing...</span>
                </span>
              ) : (
                "Ready to help you"
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto px-4 py-6 relative"
      >
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            /* Welcome Message */
            <div className="text-center py-16">
              <div className="w-24 h-24 bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl ring-4 ring-white/10 animate-pulse">
                <span className="text-4xl">👋</span>
              </div>
              <h3 className="text-3xl font-bold bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 dark:from-white dark:via-gray-100 dark:to-white bg-clip-text text-transparent mb-4">
                Hello! Welcome
              </h3>
              <p className="text-gray-600 dark:text-gray-300 max-w-lg mx-auto text-lg leading-relaxed">
                I&apos;m ready to help answer your questions and chat with you.
                How can I assist you today? 😊
              </p>
            </div>
          ) : (
            /* Chat Messages */
            <div className="space-y-4">
              {messages.map((message) => (
                <div key={message.id}>
                  {message.role === "assistant" ? (
                    <div className="flex justify-start mb-4">
                      <div className="flex items-end space-x-2 max-w-[85%]">
                        <div className="flex-shrink-0 mb-1">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-500 flex items-center justify-center text-white shadow-lg ring-2 ring-white/20">
                            <span className="text-lg">🤖</span>
                          </div>
                        </div>
                        <div className="bg-white dark:bg-gray-800/90 rounded-2xl rounded-bl-md px-5 py-4 shadow-xl border border-gray-200/50 dark:border-gray-700/50 hover:shadow-2xl transition-all duration-200">
                          <SimpleMessageRenderer
                            content={message.content}
                            isStreaming={message.isStreaming}
                            onCopyCode={(code) => {
                              navigator.clipboard.writeText(code);
                              // Could add toast notification here
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="flex justify-end mb-4">
                      <div className="flex items-end space-x-2 max-w-[70%] flex-row-reverse space-x-reverse">
                        <div className="flex-shrink-0 mb-1">
                          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-500 flex items-center justify-center text-white shadow-lg ring-2 ring-white/20">
                            <span className="text-lg">👨‍💻</span>
                          </div>
                        </div>
                        <div className="bg-white dark:bg-gray-800/90 text-gray-900 dark:text-gray-100 rounded-2xl rounded-br-md px-5 py-4 shadow-xl border border-gray-200/50 dark:border-gray-700/50">
                          <div className="prose prose-sm max-w-none prose-gray dark:prose-invert">
                            <p className="mb-0 leading-relaxed text-gray-800 dark:text-gray-200 font-medium">
                              {message.content}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Scroll to Bottom Button */}
      {showScrollButton && (
        <div className="absolute left-1/2 -translate-x-1/2 z-30 bottom-32">
          <button
            onClick={scrollToBottom}
            className="cursor-pointer rounded-full bg-clip-padding border text-gray-600 dark:text-gray-300 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 w-10 h-10 flex items-center justify-center shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-110"
            aria-label="Scroll to bottom"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 20 20"
              fill="currentColor"
              xmlns="http://www.w3.org/2000/svg"
              className="text-gray-700 dark:text-gray-200"
            >
              <path d="M9.33468 3.33333C9.33468 2.96617 9.6326 2.66847 9.99972 2.66829C10.367 2.66829 10.6648 2.96606 10.6648 3.33333V15.0609L15.363 10.3626L15.4675 10.2777C15.7255 10.1074 16.0762 10.1357 16.3034 10.3626C16.5631 10.6223 16.5631 11.0443 16.3034 11.304L10.4704 17.137C10.2108 17.3967 9.7897 17.3966 9.52999 17.137L3.69601 11.304L3.61105 11.1995C3.44054 10.9414 3.46874 10.5899 3.69601 10.3626C3.92328 10.1354 4.27479 10.1072 4.53292 10.2777L4.63741 10.3626L9.33468 15.0599V3.33333Z"></path>
            </svg>
          </button>
        </div>
      )}

      {/* Input Area */}
      <div className="flex-shrink-0 px-4 py-5 bg-white/90 dark:bg-gray-800/90 backdrop-blur-md border-t border-gray-200/50 dark:border-gray-700/50 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-3">
            {/* Message Input */}
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                placeholder='Type your message here... (Type "/" for search tools)'
                disabled={isLoading}
                className="w-full px-5 py-4 pr-12 bg-gray-50 dark:bg-gray-700/80 border border-gray-200 dark:border-gray-600 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 disabled:opacity-50 disabled:cursor-not-allowed min-h-[52px] max-h-32 shadow-sm hover:shadow-md transition-all duration-200 backdrop-blur-sm"
                rows={1}
              />

              {/* Search Tools Dropdown */}
              <div
                className="absolute bottom-full left-0 mb-2 z-[10000]"
                style={{
                  position: "absolute",
                  bottom: "100%",
                  left: "0",
                  marginBottom: "0.5rem",
                  zIndex: 10000,
                }}
              >
                <SearchToolsDropdown
                  onToolSelect={handleToolSelect}
                  selectedTool={selectedTool}
                  isDarkMode={isDarkMode}
                  externalOpen={showSearchTools}
                  showButton={false}
                  onDropdownStateChange={(isOpen) => {
                    if (!isOpen) {
                      setShowSearchTools(false);
                    }
                  }}
                />
              </div>

              {/* Character count for long messages */}
              {inputValue.length > 100 && (
                <div className="absolute bottom-1 right-12 text-xs text-gray-400">
                  {inputValue.length}
                </div>
              )}
            </div>

            {/* Send Button */}
            <button
              onClick={handleSend}
              disabled={!inputValue.trim() || isLoading}
              className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 hover:from-indigo-600 hover:via-purple-600 hover:to-pink-600 disabled:from-gray-400 disabled:to-gray-500 text-white rounded-full flex items-center justify-center transition-all duration-300 disabled:cursor-not-allowed shadow-xl hover:shadow-2xl disabled:shadow-sm hover:scale-110 disabled:scale-100 ring-2 ring-white/20 hover:ring-white/30"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
              )}
            </button>
          </div>

          {/* Typing indicator */}
          {isTyping && !isLoading && (
            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 flex items-center space-x-1">
              <div className="flex space-x-1">
                <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce"></div>
                <div
                  className="w-1 h-1 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.1s" }}
                ></div>
                <div
                  className="w-1 h-1 bg-gray-400 rounded-full animate-bounce"
                  style={{ animationDelay: "0.2s" }}
                ></div>
              </div>
              <span>Typing...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SocialChatInterface;
