'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import {
  Plus,
  Globe,
  TrendingUp,
  Sparkles,
  AlertCircle,
  Loader2,
  Search,
  Newspaper,
} from 'lucide-react';
import { chatAPI } from '@/lib/api';
import { useMediaQuery } from '@/hooks';

type SearchTool = {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
  hoverBgColor: string;
  available: boolean;
  providers?: string[];
  primary_provider?: string;
};

type Props = {
  onToolSelect: (toolId: string) => void;
  selectedTool: string | null;
  isDarkMode: boolean;
  className?: string;
  onDropdownStateChange?: (isOpen: boolean) => void;
  externalOpen?: boolean; // Allow external control
  showButton?: boolean; // Option to hide the plus button
  onFileUpload?: (files: FileList) => void; // Callback when files are uploaded
};

const getIconForTool = (toolId: string) => {
  switch (toolId) {
    case 'web_search':
      return <Globe className="h-5 w-5" />;
    case 'news_search':
      return <Newspaper className="h-5 w-5" />;
    case 'crypto_data':
      return <TrendingUp className="h-5 w-5" />;
    case 'vector_search':
      return <Search className="h-5 w-5" />;
    default:
      return <Sparkles className="h-5 w-5" />;
  }
};

const getColorForTool = (toolId: string) => {
  switch (toolId) {
    case 'web_search':
      return {
        color: 'text-blue-500',
        bgColor: 'bg-blue-500/10',
        hoverBgColor: 'hover:bg-blue-500/10',
      };
    case 'news_search':
      return {
        color: 'text-orange-500',
        bgColor: 'bg-orange-500/10',
        hoverBgColor: 'hover:bg-orange-500/10',
      };
    case 'crypto_data':
      return {
        color: 'text-green-500',
        bgColor: 'bg-green-500/10',
        hoverBgColor: 'hover:bg-green-500/10',
      };
    case 'vector_search':
      return {
        color: 'text-purple-500',
        bgColor: 'bg-purple-500/10',
        hoverBgColor: 'hover:bg-purple-500/10',
      };
    default:
      return {
        color: 'text-gray-500',
        bgColor: 'bg-gray-500/10',
        hoverBgColor: 'hover:bg-gray-500/10',
      };
  }
};

