"use client";

import React, { useState } from "react";
import { Copy, Check, ChevronDown } from "lucide-react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

interface ChatGPTStyleMessageProps {
  content: string;
  role: "user" | "assistant";
  isStreaming?: boolean;
  selectedTool?: string;
}

export const ChatGPTStyleMessage: React.FC<ChatGPTStyleMessageProps> = ({
  content,
  role,
  isStreaming = false,
}) => {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const handleCopyCode = async (code: string, id: string) => {
    await navigator.clipboard.writeText(code);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  // Parse content for code blocks
  const renderContent = () => {
    if (role === "user") {
      return (
        <div className="chatgpt-user-message chatgpt-message-animate">
          {content}
        </div>
      );
    }

    // Split content by code blocks
    const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
    const parts: React.ReactNode[] = [];
    let lastIndex = 0;
    let match;
    let blockIndex = 0;

    while ((match = codeBlockRegex.exec(content)) !== null) {
      // Add text before code block
      if (match.index > lastIndex) {
        const textContent = content.substring(lastIndex, match.index);
        parts.push(
          <div
            key={`text-${blockIndex}`}
            className="chatgpt-ai-response"
            dangerouslySetInnerHTML={{
              __html: formatText(textContent),
            }}
          />,
        );
      }

      // Add code block
      const language = match[1] || "text";
      const code = match[2].trim();
      const codeId = `code-${blockIndex}`;

      parts.push(
        <div key={codeId} className="chatgpt-code-block">
          <div className="chatgpt-code-header">
            <span className="chatgpt-code-language">{language}</span>
            <button
              className="chatgpt-copy-button"
              onClick={() => handleCopyCode(code, codeId)}
            >
              {copiedCode === codeId ? (
                <>
                  <Check size={14} />
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <Copy size={14} />
                  <span>Copy code</span>
                </>
              )}
            </button>
          </div>
          <div className="chatgpt-code-content">
            <SyntaxHighlighter
              language={language}
              style={vscDarkPlus}
              customStyle={{
                margin: 0,
                padding: 0,
                background: "transparent",
                fontSize: "0.875rem",
              }}
              codeTagProps={{
                style: {
                  fontFamily:
                    "'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace",
                },
              }}
            >
              {code}
            </SyntaxHighlighter>
          </div>
        </div>,
      );

      lastIndex = match.index + match[0].length;
      blockIndex++;
    }

    // Add remaining text
    if (lastIndex < content.length) {
      const textContent = content.substring(lastIndex);
      parts.push(
        <div
          key={`text-${blockIndex}`}
          className="chatgpt-ai-response"
          dangerouslySetInnerHTML={{
            __html: formatText(textContent),
          }}
        />,
      );
    }

    return (
      <div className="chatgpt-message-animate">
        {parts}
        {isStreaming && <span className="chatgpt-streaming-cursor" />}
      </div>
    );
  };

  // Format text with inline code, bold, etc.
  const formatText = (text: string): string => {
    // Handle inline code
    text = text.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Handle bold text
    text = text.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");

    // Handle line breaks
    text = text.replace(/\n/g, "<br />");

    return text;
  };

  return <div className="w-full">{renderContent()}</div>;
};
