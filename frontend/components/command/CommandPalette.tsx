"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import {
    Search,
    Terminal,
    Plus,
    Tag,
    Folder,
    Settings,
    Layout,
    CheckCircle,
    Command,
    ArrowRight,
    User,
    LogOut,
    Calendar,
    X
} from "lucide-react";
import apiClient from "@/lib/api/client";
import { useSession } from "@/lib/auth/provider";
import type { Task } from "@/types/task";

interface CommandAction {
    id: string;
    title: string;
    subtitle: string;
    icon: React.ReactNode;
    shortcut?: string[];
    action: () => void;
    category: "Navigation" | "Actions" | "Account";
}

export function CommandPalette() {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState("");
    const [results, setResults] = useState<Task[]>([]);
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [isSearching, setIsSearching] = useState(false);
    const router = useRouter();
    const { logout } = useSession();
    const inputRef = useRef<HTMLInputElement>(null);

    const toggle = useCallback(() => {
        setIsOpen(v => !v);
        setQuery("");
        setSelectedIndex(0);
    }, []);

    useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                toggle();
            }
            if (e.key === "Escape") {
                setIsOpen(false);
            }
        };

        document.addEventListener("keydown", down);
        return () => document.removeEventListener("keydown", down);
    }, [toggle]);

    useEffect(() => {
        if (isOpen) {
            setTimeout(() => inputRef.current?.focus(), 50);
        }
    }, [isOpen]);

    const searchTasks = useCallback(async (q: string) => {
        if (!q.trim()) {
            setResults([]);
            return;
        }
        setIsSearching(true);
        try {
            const response = await apiClient.post("/api/v1/search/", { query: q, limit: 5 });
            setResults(response.data.items || []);
        } catch (err) {
            console.error("Command palette search failed:", err);
        } finally {
            setIsSearching(false);
        }
    }, []);

    useEffect(() => {
        const timer = setTimeout(() => {
            searchTasks(query);
        }, 200);
        return () => clearTimeout(timer);
    }, [query, searchTasks]);

    const actions: CommandAction[] = [
        {
            id: "create-task",
            title: "Initialize Vector",
            subtitle: "Queue a new strategic directive",
            icon: <Plus className="w-4 h-4" />,
            shortcut: ["N"],
            action: () => router.push("/tasks/new"),
            category: "Actions"
        },
        {
            id: "go-dashboard",
            title: "Dashboard Stream",
            subtitle: "Monitor neural workspace metrics",
            icon: <Layout className="w-4 h-4" />,
            shortcut: ["G", "D"],
            action: () => router.push("/dashboard"),
            category: "Navigation"
        },
        {
            id: "go-tasks",
            title: "Task Registry",
            subtitle: "Access all active vectors",
            icon: <CheckCircle className="w-4 h-4" />,
            shortcut: ["G", "T"],
            action: () => router.push("/tasks"),
            category: "Navigation"
        },
        {
            id: "go-recurring",
            title: "Recurrence Protocols",
            subtitle: "Manage automated dispatch loops",
            icon: <Calendar className="w-4 h-4" />,
            action: () => router.push("/recurring"),
            category: "Navigation"
        },
        {
            id: "go-tags",
            title: "Tag Taxonomy",
            subtitle: "Filter matrix by classifiers",
            icon: <Tag className="w-4 h-4" />,
            action: () => router.push("/tags"),
            category: "Navigation"
        },
        {
            id: "logout",
            title: "Terminate Session",
            subtitle: "Securely de-authenticate",
            icon: <LogOut className="w-4 h-4" />,
            action: logout,
            category: "Account"
        }
    ];

    const filteredActions = actions.filter(a =>
        a.title.toLowerCase().includes(query.toLowerCase()) ||
        a.category.toLowerCase().includes(query.toLowerCase())
    );

    const totalItems = filteredActions.length + results.length;

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "ArrowDown") {
            e.preventDefault();
            setSelectedIndex(i => (i + 1) % totalItems);
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            setSelectedIndex(i => (i - 1 + totalItems) % totalItems);
        } else if (e.key === "Enter") {
            if (selectedIndex < filteredActions.length) {
                filteredActions[selectedIndex].action();
            } else {
                const taskIndex = selectedIndex - filteredActions.length;
                router.push(`/tasks/${results[taskIndex].id}`);
            }
            setIsOpen(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[200] flex items-start justify-center pt-[15vh] px-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-surface-dark/40 backdrop-blur-xl animate-in fade-in duration-300"
                onClick={() => setIsOpen(false)}
            ></div>

            {/* Palette Container */}
            <div className="relative w-full max-w-2xl bg-surface-card border border-primary-500/10 rounded-[2rem] shadow-mist-glow overflow-hidden animate-in zoom-in-95 slide-in-from-top-10 duration-500">
                <div className="flex items-center px-6 py-6 border-b border-primary-500/10">
                    <Terminal className="w-5 h-5 text-primary-500 mr-4 opacity-50" />
                    <input
                        ref={inputRef}
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Search vectors or execute command..."
                        className="w-full bg-transparent border-none text-white placeholder-primary-100/20 focus:outline-none text-lg font-bold italic"
                    />
                    <div className="flex items-center space-x-2">
                        <kbd className="px-2 py-1 bg-primary-500/10 rounded border border-primary-500/20 text-[8px] font-black text-primary-500 uppercase tracking-widest italic">Esc</kbd>
                    </div>
                </div>

                <div className="max-h-[60vh] overflow-y-auto scrollbar-hide py-4">
                    {/* Actions Section */}
                    {filteredActions.length > 0 && (
                        <div className="px-4 mb-6">
                            <h3 className="px-4 text-[10px] font-black text-primary-100/20 uppercase tracking-[0.2em] mb-3 italic">System Directives</h3>
                            <div className="space-y-1">
                                {filteredActions.map((action, i) => {
                                    const isActive = i === selectedIndex;
                                    return (
                                        <button
                                            key={action.id}
                                            onClick={() => { action.action(); setIsOpen(false); }}
                                            onMouseEnter={() => setSelectedIndex(i)}
                                            className={`w-full flex items-center justify-between p-4 rounded-2xl transition-all ${isActive ? 'bg-primary-500/10 border border-primary-500/20' : 'border border-transparent'
                                                }`}
                                        >
                                            <div className="flex items-center space-x-4">
                                                <div className={`p-2.5 rounded-xl border ${isActive ? 'bg-primary-500 text-white border-primary-500 shadow-mist' : 'bg-primary-500/5 text-primary-500 border-primary-500/10'}`}>
                                                    {action.icon}
                                                </div>
                                                <div className="text-left">
                                                    <p className={`text-sm font-black italic uppercase tracking-tighter ${isActive ? 'text-white' : 'text-primary-50/60'}`}>{action.title}</p>
                                                    <p className="text-[10px] text-primary-50/20 font-medium italic">{action.subtitle}</p>
                                                </div>
                                            </div>
                                            {action.shortcut && (
                                                <div className="flex space-x-1">
                                                    {action.shortcut.map(s => (
                                                        <kbd key={s} className="px-1.5 py-0.5 bg-primary-500/5 rounded border border-primary-500/10 text-[9px] font-black text-primary-100/20">{s}</kbd>
                                                    ))}
                                                </div>
                                            )}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* Search Results Section */}
                    {results.length > 0 && (
                        <div className="px-4">
                            <h3 className="px-4 text-[10px] font-black text-primary-100/20 uppercase tracking-[0.2em] mb-3 italic">Neural Matches</h3>
                            <div className="space-y-1">
                                {results.map((task, i) => {
                                    const globalIndex = filteredActions.length + i;
                                    const isActive = globalIndex === selectedIndex;
                                    return (
                                        <button
                                            key={task.id}
                                            onClick={() => { router.push(`/tasks/${task.id}`); setIsOpen(false); }}
                                            onMouseEnter={() => setSelectedIndex(globalIndex)}
                                            className={`w-full flex items-center justify-between p-4 rounded-2xl transition-all ${isActive ? 'bg-primary-500/10 border border-primary-500/20' : 'border border-transparent'
                                                }`}
                                        >
                                            <div className="flex items-center space-x-4">
                                                <div className={`w-10 h-10 rounded-xl flex items-center justify-center border font-black text-xs ${task.priority === 'high' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                                                        task.priority === 'medium' ? 'bg-orange-500/10 text-orange-500 border-orange-500/20' :
                                                            'bg-primary-500/10 text-primary-500 border-primary-500/20'
                                                    }`}>
                                                    {task.title.charAt(0)}
                                                </div>
                                                <div className="text-left">
                                                    <p className={`text-sm font-black italic uppercase tracking-tighter ${isActive ? 'text-white' : 'text-primary-50/60'}`}>{task.title}</p>
                                                    <p className="text-[10px] text-primary-50/20 font-medium italic">{task.priority} Focus • {task.status}</p>
                                                </div>
                                            </div>
                                            <ArrowRight className={`w-4 h-4 transition-all ${isActive ? 'text-primary-500 opacity-100' : 'opacity-0'}`} />
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {query && filteredActions.length === 0 && results.length === 0 && !isSearching && (
                        <div className="py-20 text-center">
                            <Command className="w-12 h-12 text-primary-500/10 mx-auto mb-4" />
                            <p className="text-primary-50/20 text-xs font-black uppercase tracking-widest italic">No matching vectors found.</p>
                        </div>
                    )}
                </div>

                <div className="px-10 py-4 bg-primary-500/5 border-t border-primary-500/10 flex items-center justify-between">
                    <div className="flex items-center space-x-6">
                        <div className="flex items-center space-x-2">
                            <kbd className="p-1 bg-primary-500/10 rounded border border-primary-500/20"><Search className="w-2.5 h-2.5 text-primary-500/40" /></kbd>
                            <span className="text-[8px] font-black text-primary-100/20 uppercase tracking-[0.1em] italic">Search</span>
                        </div>
                        <div className="flex items-center space-x-2">
                            <kbd className="p-1 bg-primary-500/10 rounded border border-primary-500/20"><Command className="w-2.5 h-2.5 text-primary-500/40" /></kbd>
                            <span className="text-[8px] font-black text-primary-100/20 uppercase tracking-[0.1em] italic">Navigate</span>
                        </div>
                    </div>
                    <p className="text-[8px] font-black text-primary-500/40 uppercase italic tracking-widest animate-pulse">Neural Engine Ready</p>
                </div>
            </div>
        </div>
    );
}