export const SearchToolsDropdown = ({
  onToolSelect,
  selectedTool,
  isDarkMode,
  className = '',
  onDropdownStateChange,
  externalOpen,
  showButton = true,
  onFileUpload,
}: Props) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);
  const [shouldRender, setShouldRender] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1);
  const [searchTools, setSearchTools] = useState<SearchTool[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const plusButtonRef = useRef<HTMLButtonElement>(null);
  const backdropRef = useRef<HTMLDivElement>(null);
  const isMobile = useMediaQuery('(max-width: 768px)');

  // Fetch search tools from enhanced backend
  useEffect(() => {
    const fetchSearchTools = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await chatAPI.getSearchTools();
        const fetchedTools = response.tools || [];

        // Transform backend tools to frontend format
        const transformedTools: SearchTool[] = fetchedTools.map(
          (tool: {
            id: string;
            name: string;
            description: string;
            available: boolean;
            providers?: string[];
            primary_provider?: string;
          }) => {
            const colors = getColorForTool(tool.id);
            return {
              id: tool.id,
              name: tool.name,
              description: tool.description,
              icon: getIconForTool(tool.id),
              available: tool.available,
              providers: tool.providers,
              primary_provider: tool.primary_provider,
              ...colors,
            };
          }
        );

        setSearchTools(transformedTools);
      } catch (err) {
        console.error('Failed to fetch search tools:', err);
        setError('Failed to load search tools');

        // Fallback to default tools if API fails - enhanced with news search
        setSearchTools([
          {
            id: 'web_search',
            name: 'Web Search',
            description: 'Search the web for current information',
            icon: <Globe className="h-5 w-5" />,
            color: 'text-blue-500',
            bgColor: 'bg-blue-500/10',
            hoverBgColor: 'hover:bg-blue-500/10',
            available: true,
            providers: ['SerpAPI', 'Brave Search'],
            primary_provider: 'SerpAPI',
          },
          {
            id: 'news_search',
            name: 'News Search',
            description: 'Search for latest news and current events',
            icon: <Newspaper className="h-5 w-5" />,
            color: 'text-orange-500',
            bgColor: 'bg-orange-500/10',
            hoverBgColor: 'hover:bg-orange-500/10',
            available: true,
            providers: ['SerpAPI', 'Brave Search'],
            primary_provider: 'SerpAPI',
          },
          {
            id: 'crypto_data',
            name: 'Crypto Data',
            description: 'Get real-time cryptocurrency market data',
            icon: <TrendingUp className="h-5 w-5" />,
            color: 'text-green-500',
            bgColor: 'bg-green-500/10',
            hoverBgColor: 'hover:bg-green-500/10',
            available: true,
            providers: ['Binance'],
            primary_provider: 'Binance',
          },
          {
            id: 'vector_search',
            name: 'Knowledge Search',
            description: 'Search domain-specific knowledge base',
            icon: <Search className="h-5 w-5" />,
            color: 'text-purple-500',
            bgColor: 'bg-purple-500/10',
            hoverBgColor: 'hover:bg-purple-500/10',
            available: true,
            providers: ['Vector Database'],
            primary_provider: 'PostgreSQL + pgvector',
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSearchTools();
  }, []);

  // Smooth open/close animation management
  const openDropdown = useCallback(() => {
    setShouldRender(true);
    setIsAnimating(true);
    // Small delay to ensure DOM is ready
    requestAnimationFrame(() => {
      setIsOpen(true);
    });
  }, []);

  const closeDropdown = useCallback(() => {
    setIsOpen(false);
    setIsAnimating(true);
    setHighlightedIndex(-1);
    // Wait for animation to complete before removing from DOM
    setTimeout(() => {
      setShouldRender(false);
      setIsAnimating(false);
    }, 300); // Match animation duration
  }, []);

  // Sync with external control - CRITICAL: This must trigger immediately
  useEffect(() => {
    if (externalOpen !== undefined) {
      if (externalOpen && !isOpen) {
        // Force immediate render
        setShouldRender(true);
        setIsAnimating(true);
        // Use setTimeout with 0 to ensure state is set before animation
        setTimeout(() => {
          setIsOpen(true);
        }, 0);
      } else if (!externalOpen && isOpen) {
        setIsOpen(false);
        setIsAnimating(true);
        setHighlightedIndex(-1);
        setTimeout(() => {
          setShouldRender(false);
          setIsAnimating(false);
        }, 300);
      }
    }
  }, [externalOpen, isOpen]);

  // Handle tool selection
  const handleToolSelect = useCallback(
    (toolId: string) => {
      onToolSelect(toolId);
      closeDropdown();
    },
    [onToolSelect, closeDropdown]
  );

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        plusButtonRef.current &&
        !plusButtonRef.current.contains(event.target as Node)
      ) {
        closeDropdown();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [closeDropdown]);

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Only handle keyboard events if the dropdown is open
      if (e.key === 'ArrowUp') {
        e.preventDefault();
        e.stopPropagation();
        setHighlightedIndex(prev => {
          // If nothing is highlighted, start from the last item
          if (prev === -1) return searchTools.length - 1;
          return prev <= 0 ? searchTools.length - 1 : prev - 1;
        });
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        e.stopPropagation();
        setHighlightedIndex(prev => {
          // If nothing is highlighted, start from the first item
          if (prev === -1) return 0;
          return prev >= searchTools.length - 1 ? 0 : prev + 1;
        });
      } else if (
        e.key === 'Enter' &&
        highlightedIndex >= 0 &&
        searchTools[highlightedIndex]?.available
      ) {
        e.preventDefault();
        e.stopPropagation();
        handleToolSelect(searchTools[highlightedIndex].id);
      } else if (e.key === 'Escape') {
        e.preventDefault();
        e.stopPropagation();
        closeDropdown();
      }
    };

    // Use capture phase to ensure we handle events before other components
    window.addEventListener('keydown', handleKeyDown, true);
    return () => window.removeEventListener('keydown', handleKeyDown, true);
  }, [isOpen, highlightedIndex, searchTools, handleToolSelect, closeDropdown]);

  // Focus management - only reset highlight when closed
  useEffect(() => {
    if (!isOpen && !isAnimating) {
      setHighlightedIndex(-1); // Reset highlight when closed
    }
    // Don't auto-highlight first item when opened - let user hover or use keyboard
  }, [isOpen, isAnimating]);

  // Notify parent component about dropdown state changes
  useEffect(() => {
    onDropdownStateChange?.(isOpen || isAnimating);
  }, [isOpen, isAnimating, onDropdownStateChange]);

  // Calculate the button color based on selected tool
  const getButtonColor = () => {
    if (selectedTool === 'web_search') return '#3b82f6';
    if (selectedTool === 'news_search') return '#f97316';
    if (selectedTool === 'crypto_data') return '#10b981';
    if (selectedTool === 'vector_search') return '#8b5cf6';
    return isDarkMode ? '#9ca3af' : '#6b7280';
  };

  return (
    <>
      {/* Backdrop Blur Overlay - Professional smooth transitions */}
      {shouldRender && (
        <div
          ref={backdropRef}
          className={`fixed inset-0 z-[9998] transition-all duration-300 ease-out ${
            isOpen
              ? 'bg-black/20 dark:bg-black/40 backdrop-blur-sm opacity-100'
              : 'bg-black/0 dark:bg-black/0 backdrop-blur-none opacity-0'
          }`}
          style={{
            backdropFilter: isOpen ? 'blur(8px)' : 'blur(0px)',
            WebkitBackdropFilter: isOpen ? 'blur(8px)' : 'blur(0px)',
          }}
          onClick={closeDropdown}
        />
      )}

      <div className={`relative ${className}`}>
        {/* Plus Button */}
        {showButton && (
          <button
            ref={plusButtonRef}
            type="button"
            className={`w-full h-full flex items-center justify-center rounded-full transition-all duration-300 ease-out transform ${
              isOpen || isAnimating ? 'rotate-45 scale-110' : 'rotate-0 scale-100'
            } hover:bg-gray-100 dark:hover:bg-gray-700 hover:scale-105 touch-manipulation relative z-[9999] ${
              isOpen ? 'shadow-lg' : ''
            }`}
            onClick={e => {
              e.preventDefault();
              e.stopPropagation();
              if (isOpen || isAnimating) {
                closeDropdown();
              } else {
                openDropdown();
              }
            }}
            onTouchStart={e => {
              // Prevent iOS Safari from showing touch callout
              e.preventDefault();
            }}
            style={{
              color: getButtonColor(),
              WebkitTapHighlightColor: 'transparent',
            }}
            disabled={isLoading}
            data-plus-button
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : error ? (
              <AlertCircle className="h-5 w-5" />
            ) : (
              <Plus className="h-5 w-5" />
            )}
          </button>
        )}

        {/* Dropdown Menu - ChatGPT style compact design */}
        {shouldRender && (
          <div
            ref={dropdownRef}
            className={`rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-[9999] bg-white dark:bg-gray-800 transition-all duration-200 ease-out ${
              isMobile ? 'fixed w-64' : 'absolute w-56 left-0'
            } ${
              isOpen ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2 pointer-events-none'
            }`}
            style={
              isMobile
                ? {
                    left: '16px',
                    bottom: '100px',
                    transformOrigin: 'bottom left',
                  }
                : {
                    bottom: 'calc(100% + 8px)',
                    transformOrigin: 'bottom left',
                  }
            }
          >
            {error ? (
              <div className="px-4 py-3 text-sm text-red-600 dark:text-red-400 flex items-center">
                <AlertCircle className="h-4 w-4 mr-2" />
                <span>Failed to load search tools</span>
              </div>
            ) : (
              <>
                {/* Add photos & files option */}
                <button
                  type="button"
                  className="w-full text-left px-4 py-3 flex items-center gap-3 group transition-all duration-200 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
                  style={{
                    WebkitTapHighlightColor: 'transparent',
                  }}
                  onClick={e => {
                    e.preventDefault();
                    e.stopPropagation();
                    const fileInput = document.createElement('input');
                    fileInput.type = 'file';
                    fileInput.multiple = true;
                    fileInput.accept = 'image/*,.pdf,.doc,.docx,.txt';
                    fileInput.onchange = event => {
                      const files = (event.target as HTMLInputElement).files;
                      if (files && files.length > 0 && onFileUpload) {
                        onFileUpload(files);
                      }
                    };
                    fileInput.click();
                    closeDropdown();
                  }}
                >
                  <div className="flex-shrink-0 text-gray-600 dark:text-gray-400 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 ease-out">
                    <svg
                      width="18"
                      height="18"
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                      className="stroke-[2] transition-colors duration-100"
                    >
                      <path
                        d="M10 9V15C10 16.1046 10.8954 17 12 17V17C13.1046 17 14 16.1046 14 15V7C14 4.79086 12.2091 3 10 3V3C7.79086 3 6 4.79086 6 7V15C6 18.3137 8.68629 21 12 21V21C15.3137 21 18 18.3137 18 15V8"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                      ></path>
                    </svg>
                  </div>
                  <span className="font-medium text-[15px] group-hover:translate-x-1 transition-transform duration-300 ease-out">
                    Add photos & files
                  </span>
                </button>

                {/* Divider - shorter with margins */}
                <div className="my-1 mx-4 border-t border-gray-200 dark:border-gray-700"></div>

                {/* Search tools */}
                {searchTools.map((tool, index) => (
                  <button
                    key={tool.id}
                    type="button"
                    className={`w-full text-left px-4 py-3 flex items-center gap-3 group transition-all duration-200 ${
                      tool.available
                        ? `text-gray-700 dark:text-gray-200 hover:${tool.bgColor} dark:hover:${tool.bgColor}`
                        : 'text-gray-400 dark:text-gray-500 cursor-not-allowed'
                    } ${highlightedIndex === index ? `${tool.bgColor} dark:${tool.bgColor}` : ''}`}
                    style={{
                      WebkitTapHighlightColor: 'transparent',
                    }}
                    onClick={e => {
                      e.preventDefault();
                      e.stopPropagation();
                      if (tool.available) {
                        handleToolSelect(tool.id);
                      }
                    }}
                    onMouseEnter={() => setHighlightedIndex(index)}
                    onMouseLeave={() => setHighlightedIndex(-1)}
                    disabled={!tool.available}
                  >
                    <div
                      className={`flex-shrink-0 ${tool.available ? tool.color : 'text-gray-400'} group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 ease-out`}
                    >
                      {tool.icon}
                    </div>
                    <span className="font-medium text-[15px] group-hover:translate-x-1 transition-transform duration-300 ease-out">
                      {tool.name}
                    </span>
                  </button>
                ))}
              </>
            )}
          </div>
        )}
      </div>
    </>
  );
};
