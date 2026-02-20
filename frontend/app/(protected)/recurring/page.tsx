"use client";

import { useEffect, useState, useCallback } from "react";
import { RecurringSeriesCard } from "@/components/recurring/RecurringSeriesCard";
import { Repeat } from "lucide-react";
import apiClient from "@/lib/api/client";
import { Button } from "@/components/ui/Button";
import type { RecurringTaskSeries } from "@/types/task";

export default function RecurringPage() {
    const [series, setSeries] = useState<RecurringTaskSeries[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchSeries = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await apiClient.get<RecurringTaskSeries[]>("/api/v1/recurring/");
            setSeries(response.data);
        } catch (err) {
            setError("Failed to fetch recurring series protocol.");
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchSeries();
    }, [fetchSeries]);

    const handleTogglePause = async (id: string, currentlyPaused: boolean) => {
        const action = currentlyPaused ? "resume" : "pause";
        try {
            await apiClient.post(`/api/v1/recurring/${id}/${action}`);
            setSeries(prev => prev.map(s => s.id === id ? { ...s, paused: !currentlyPaused } : s));
        } catch (err) {
            console.error(`Failed to ${action} series:`, err);
        }
    };

    const handleDeleteSeries = async (id: string) => {
        if (!confirm("Deactivate recurring series? Future instances will be terminated.")) return;
        try {
            await apiClient.delete(`/api/v1/recurring/${id}?delete_future_instances=true`);
            setSeries(prev => prev.filter(s => s.id !== id));
        } catch (err) {
            console.error("Failed to delete series:", err);
        }
    };

    return (
        <div className="min-h-screen bg-surface-dark p-6 md:p-12">
            <div className="max-w-6xl mx-auto">
                <div className="mb-16">
                    <div className="flex items-center space-x-4 mb-4">
                        <div className="w-12 h-0.5 bg-primary-500 shadow-mist"></div>
                        <span className="text-[10px] font-black uppercase tracking-[0.4em] text-primary-500 italic">Automated Dispatch Core</span>
                    </div>
                    <h1 className="text-6xl font-black text-white tracking-tighter italic uppercase leading-none">
                        Recurring.<br />Protocols.
                    </h1>
                </div>

                {isLoading ? (
                    <div className="flex justify-center py-24">
                        <div className="w-10 h-10 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
                    </div>
                ) : series.length === 0 ? (
                    <div className="glass-card py-24 text-center border-dashed border-primary-500/20">
                        <div className="w-20 h-20 bg-primary-500/5 rounded-full flex items-center justify-center mx-auto mb-6">
                            <Repeat className="w-10 h-10 text-primary-500/20" />
                        </div>
                        <h3 className="text-2xl font-black text-white italic uppercase tracking-tighter mb-2">No active loops detected.</h3>
                        <p className="text-primary-50/30 text-sm font-medium">Create a recurring task in the Command Center to populate this matrix.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {series.map((s) => (
                            <RecurringSeriesCard
                                key={s.id}
                                series={s}
                                onTogglePause={handleTogglePause}
                                onDelete={handleDeleteSeries}
                            />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
