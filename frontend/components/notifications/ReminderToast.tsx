"use client";

import { useEffect, useState } from "react";
import { Bell, X, ArrowRight } from "lucide-react";
import Link from "next/link";

interface ReminderToastProps {
    title: string;
    message: string;
    taskId: string;
    onClose: () => void;
}

export function ReminderToast({ title, message, taskId, onClose }: ReminderToastProps) {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        setIsVisible(true);
        const timer = setTimeout(() => {
            setIsVisible(false);
            setTimeout(onClose, 500);
        }, 8000);
        return () => clearTimeout(timer);
    }, [onClose]);

    return (
        <div
            className={`fixed bottom-8 right-8 z-[300] w-96 transform transition-all duration-500 ease-out ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0'
                }`}
        >
            <div className="glass-card p-6 border-primary-500/30 shadow-mist-glow overflow-hidden relative group">
                {/* Progress Bar */}
                <div className="absolute bottom-0 left-0 h-1 bg-primary-500/40 animate-shrink-width w-full"></div>

                <div className="flex items-start space-x-4">
                    <div className="p-3 bg-primary-500 rounded-xl shadow-mist shrink-0">
                        <Bell className="w-5 h-5 text-white" />
                    </div>

                    <div className="flex-grow">
                        <div className="flex justify-between items-start mb-1">
                            <h4 className="text-sm font-black text-white uppercase italic tracking-tighter">Strategic Dispatch</h4>
                            <button onClick={() => setIsVisible(false)} className="text-primary-100/20 hover:text-white transition-colors">
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                        <p className="text-xs font-bold text-primary-500 mb-2 italic">{title}</p>
                        <p className="text-[10px] text-primary-50/40 font-medium mb-4 italic leading-relaxed">{message}</p>

                        <Link
                            href={`/tasks/${taskId}`}
                            className="inline-flex items-center text-[10px] font-black uppercase tracking-widest text-white italic group/btn"
                            onClick={() => setIsVisible(false)}
                        >
                            Access Vector
                            <ArrowRight className="w-3 h-3 ml-2 group-hover/btn:translate-x-1 transition-transform" />
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
