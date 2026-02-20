"use client";

import React from "react";

interface HighlightedTextProps {
    text: string;
    query?: string;
    className?: string;
    highlightClassName?: string;
}

export function HighlightedText({
    text,
    query,
    className = "",
    highlightClassName = "bg-primary-500/30 text-white rounded-sm px-0.5"
}: HighlightedTextProps) {
    if (!query || !query.trim()) {
        return <span className={className}>{text}</span>;
    }

    const parts = text.split(new RegExp(`(${query})`, "gi"));

    return (
        <span className={className}>
            {parts.map((part, i) => (
                part.toLowerCase() === query.toLowerCase() ? (
                    <mark key={i} className={highlightClassName}>
                        {part}
                    </mark>
                ) : (
                    <React.Fragment key={i}>{part}</React.Fragment>
                )
            ))}
        </span>
    );
}
