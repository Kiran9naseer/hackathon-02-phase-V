"use client";

import { Search, Sparkles } from "lucide-react";

interface SearchEmptyStateProps {
    query: string;
}

export function SearchEmptyState({ query }: SearchEmptyStateProps) {
    return (
        <div className="glass-card py-24 text-center border-dashed border-primary-500/20 animate-in fade-in zoom-in duration-700">
            <div className="w-24 h-24 bg-primary-500/5 rounded-full flex items-center justify-center mx-auto mb-8 relative">
                <Search className="w-10 h-10 text-primary-500/20" />
                <div className="absolute -top-2 -right-2">
                    <Sparkles className="w-6 h-6 text-primary-500/40 animate-pulse" />
                </div>
            </div>

            <h3 className="text-3xl font-black text-white italic uppercase tracking-tighter mb-4">
                Zero Signals Found.
            </h3>

            <p className="text-primary-50/30 text-lg font-medium max-w-md mx-auto leading-relaxed">
                {query ? (
                    <>The encryption <span className="text-primary-400 font-bold">&quot;{query}&quot;</span> yielded no matching nodes in the centralized task matrix.</>
                ) : (
                    "Initiate a scan across the neural network to track specific task signals."
                )}
            </p>

            <div className="mt-12 flex flex-col items-center justify-center space-y-4">
                <span className="text-[10px] font-black uppercase tracking-[0.3em] text-primary-50/10 italic">Suggested Protocols</span>
                <div className="flex flex-wrap justify-center gap-3">
                    {["Review Filters", "Check Syntax", "Expand Range"].map((tip) => (
                        <div key={tip} className="px-4 py-2 bg-primary-500/5 border border-primary-500/10 rounded-full text-[10px] font-black text-primary-500 uppercase italic tracking-widest">
                            {tip}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
