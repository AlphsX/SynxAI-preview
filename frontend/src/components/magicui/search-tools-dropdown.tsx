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

        {/* Dropdown Menu - Professional smooth animations */}
        {shouldRender && (
          <div
            ref={dropdownRef}
            className={`absolute bottom-full mb-2 rounded-2xl shadow-2xl border border-gray-200/40 dark:border-gray-700/40 py-2 z-[9999] bg-white/95 dark:bg-gray-800/95 backdrop-blur-xl transition-all duration-300 ease-out ${
              isMobile ? 'w-56' : 'w-48'
            } ${
              isOpen ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-4 scale-95'
            }`}
            style={{
              left: '0',
              bottom: 'calc(100% + 0.5rem)',
              transformOrigin: 'bottom left',
            }}
          >
            <div className="px-4 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              {error ? 'Error Loading Tools' : 'Select Tools'}
            </div>
            {error ? (
              <div className="px-4 py-3 text-sm text-red-600 dark:text-red-400 flex items-center">
                <AlertCircle className="h-4 w-4 mr-2" />
                <span>Failed to load search tools</span>
              </div>
            ) : (
              searchTools.map((tool, index) => (
                <button
                  key={tool.id}
                  type="button"
                  className={`w-full text-left group rounded-xl mx-1 touch-manipulation dropdown-item-hover ${
                    isMobile ? 'px-3 py-2.5' : 'px-4 py-3'
                  } ${
                    tool.available
                      ? `text-gray-700 dark:text-gray-300 hover:${tool.bgColor} dark:hover:${tool.bgColor}`
                      : 'text-gray-400 dark:text-gray-600 cursor-not-allowed opacity-60'
                  } ${
                    highlightedIndex === index
                      ? `${tool.bgColor} dark:${tool.bgColor} shadow-md`
                      : ''
                  } ${isOpen ? 'animate-item-slide-in' : ''}`}
                  style={{
                    animationDelay: isOpen ? `${index * 50}ms` : '0ms',
                    minHeight: isMobile ? '48px' : '44px',
                    WebkitTapHighlightColor: 'transparent',
                  }}
                  onClick={e => {
                    e.preventDefault();
                    e.stopPropagation();
                    if (tool.available) {
                      handleToolSelect(tool.id);
                    }
                  }}
                  onMouseEnter={() => {
                    // Update highlight on mouse hover
                    setHighlightedIndex(index);
                  }}
                  onMouseLeave={() => {
                    // Clear highlight when mouse leaves
                    setHighlightedIndex(-1);
                  }}
                  onTouchStart={e => {
                    e.preventDefault();
                  }}
                  disabled={!tool.available}
                >
                  {isMobile ? (
                    // Mobile layout: Icon left, simple name right
                    <div className="flex items-center">
                      <div
                        className={`${
                          tool.available ? tool.color : 'text-gray-400 dark:text-gray-600'
                        } mr-3 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 ease-out flex-shrink-0`}
                      >
                        {tool.icon}
                      </div>
                      <div className="flex-1 min-w-0 flex items-center justify-between">
                        <span className="group-hover:translate-x-2 transition-all duration-300 ease-out font-medium text-sm">
                          {tool.name}
                        </span>
                        {!tool.available && (
                          <span className="text-xs text-red-500 dark:text-red-400 ml-2 flex-shrink-0">
                            Unavailable
                          </span>
                        )}
                      </div>
                    </div>
                  ) : (
                    // Desktop layout: Keep original with descriptions
                    <div className="flex items-start">
                      <div
                        className={`${
                          tool.available ? tool.color : 'text-gray-400 dark:text-gray-600'
                        } mr-3 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300 ease-out flex-shrink-0 mt-0.5`}
                      >
                        {tool.icon}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="group-hover:translate-x-2 transition-all duration-300 ease-out font-medium truncate text-sm">
                            {tool.name}
                          </span>
                          {!tool.available && (
                            <span className="text-xs text-red-500 dark:text-red-400 ml-2 flex-shrink-0">
                              Unavailable
                            </span>
                          )}
                        </div>
                        {tool.description && (
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">
                            {tool.description}
                          </p>
                        )}
                        {tool.primary_provider && (
                          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                            via {tool.primary_provider}
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </button>
              ))
            )}
          </div>
        )}
      </div>
    </>
  );
};
