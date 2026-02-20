"use client";

import { Repeat, Pause, Play, Trash2, Calendar, AlertCircle } from "lucide-react";
import type { RecurringTaskSeries } from "@/types/task";

interface RecurringSeriesCardProps {
    series: RecurringTaskSeries;
    onTogglePause: (id: string, paused: boolean) => void;
    onDelete: (id: string) => void;
}

export function RecurringSeriesCard({
    series: s,
    onTogglePause,
    onDelete
}: RecurringSeriesCardProps) {
    return (
        <div className={`glass-card p-8 border transition-all relative overflow-hidden group ${s.paused ? 'border-primary-500/10 opacity-60' : 'border-primary-500/20 hover:border-primary-500/40 shadow-mist'}`}>
            <div className="absolute top-0 right-0 p-4">
                {s.paused ? (
                    <div className="text-[8px] font-black text-primary-500/40 uppercase italic tracking-widest bg-primary-500/5 px-2 py-1 rounded border border-primary-500/10">Standby</div>
                ) : (
                    <div className="flex items-center space-x-1.5">
                        <div className="w-1.5 h-1.5 bg-primary-500 rounded-full animate-pulse shadow-mist"></div>
                        <span className="text-[8px] font-black text-primary-500 uppercase italic tracking-widest">Active</span>
                    </div>
                )}
            </div>

            <div className="mb-8">
                <h4 className="text-2xl font-black text-white tracking-tighter italic uppercase group-hover:text-primary-400 transition-colors mb-2">
                    {s.title}
                </h4>
                <div className="flex items-center space-x-3 text-primary-50/30 text-[10px] font-black uppercase tracking-widest italic">
                    <Repeat className="w-3 h-3" />
                    <span>{s.frequency} • Every {s.interval} unit(s)</span>
                </div>
            </div>

            <div className="space-y-4 mb-10 pt-6 border-t border-primary-500/10">
                <div className="flex items-center space-x-3 text-primary-50/40">
                    <Calendar className="w-4 h-4" />
                    <span className="text-xs font-medium italic">Commenced: {new Date(s.startDate).toLocaleDateString()}</span>
                </div>
                {s.endDate && (
                    <div className="flex items-center space-x-3 text-primary-50/40">
                        <AlertCircle className="w-4 h-4" />
                        <span className="text-xs font-medium italic">Terminates: {new Date(s.endDate).toLocaleDateString()}</span>
                    </div>
                )}
            </div>

            <div className="flex items-center gap-3">
                <button
                    onClick={() => onTogglePause(s.id, s.paused)}
                    className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-black text-[10px] uppercase tracking-[0.2em] italic border transition-all ${s.paused
                        ? 'bg-primary-500 text-white border-primary-500 shadow-mist'
                        : 'bg-primary-500/5 text-primary-500 border-primary-500/20 hover:bg-primary-500/10'
                        }`}
                >
                    {s.paused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
                    {s.paused ? 'Resume' : 'Pause'}
                </button>
                <button
                    onClick={() => onDelete(s.id)}
                    className="p-3 bg-red-500/5 hover:bg-red-500/10 text-red-500 border border-red-500/20 rounded-xl transition-all"
                >
                    <Trash2 className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}
