"use client";

import React, { useState, useCallback } from "react";
import ChatMessages from "./ChatMessages";
import ChatInput from "./ChatInput";
import { useAuth } from "@/hooks/useAuth";
import { getToken } from "@/lib/auth/hooks";
import { getEnv } from "@/lib/config";

interface Message {
    role: "user" | "assistant";
    content: string;
}

const ChatContainer: React.FC = () => {
    const { user } = useAuth();
    const [messages, setMessages] = useState<Message[]>([]);
    const [conversationId, setConversationId] = useState<number | undefined>(undefined);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSendMessage = useCallback(async (text: string) => {
        if (!user) {
            setError("You must be logged in to chat.");
            return;
        }

        const newMessage: Message = { role: "user", content: text };
        setMessages((prev) => [...prev, newMessage]);
        setIsLoading(true);
        setError(null);

        try {
            const token = await getToken();
            const apiUrl = getEnv().NEXT_PUBLIC_API_URL;

            const response = await fetch(`${apiUrl}/api/v1/${user.id}/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    conversation_id: conversationId,
                    message: text,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || "Failed to get response from AI");
            }

            const data = await response.json();

            if (data.conversation_id) {
                setConversationId(data.conversation_id);
            }

            const assistantMessage: Message = {
                role: "assistant",
                content: data.response,
            };

            setMessages((prev) => [...prev, assistantMessage]);
        } catch (err: any) {
            setError(err.message || "An error occurred. Please try again.");
            console.error("Chat error:", err);
        } finally {
            setIsLoading(false);
        }
    }, [user, conversationId]);

    return (
        <div className="flex flex-col h-[70vh] max-w-4xl mx-auto glass-card overflow-hidden">
            {/* Chat Header */}
            <div className="px-8 py-6 border-b border-primary-500/10 bg-surface-dark/80 backdrop-blur-xl">
                <h2 className="text-xl font-black text-white italic tracking-tighter uppercase">AI <span className="text-primary-500">Operative</span></h2>
                <p className="text-[10px] uppercase tracking-[0.2em] font-black text-primary-400 opacity-60">Neural Network Active</p>
            </div>

            {/* Messages Area */}
            <ChatMessages messages={messages} isLoading={isLoading} />

            {/* Error Message */}
            {error && (
                <div className="px-4 py-2 bg-red-500/10 border-t border-red-500/20 text-red-400 text-sm">
                    {error}
                </div>
            )}

            {/* Input Area */}
            <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
        </div>
    );
};

export default ChatContainer;
