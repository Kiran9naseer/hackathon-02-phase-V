"use client";

import { useState, useCallback } from "react";
import { SearchBar } from "@/components/search/SearchBar";
import { SearchFilters } from "@/components/search/SearchFilters";
import { SearchResults } from "@/components/search/SearchResults";
import apiClient from "@/lib/api/client";
import type { Task } from "@/types/task";

export default function SearchPage() {
    const [query, setQuery] = useState("");
    const [filters, setFilters] = useState<any>({});
    const [results, setResults] = useState<Task[]>([]);
    const [loading, setLoading] = useState(false);
    const [total, setTotal] = useState(0);

    const performSearch = useCallback(async (searchQuery: string, currentFilters: any) => {
        setLoading(true);
        try {
            const response = await apiClient.post("/api/v1/search/", {
                query: searchQuery,
                ...currentFilters,
                limit: 50,
                offset: 0
            });
            setResults(response.data.items);
            setTotal(response.data.total);
        } catch (error) {
            console.error("Search failed:", error);
        } finally {
            setLoading(false);
        }
    }, []);

    const handleSearch = (newQuery: string) => {
        setQuery(newQuery);
        performSearch(newQuery, filters);
    };

    const handleFilterChange = (newFilters: any) => {
        setFilters(newFilters);
        performSearch(query, newFilters);
    };

    const handleToggleComplete = async (id: string) => {
        try {
            await apiClient.post(`/api/v1/tasks/${id}/complete`);
            // Update local state for immediate feedback
            setResults(prev => prev.map(t => t.id === id ? { ...t, status: 'completed' as any } : t));
        } catch (err) {
            console.error("Failed to complete task:", err);
        }
    };

    const handleDeleteTask = async (id: string) => {
        if (!confirm("Confirm deletion of task node?")) return;
        try {
            await apiClient.delete(`/api/v1/tasks/${id}`);
            setResults(prev => prev.filter(t => t.id !== id));
            setTotal(prev => prev - 1);
        } catch (err) {
            console.error("Failed to delete task:", err);
        }
    };

    return (
        <div className="min-h-screen bg-surface-dark p-6 md:p-12">
            <div className="max-w-7xl mx-auto">
                {/* Header Section */}
                <div className="mb-16">
                    <div className="flex items-center space-x-4 mb-4">
                        <div className="w-12 h-0.5 bg-primary-500 shadow-mist"></div>
                        <span className="text-[10px] font-black uppercase tracking-[0.4em] text-primary-500 italic">Advanced Neural Search</span>
                    </div>
                    <h1 className="text-6xl md:text-8xl font-black text-white tracking-tighter italic uppercase leading-none mb-12">
                        Intelligence.<br />Matrix.
                    </h1>

                    <SearchBar
                        onSearch={handleSearch}
                        isLoading={loading}
                        placeholder="Interrogate the task database..."
                    />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-16">
                    {/* Controls Sidebar */}
                    <div className="lg:col-span-3">
                        <div className="sticky top-12">
                            <div className="glass-card p-10 relative overflow-hidden">
                                <div className="absolute top-0 right-0 w-32 h-32 bg-primary-500/5 rounded-full blur-3xl -z-10"></div>

                                <h3 className="text-[10px] font-black uppercase tracking-[0.3em] text-primary-50/20 italic mb-10 pb-4 border-b border-primary-500/10">
                                    Filter Protocols
                                </h3>

                                <SearchFilters onFilterChange={handleFilterChange} initialFilters={filters} />

                                <div className="mt-12 pt-8 border-t border-primary-500/10">
                                    <button
                                        onClick={() => {
                                            setFilters({});
                                            setQuery("");
                                            performSearch("", {});
                                        }}
                                        className="w-full py-4 text-[10px] font-black uppercase tracking-widest text-primary-50/20 hover:text-white transition-colors italic bg-primary-500/5 rounded-xl border border-primary-500/10 hover:border-primary-500/30"
                                    >
                                        Reset All Nodes
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Results Main Area */}
                    <div className="lg:col-span-9">
                        <SearchResults
                            tasks={results}
                            total={total}
                            query={query}
                            isLoading={loading}
                            onToggleComplete={handleToggleComplete}
                            onDelete={handleDeleteTask}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
