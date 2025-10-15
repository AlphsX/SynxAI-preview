"use client";

import React, { useState } from 'react';
import { Search, Newspaper, Clock, TrendingUp } from 'lucide-react';

interface NewsAgentPanelProps {
  onSearch?: (query: string) => void;
}

export function NewsAgentPanel({ onSearch }: NewsAgentPanelProps) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/news/agent/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      
      const data = await response.json();
      setResult(data);
      onSearch?.(query);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="Search news..."
          className="flex-1 px-4 py-2 border rounded-lg"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          <Search className="w-5 h-5" />
        </button>
      </div>

      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-sm text-gray-600">Searching news...</p>
        </div>
      )}

      {result && !loading && (
        <div className="space-y-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-5 h-5 text-blue-600" />
              <h3 className="font-semibold">AI Agent Decision</h3>
            </div>
            <p className="text-sm text-gray-700">{result.decision_explanation}</p>
            <div className="mt-2 flex gap-4 text-xs text-gray-600">
              <span>Sources: {result.decision.sources_searched}</span>
              <span>Time: {result.search_time}s</span>
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg border">
            <h3 className="font-semibold mb-2 flex items-center gap-2">
              <Newspaper className="w-5 h-5" />
              News Summary
            </h3>
            <p className="text-gray-700 mb-4">{result.summary.text}</p>
            
            {result.summary.key_points && result.summary.key_points.length > 0 && (
              <div>
                <h4 className="font-medium text-sm mb-2">Key Points:</h4>
                <ul className="space-y-1">
                  {result.summary.key_points.map((point: string, idx: number) => (
                    <li key={idx} className="text-sm text-gray-600 flex gap-2">
                      <span className="text-blue-600">•</span>
                      <span>{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="text-xs text-gray-500">
            Sources: {result.sources_used.join(', ')}
          </div>
        </div>
      )}
    </div>
  );
}
