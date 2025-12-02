"use client";

import React, { useState, useCallback, useMemo } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  oneDark,
  oneLight,
} from "react-syntax-highlighter/dist/esm/styles/prism";
import { CodeBlockProps } from "@/types/markdown";
import { detectLanguage } from "@/lib/markdown-utils";
import { DEFAULT_MARKDOWN_THEME } from "@/constants/markdown";
import { useSyntaxHighlightingTheme } from "@/hooks/useMarkdownTheme";

// Copy button component
interface CopyButtonProps {
  onCopy: () => void;
  copied: boolean;
  disabled?: boolean;
}

const CopyButton: React.FC<CopyButtonProps> = ({
  onCopy,
  copied,
  disabled = false,
}) => {
  return (
    <button
      onClick={onCopy}
      disabled={disabled}
      className={`
        absolute top-2 right-2 flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all
        ${
          copied
            ? "bg-green-500 text-white"
            : "bg-gray-700 dark:bg-gray-600 text-white hover:bg-gray-600 dark:hover:bg-gray-500"
        }
        ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
      `}
      aria-label={copied ? "Copied to clipboard" : "Copy code to clipboard"}
      title={copied ? "Copied!" : "Copy code"}
    >
      {copied ? (
        <>
          <svg
            className="w-3.5 h-3.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5 13l4 4L19 7"
            />
          </svg>
          <span>Copied!</span>
        </>
      ) : (
        <>
          <svg
            className="w-3.5 h-3.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
          <span>Copy</span>
        </>
      )}
    </button>
  );
};

// Language badge component with enhanced styling
interface LanguageBadgeProps {
  language: string;
}

const LanguageBadge: React.FC<LanguageBadgeProps> = ({ language }) => {
  if (!language || language === "plaintext" || language === "text") {
    return null;
  }

  // Language-specific colors
  const getLanguageColor = (lang: string) => {
    const colors: Record<string, string> = {
      javascript: "bg-yellow-500",
      typescript: "bg-blue-500",
      python: "bg-blue-600",
      java: "bg-red-600",
      cpp: "bg-pink-600",
      c: "bg-gray-600",
      csharp: "bg-purple-600",
      go: "bg-cyan-500",
      rust: "bg-orange-600",
      php: "bg-indigo-500",
      ruby: "bg-red-500",
      swift: "bg-orange-500",
      kotlin: "bg-purple-500",
      html: "bg-orange-500",
      css: "bg-blue-400",
      scss: "bg-pink-500",
      json: "bg-gray-500",
      yaml: "bg-red-400",
      sql: "bg-blue-700",
      bash: "bg-green-600",
      shell: "bg-green-600",
      powershell: "bg-blue-600",
    };
    return colors[lang.toLowerCase()] || "bg-gray-500";
  };

  return (
    <div
      className={`absolute top-2 left-3 px-2.5 py-1 ${getLanguageColor(language)} text-white text-xs font-semibold rounded-md shadow-sm uppercase tracking-wide`}
    >
      {language}
    </div>
  );
};

export const CodeBlock: React.FC<CodeBlockProps> = ({
  children,
  language,
  inline = false,
  showCopyButton = true,
  onCopy,
}) => {
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);

  // Detect language if not provided
  const detectedLanguage = useMemo(() => {
    return language ? detectLanguage(language) : "plaintext";
  }, [language]);

  // Get the code content as string
  const codeContent = useMemo(() => {
    return String(children).replace(/\n$/, "");
  }, [children]);

  // Handle copy to clipboard
  const handleCopy = useCallback(async () => {
    try {
      setCopyError(false);

      // Try using the modern Clipboard API first
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(codeContent);
      } else {
        // Fallback for older browsers or non-secure contexts
        const textArea = document.createElement("textarea");
        textArea.value = codeContent;
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();

        const successful = document.execCommand("copy");
        document.body.removeChild(textArea);

        if (!successful) {
          throw new Error("Copy command failed");
        }
      }

      setCopied(true);

      // Call the onCopy callback if provided
      if (onCopy) {
        onCopy(codeContent);
      }

      // Reset copied state after 2 seconds
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Failed to copy code:", error);
      setCopyError(true);
      setTimeout(() => setCopyError(false), 2000);
    }
  }, [codeContent, onCopy]);

  // Use theme hook for consistent theming
  const { isDarkMode, backgroundColor, textColor, borderColor } =
    useSyntaxHighlightingTheme();
  const syntaxTheme = isDarkMode ? oneDark : oneLight;

  // Render inline code
  if (inline) {
    return (
      <code className={DEFAULT_MARKDOWN_THEME.typography.inlineCode}>
        {children}
      </code>
    );
  }

  // Render block code with syntax highlighting
  return (
    <div className="my-4 relative group">
      {/* Enhanced container with better visual hierarchy */}
      <div className="relative overflow-hidden rounded-xl border-2 border-gray-200 dark:border-gray-700 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 shadow-lg hover:shadow-xl transition-shadow duration-200">
        {/* Header bar for better visual separation */}
        <div className="flex items-center justify-between px-4 py-2 bg-gray-100 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-2">
            {/* Language badge */}
            {detectedLanguage &&
            detectedLanguage !== "plaintext" &&
            detectedLanguage !== "text" ? (
              <span className="px-2.5 py-1 bg-blue-500 dark:bg-blue-600 text-white text-xs font-semibold rounded-md uppercase tracking-wide">
                {detectedLanguage}
              </span>
            ) : (
              <span className="px-2.5 py-1 bg-gray-400 dark:bg-gray-600 text-white text-xs font-semibold rounded-md uppercase tracking-wide">
                Code
              </span>
            )}

            {/* Line count indicator */}
            <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">
              {codeContent.split("\n").length}{" "}
              {codeContent.split("\n").length === 1 ? "line" : "lines"}
            </span>
          </div>

          {/* Copy button in header */}
          {showCopyButton && (
            <button
              onClick={handleCopy}
              disabled={copyError}
              className={`
                flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all
                ${
                  copied
                    ? "bg-green-500 text-white shadow-md"
                    : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600"
                }
                ${copyError ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
              `}
              aria-label={
                copied ? "Copied to clipboard" : "Copy code to clipboard"
              }
              title={copied ? "Copied!" : "Copy code"}
            >
              {copied ? (
                <>
                  <svg
                    className="w-3.5 h-3.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <svg
                    className="w-3.5 h-3.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                    />
                  </svg>
                  <span>Copy</span>
                </>
              )}
            </button>
          )}
        </div>

        {/* Code content with enhanced styling */}
        <div className="relative overflow-x-auto">
          <SyntaxHighlighter
            language={detectedLanguage}
            style={syntaxTheme}
            customStyle={{
              margin: 0,
              padding: "1.25rem",
              background: "transparent",
              fontSize: "0.875rem",
              lineHeight: "1.7",
              borderRadius: 0,
            }}
            codeTagProps={{
              style: {
                fontFamily:
                  'ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace',
                fontSize: "0.875rem",
              },
            }}
            showLineNumbers={codeContent.split("\n").length > 5}
            lineNumberStyle={{
              minWidth: "3em",
              paddingRight: "1em",
              color: "#6b7280",
              userSelect: "none",
            }}
            wrapLines={true}
            wrapLongLines={true}
          >
            {codeContent}
          </SyntaxHighlighter>
        </div>

        {/* Copy error message */}
        {copyError && (
          <div className="absolute bottom-2 right-2 px-3 py-1.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs rounded-md shadow-md animate-fade-in">
            ❌ Copy failed
          </div>
        )}
      </div>
    </div>
  );
};

export default CodeBlock;
