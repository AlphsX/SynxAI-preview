'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Brain, Trash2, Info } from 'lucide-react';

interface MemoryStats {
  total_messages: number;
  user_messages: number;
  assistant_messages: number;
  storage_type: string;
  langsmith_enabled: boolean;
}

interface MemoryIndicatorProps {
  conversationId: string;
  onClearMemory?: () => void;
}

export default function MemoryIndicator({ conversationId, onClearMemory }: MemoryIndicatorProps) {
  const [stats, setStats] = useState<MemoryStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [memoryEnabled, setMemoryEnabled] = useState(true);

  const fetchMemoryStats = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/memory/stats/${conversationId}`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch memory stats:', error);
    }
  }, [conversationId]);

  const checkMemoryStatus = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/memory/status');
      if (response.ok) {
        const data = await response.json();
        setMemoryEnabled(data.memory_enabled);
      }
    } catch (error) {
      console.error('Failed to check memory status:', error);
    }
  }, []);

  useEffect(() => {
    if (conversationId) {
      fetchMemoryStats();
      checkMemoryStatus();
    }
  }, [conversationId, fetchMemoryStats, checkMemoryStatus]);

  const handleClearMemory = async () => {
    if (!confirm('Are you sure you want to clear the conversation memory?')) {
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`/api/v1/memory/clear/${conversationId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setStats(null);
        if (onClearMemory) {
          onClearMemory();
        }
        alert('Memory cleared successfully!');
      } else {
        alert('Failed to clear memory');
      }
    } catch (error) {
      console.error('Failed to clear memory:', error);
      alert('Error clearing memory');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMemory = async () => {
    setIsLoading(true);
    try {
      const endpoint = memoryEnabled ? '/api/v1/memory/disable' : '/api/v1/memory/enable';
      const response = await fetch(endpoint, { method: 'POST' });

      if (response.ok) {
        setMemoryEnabled(!memoryEnabled);
      }
    } catch (error) {
      console.error('Failed to toggle memory:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!conversationId) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Memory Status Badge */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-3">
        <div className="flex items-center gap-3">
          {/* Memory Icon */}
          <div
            className={`p-2 rounded-full ${
              memoryEnabled ? 'bg-green-100 dark:bg-green-900' : 'bg-gray-100 dark:bg-gray-700'
            }`}
          >
            <Brain
              className={`w-5 h-5 ${
                memoryEnabled ? 'text-green-600 dark:text-green-400' : 'text-gray-400'
              }`}
            />
          </div>

          {/* Stats */}
          {stats && (
            <div className="flex-1">
              <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                Memory Active
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {stats.total_messages} messages
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2">
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title="Show details"
            >
              <Info className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            </button>

            <button
              onClick={handleClearMemory}
              disabled={isLoading}
              className="p-2 hover:bg-red-100 dark:hover:bg-red-900 rounded-lg transition-colors disabled:opacity-50"
              title="Clear memory"
            >
              <Trash2 className="w-4 h-4 text-red-600 dark:text-red-400" />
            </button>
          </div>
        </div>

        {/* Detailed Stats */}
        {showDetails && stats && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-gray-600 dark:text-gray-400">User messages:</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {stats.user_messages}
              </span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-gray-600 dark:text-gray-400">AI messages:</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {stats.assistant_messages}
              </span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-gray-600 dark:text-gray-400">Storage:</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {stats.storage_type}
              </span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-gray-600 dark:text-gray-400">LangSmith:</span>
              <span
                className={`font-medium ${
                  stats.langsmith_enabled ? 'text-green-600 dark:text-green-400' : 'text-gray-400'
                }`}
              >
                {stats.langsmith_enabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>

            {/* Toggle Memory */}
            <button
              onClick={toggleMemory}
              disabled={isLoading}
              className={`w-full mt-2 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                memoryEnabled
                  ? 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 hover:bg-red-200 dark:hover:bg-red-800'
                  : 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 hover:bg-green-200 dark:hover:bg-green-800'
              } disabled:opacity-50`}
            >
              {isLoading ? 'Processing...' : memoryEnabled ? 'Disable Memory' : 'Enable Memory'}
            </button>
          </div>
        )}

        {/* Memory Tips */}
        {showDetails && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
              <p className="font-medium">💡 Try asking:</p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                <li>&quot;What are we talking about?&quot;</li>
                <li>&quot;What did I ask earlier?&quot;</li>
                <li>&quot;Summarize our conversation&quot;</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
