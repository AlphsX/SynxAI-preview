'use client';

import React, { useState } from 'react';
import { ChatGPTStyleMessage } from '@/components/chat/ChatGPTStyleMessage';
import { ChatGPTStyleInput } from '@/components/chat/ChatGPTStyleInput';

export default function TestChatGPTStyle() {
  const [messages, setMessages] = useState([
    {
      role: 'user' as const,
      content: 'Gimme Async Rust Code example',
    },
    {
      role: 'assistant' as const,
      content: `Absolutely 😎 — here's a clean, **expert-level async Rust example** demonstrating async/await, concurrency with \`tokio\`, error handling, and structured design.

🦀 **Example: Concurrent API Fetcher with Async Rust**

\`\`\`rust
use reqwest::Client;
use tokio::task;
use anyhow::{Result, anyhow};
use futures::future::join_all;

#[tokio::main]
async fn main() -> Result<()> {
    // Create a shared async HTTP client
    let client = Client::new();

    // A list of example URLs to fetch concurrently
    let urls = vec![
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
        "https://jsonplaceholder.typicode.com/posts/3",
    ];

    // Spawn concurrent tasks for each URL
    let tasks: Vec<_> = urls
        .into_iter()
        .map(|url| {
            let client = client.clone();
            task::spawn(async move {
                fetch_url(&client, url).await
            })
        })
        .collect();

    // Wait for all tasks to complete
    let results = join_all(tasks).await;

    // Process results
    for (i, result) in results.into_iter().enumerate() {
        match result {
            Ok(Ok(body)) => println!("Response {}: {}", i + 1, body),
            Ok(Err(e)) => eprintln!("Error {}: {}", i + 1, e),
            Err(e) => eprintln!("Task {} panicked: {}", i + 1, e),
        }
    }

    Ok(())
}

async fn fetch_url(client: &Client, url: &str) -> Result<String> {
    let response = client.get(url).send().await?;
    
    if !response.status().is_success() {
        return Err(anyhow!("HTTP error: {}", response.status()));
    }

    let body = response.text().await?;
    Ok(body)
}
\`\`\``,
    },
  ]);
  const [input, setInput] = useState('');

  const handleSubmit = () => {
    if (!input.trim()) return;

    setMessages([...messages, { role: 'user', content: input }]);
    setInput('');

    // Simulate AI response
    setTimeout(() => {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'This is a simulated response. The ChatGPT-style UI is working!',
        },
      ]);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-[#1a1a1a] text-white">
      {/* Messages */}
      <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
        {messages.map((msg, idx) => (
          <ChatGPTStyleMessage key={idx} role={msg.role} content={msg.content} />
        ))}
      </div>

      {/* Input */}
      <div className="fixed bottom-8 left-0 right-0">
        <ChatGPTStyleInput value={input} onChange={setInput} onSubmit={handleSubmit} />
      </div>
    </div>
  );
}
