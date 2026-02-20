"use client";

import { Bell, Clock, CheckCircle, AlertTriangle } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import type { Task } from "@/types/task";

export interface Reminder {
    id: string;
    task_id: string;
    task?: Task;
    scheduled_time: string;
    status: "pending" | "sent" | "acknowledged" | "failed";
    delivered_at?: string;
    acknowledged_at?: string;
}

interface ReminderListProps {
    reminders: Reminder[];
    onAcknowledge: (id: string) => void;
    isLoading?: boolean;
}

export function ReminderList({ reminders, onAcknowledge, isLoading }: ReminderListProps) {
    if (isLoading) {
        return (
            <div className="flex justify-center py-12">
                <div className="w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    if (reminders.length === 0) {
        return (
            <div className="glass-card p-12 text-center border-dashed border-primary-500/20">
                <Bell className="w-12 h-12 text-primary-500/10 mx-auto mb-4" />
                <p className="text-primary-100/20 font-black uppercase tracking-widest italic">No pending dispatches detected.</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {reminders.map((reminder) => (
                <div
                    key={reminder.id}
                    className="glass-card p-6 border border-primary-500/10 hover:border-primary-500/30 transition-all flex items-center justify-between group"
                >
                    <div className="flex items-center space-x-6">
                        <div className={`p-4 rounded-2xl border ${reminder.status === 'sent' ? 'bg-orange-500/10 border-orange-500/20 text-orange-500' :
                                reminder.status === 'pending' ? 'bg-primary-500/10 border-primary-500/20 text-primary-500' :
                                    'bg-primary-500/5 border-primary-500/10 text-primary-100/20'
                            }`}>
                            <Bell className="w-5 h-5" />
                        </div>

                        <div>
                            <h4 className="text-sm font-black text-white uppercase italic tracking-tighter mb-1 group-hover:text-primary-400 transition-colors">
                                {reminder.task?.title || "Directive Synchronization"}
                            </h4>
                            <div className="flex items-center space-x-3 text-[10px] font-black uppercase tracking-widest text-primary-100/20">
                                <Clock className="w-3 h-3" />
                                <span>Trigger: {formatDistanceToNow(new Date(reminder.scheduled_time), { addSuffix: true })}</span>
                                <span className="w-1 h-1 bg-primary-500/20 rounded-full" />
                                <span>Status: {reminder.status}</span>
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={() => onAcknowledge(reminder.id)}
                        disabled={reminder.status === 'acknowledged'}
                        className={`px-6 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest italic border transition-all ${reminder.status === 'acknowledged'
                                ? 'opacity-20 cursor-not-allowed border-primary-500/10'
                                : 'bg-primary-500/10 border-primary-500/20 text-primary-500 hover:bg-primary-500 hover:text-white hover:border-primary-500 hover:shadow-mist'
                            }`}
                    >
                        {reminder.status === 'acknowledged' ? 'Terminated' : 'Acknowledge'}
                    </button>
                </div>
            ))}
        </div>
    );
}
