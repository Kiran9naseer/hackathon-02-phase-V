// app/(protected)/layout.tsx
"use client";

import LoggedInNavbar from '@/components/layout/LoggedInNavbar';
import { CommandPalette } from '@/components/command/CommandPalette';
import { NotificationCenter } from '@/components/notifications/NotificationCenter';
import React, { useEffect, useState } from 'react';
import { useTheme } from 'next-themes';

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { theme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="flex flex-col min-h-screen transition-colors duration-300 bg-surface-dark text-primary-50">
      <LoggedInNavbar />
      <NotificationCenter />
      <CommandPalette />
      <main className="flex-grow p-4 md:p-8 bg-surface-dark/50">
        {children}
      </main>
    </div>
  );
}
