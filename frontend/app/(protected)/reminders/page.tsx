"use client";

import { useEffect, useState, useCallback } from "react";
import { Bell, ShieldAlert, ArrowLeft } from "lucide-react";
import Link from "next/link";
import apiClient from "@/lib/api/client";
import { ReminderList, type Reminder } from "@/components/reminders/ReminderList";

export default function RemindersPage() {
    const [reminders, setReminders] = useState<Reminder[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchReminders = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await apiClient.get<{ items: Reminder[] }>("/api/v1/reminders/");
            setReminders(response.data.items);
        } catch (err) {
            setError("Failed to interface with dispatch registry.");
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchReminders();
    }, [fetchReminders]);

    const handleAcknowledge = async (id: string) => {
        try {
            await apiClient.post(`/api/v1/reminders/${id}/acknowledge`);
            setReminders(prev => prev.map(r => r.id === id ? { ...r, status: "acknowledged" as const } : r));
        } catch (err) {
            console.error("Failed to acknowledge dispatch:", err);
        }
    };

    return (
        <div className="min-h-screen bg-surface-dark p-6 md:p-12">
            <div className="max-w-4xl mx-auto">
                <div className="mb-12">
                    <Link
                        href="/dashboard"
                        className="inline-flex items-center text-[10px] font-black uppercase tracking-widest text-primary-100/40 hover:text-primary-500 transition-all italic mb-8 group"
                    >
                        <ArrowLeft className="w-3 h-3 mr-2 group-hover:-translate-x-1 transition-transform" />
                        Back to Matrix
                    </Link>

                    <div className="flex items-center space-x-4 mb-4">
                        <div className="w-12 h-0.5 bg-primary-500 shadow-mist"></div>
                        <span className="text-[10px] font-black uppercase tracking-[0.4em] text-primary-500 italic">Dispatch Notification Core</span>
                    </div>
                    <h1 className="text-6xl font-black text-white tracking-tighter italic uppercase leading-none mb-4">
                        Alert.<br />Protocols.
                    </h1>
                    <p className="text-primary-100/30 text-xs font-medium italic">Pending reminders and overdue synchronizations.</p>
                </div>

                {error && (
                    <div className="p-6 bg-red-500/5 border border-red-500/20 rounded-2xl flex items-center space-x-4 text-red-500 mb-8 italic animate-pulse">
                        <ShieldAlert className="w-6 h-6" />
                        <span className="text-xs font-black uppercase tracking-widest leading-none">!! Error: {error}</span>
                    </div>
                )}

                <div className="space-y-12">
                    <section>
                        <div className="flex items-center justify-between mb-8">
                            <h3 className="text-sm font-black text-white uppercase italic tracking-widest flex items-center">
                                <Bell className="w-4 h-4 mr-2 text-primary-500" />
                                Active Alerts
                            </h3>
                            <span className="px-3 py-1 bg-primary-500/10 rounded-full text-[10px] font-black text-primary-500 italic">
                                {reminders.filter(r => r.status !== 'acknowledged').length} PENDING
                            </span>
                        </div>

                        <ReminderList
                            reminders={reminders}
                            onAcknowledge={handleAcknowledge}
                            isLoading={isLoading}
                        />
                    </section>
                </div>
            </div>
        </div>
    );
}
