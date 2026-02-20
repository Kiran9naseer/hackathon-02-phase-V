"use client";

import { useState } from "react";
import { Label } from "@/components/ui/Label";
import { Select } from "@/components/ui/Select";
import { Input } from "@/components/ui/Input";
import { Repeat } from "lucide-react";

interface RecurringSettingsProps {
    frequency: string;
    interval: number;
    endDate?: string;
    onChange: (settings: { frequency: string; interval: number; endDate?: string }) => void;
}

export function RecurringSettings({
    frequency,
    interval,
    endDate,
    onChange
}: RecurringSettingsProps) {
    return (
        <div className="p-6 bg-primary-500/5 border border-primary-500/10 rounded-2xl animate-in fade-in slide-in-from-top-4 duration-500">
            <div className="flex items-center space-x-3 mb-6">
                <div className="w-8 h-8 bg-primary-500/10 rounded-lg flex items-center justify-center border border-primary-500/20">
                    <Repeat className="w-4 h-4 text-primary-500" />
                </div>
                <h4 className="text-sm font-black text-white italic uppercase tracking-widest">Recurrence Protocol</h4>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <div className="space-y-1.5">
                    <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 ml-1 italic">Frequency</Label>
                    <Select
                        value={frequency}
                        onChange={(e) => onChange({ frequency: e.target.value, interval, endDate })}
                        options={[
                            { value: "daily", label: "Daily Cycles" },
                            { value: "weekly", label: "Weekly Iterations" },
                            { value: "monthly", label: "Monthly Phases" },
                            { value: "yearly", label: "Annual Revolutions" },
                        ]}
                        className="premium-input w-full"
                    />
                </div>

                <div className="space-y-1.5">
                    <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 ml-1 italic">Interval</Label>
                    <Input
                        type="number"
                        min="1"
                        value={interval}
                        onChange={(e) => onChange({ frequency, interval: parseInt(e.target.value) || 1, endDate })}
                        className="premium-input w-full"
                    />
                </div>

                <div className="space-y-1.5 sm:col-span-2">
                    <Label className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-50/30 ml-1 italic">Terminate Date (Optional)</Label>
                    <Input
                        type="date"
                        value={endDate || ""}
                        onChange={(e) => onChange({ frequency, interval, endDate: e.target.value || undefined })}
                        className="premium-input w-full [color-scheme:dark]"
                    />
                </div>
            </div>
        </div>
    );
}
