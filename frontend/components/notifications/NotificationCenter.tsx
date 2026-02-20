"use client";

import { useEvents } from "@/hooks/useEvents";
import { useEffect, useState } from "react";
import { ReminderToast } from "./ReminderToast";

export function NotificationCenter() {
    const { lastEvent } = useEvents();
    const [activeNotification, setActiveNotification] = useState<{
        id: string;
        title: string;
        message: string;
        taskId: string;
    } | null>(null);

    useEffect(() => {
        if (lastEvent) {
            const { type, payload } = lastEvent;

            let title = "";
            let message = "";

            switch (type) {
                case "TaskCreated":
                    title = "New Directive Registered";
                    message = `Task "${payload.title}" has been added to the matrix.`;
                    break;
                case "TaskCompleted":
                    title = "Directive Synchronized";
                    message = `Task "${payload.title}" has been marked as complete.`;
                    break;
                case "Reminder":
                    title = "Strategic Alert";
                    message = payload.message || `Deadline approaching for "${payload.title}".`;
                    break;
                default:
                    return; // Ignore other events for now
            }

            setActiveNotification({
                id: Date.now().toString(),
                title,
                message,
                taskId: payload.task_id
            });
        }
    }, [lastEvent]);

    if (!activeNotification) return null;

    return (
        <ReminderToast
            key={activeNotification.id}
            title={activeNotification.title}
            message={activeNotification.message}
            taskId={activeNotification.taskId}
            onClose={() => setActiveNotification(null)}
        />
    );
}
