"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { getToken } from "@/lib/auth/hooks";

export interface SystemEvent {
  type: string;
  payload: any;
}

export function useEvents() {
  const [lastEvent, setLastEvent] = useState<SystemEvent | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback(async () => {
    // We need the token for authentication if the endpoint is protected
    // EventSource doesn't support custom headers easily, so we usually pass it as a query param
    // or use a wrapper that supports headers.
    const token = await getToken();
    if (!token) return;

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/events/stream?token=${token}`;
    const es = new EventSource(url);

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastEvent(data);
      } catch (err) {
        console.error("Failed to parse SSE event:", err);
      }
    };

    es.onerror = (err) => {
      console.error("SSE Connection error:", err);
      es.close();
      // Simple reconnection logic
      setTimeout(connect, 5000);
    };

    eventSourceRef.current = es;
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [connect]);

  return { lastEvent };
}
