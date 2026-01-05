'use client';

import React from 'react';
import { ChatGPTStyleMessage } from '@/components/chat/ChatGPTStyleMessage';
import { MessageRenderer } from '@/components/chat/MessageRenderer';

const exampleMessage = `Absolutely 😎 — here's a clean, **expert-level async Rust example** demonstrating async/await, concurrency with \`tokio\`, error handling, and structured design.

🦀 **Example: Concurrent API Fetcher with Async Rust**

\`\`\`rust
use reqwest::Client;
use tokio::task;
use anyhow::{Result, anyhow};

#[tokio::main]
async fn main() -> Result<()> {
    let client = Client::new();
    let urls = vec![
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
    ];
    
    let tasks: Vec<_> = urls
        .into_iter()
        .map(|url| {
            let client = client.clone();
            task::spawn(async move {
                fetch_url(&client, url).await
            })
        })
        .collect();
    
    Ok(())
}
\`\`\`

This example shows **async/await**, **concurrency**, and **error handling** in Rust! 🚀`;

export default function CompareStyles() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-900 dark:text-white">
          Chat Style Comparison
        </h1>

        <div className="grid md:grid-cols-2 gap-8">
          {/* ChatGPT Style */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">ChatGPT Style</h2>
            <div className="bg-[#1a1a1a] rounded-lg p-6 min-h-[600px]">
              <div className="space-y-6">
                <ChatGPTStyleMessage role="user" content="Gimme Async Rust Code example" />
                <ChatGPTStyleMessage role="assistant" content={exampleMessage} />
              </div>
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              <strong>Features:</strong>
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>Dark gray user bubble (#3f3f46)</li>
                <li>Clean code blocks with copy button</li>
                <li>VS Code Dark+ syntax highlighting</li>
                <li>Inline code styling</li>
                <li>Bold text emphasis</li>
              </ul>
            </div>
          </div>

          {/* Default Style */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Default Style</h2>
            <div className="bg-white dark:bg-gray-800 rounded-lg p-6 min-h-[600px]">
              <div className="space-y-6">
                <div className="flex justify-end">
                  <div className="bg-blue-600 text-white rounded-2xl px-4 py-2 max-w-[70%]">
                    Gimme Async Rust Code example
                  </div>
                </div>
                <div className="flex justify-start">
                  <div className="bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-2xl px-4 py-2 max-w-[85%]">
                    <MessageRenderer content={exampleMessage} />
                  </div>
                </div>
              </div>
            </div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              <strong>Features:</strong>
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>Colorful user bubble (blue)</li>
                <li>Markdown rendering</li>
                <li>Flexible theming</li>
                <li>Enhanced typography</li>
                <li>Table support</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Color Palette Reference */}
        <div className="mt-12 bg-white dark:bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            ChatGPT Color Palette
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="h-20 bg-[#1a1a1a] rounded-lg mb-2"></div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Background
                <br />
                #1a1a1a
              </p>
            </div>
            <div>
              <div className="h-20 bg-[#3f3f46] rounded-lg mb-2"></div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                User Bubble
                <br />
                #3f3f46
              </p>
            </div>
            <div>
              <div className="h-20 bg-[#2f2f2f] rounded-lg mb-2"></div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Input Area
                <br />
                #2f2f2f
              </p>
            </div>
            <div>
              <div className="h-20 bg-[#1e1e1e] rounded-lg mb-2"></div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Code Block
                <br />
                #1e1e1e
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
