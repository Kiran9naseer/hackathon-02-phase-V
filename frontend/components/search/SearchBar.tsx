"use client";

import { useState, useEffect } from "react";
import { Search, Loader2, X } from "lucide-react";

interface SearchBarProps {
    onSearch: (query: str) => void;
    isLoading?: boolean;
    initialQuery?: string;
    placeholder?: string;
}

export function SearchBar({
    onSearch,
    isLoading,
    initialQuery = "",
    placeholder = "Scan database..."
}: SearchBarProps) {
    const [query, setQuery] = useState(initialQuery);

    useEffect(() => {
        const timer = setTimeout(() => {
            onSearch(query);
        }, 300);
        return () => clearTimeout(timer);
    }, [query, onSearch]);

    return (
        <div className="relative group w-full">
            <div className="absolute inset-y-0 left-6 flex items-center pointer-events-none">
                <Search className="w-5 h-5 text-primary-500/40 group-focus-within:text-primary-500 transition-colors" />
            </div>
            <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={placeholder}
                className="w-full bg-primary-500/5 border border-primary-500/10 rounded-2xl py-6 pl-14 pr-12 text-xl font-bold text-white placeholder-primary-50/10 focus:outline-none focus:border-primary-500/30 transition-all shadow-mist"
            />

            <div className="absolute inset-y-0 right-4 flex items-center space-x-2">
                {query && (
                    <button
                        onClick={() => setQuery("")}
                        className="p-2 hover:bg-white/5 rounded-full text-primary-50/20 hover:text-white transition-all"
                    >
                        <X className="w-4 h-4" />
                    </button>
                )}
                {isLoading && (
                    <Loader2 className="w-5 h-5 text-primary-500 animate-spin" />
                )}
            </div>
        </div>
    );
}
