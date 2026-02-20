"use client";

import { Bell } from "lucide-react";
import { Label } from "@/components/ui/Label";
import { Select } from "@/components/ui/Select";

interface ReminderConfigProps {
    offsets: number[];
    onChange: (offsets: number[]) => void;
}

const REMINDER_OPTIONS = [
    { label: "1 hour before", value: "-60" },
    { label: "2 hours before", value: "-120" },
    { label: "1 day before", value: "-1440" },
    { label: "2 days before", value: "-2880" },
    { label: "1 week before", value: "-10080" },
];

export function ReminderConfig({ offsets, onChange }: ReminderConfigProps) {
    const currentOffset = offsets.length > 0 ? offsets[0] : -1440;

    return (
        <div className="space-y-4 p-6 bg-primary-500/5 rounded-2xl border border-primary-500/10">
            <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-primary-500/10 rounded-lg">
                    <Bell className="w-4 h-4 text-primary-500" />
                </div>
                <h4 className="text-xs font-black text-white uppercase tracking-widest italic">Reminder Protocol</h4>
            </div>

            <div className="space-y-2">
                <Label className="text-[10px] uppercase tracking-widest text-primary-100/40 italic">Trigger Offset</Label>
                <Select
                    value={currentOffset.toString()}
                    onChange={(e) => onChange([parseInt(e.target.value)])}
                    className="bg-surface-dark border-primary-500/20 text-white font-bold italic"
                    options={REMINDER_OPTIONS}
                />
            </div>

            <p className="text-[10px] text-primary-100/20 italic font-medium">
                Notification will be dispatched to your neural interface at the selected window.
            </p>
        </div>
    );
}
