"use client";

import { Repeat } from "lucide-react";

interface RecurrenceBadgeProps {
    className?: string;
}

export function RecurrenceBadge({ className = "" }: RecurrenceBadgeProps) {
    return (
        <div
            className={`p-1.5 bg-primary-500/10 rounded-lg border border-primary-500/10 shadow-mist flex items-center justify-center ${className}`}
            title="Recurring Task Protocol Active"
        >
            <Repeat className="w-3.5 h-3.5 text-primary-500" />
        </div>
    );
}
