'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Sparkles, BarChart3, Upload, LogOut, User, Cpu } from 'lucide-react';
import { getAuthToken, clearAuthToken } from '@/lib/api';

export default function Navbar() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [userEmail, setUserEmail] = useState<string>('');

  useEffect(() => {
    const token = getAuthToken();
    setIsAuthenticated(!!token);
    if (typeof window !== 'undefined') {
      const email = localStorage.getItem('user_email') || '';
      setUserEmail(email);
    }
  }, []);

  const handleLogout = () => {
    clearAuthToken();
    setIsAuthenticated(false);
    router.push('/login');
  };

  return (
    <nav className="fixed top-4 left-1/2 -translate-x-1/2 w-[92%] max-w-6xl z-50 glass-panel px-6 py-3.5 flex items-center justify-between transition-all duration-300">
      <Link href="/" className="flex items-center gap-3 group">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-accent-violet to-accent-cyan p-[1px] shadow-lg shadow-accent-violet/20 group-hover:scale-105 transition-transform">
          <div className="w-full h-full bg-[#0d0922] rounded-[11px] flex items-center justify-center">
            <Cpu className="w-5 h-5 text-accent-cyan group-hover:rotate-12 transition-transform duration-300" />
          </div>
        </div>
        <div>
          <span className="text-lg font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-accent-violetGlow">
            AI Interview Coach
          </span>
          <span className="block text-[10px] text-accent-cyan font-mono tracking-wider uppercase -mt-0.5">
            OpenRouter Intelligence
          </span>
        </div>
      </Link>

      <div className="flex items-center gap-2 sm:gap-4">
        {isAuthenticated ? (
          <>
            <Link
              href="/upload"
              className="flex items-center gap-2 text-sm font-medium text-slate-300 hover:text-white px-3.5 py-2 rounded-lg hover:bg-white/5 transition-colors"
            >
              <Upload className="w-4 h-4 text-accent-cyan" />
              <span className="hidden sm:inline">New Interview</span>
            </Link>
            <Link
              href="/dashboard"
              className="flex items-center gap-2 text-sm font-medium text-slate-300 hover:text-white px-3.5 py-2 rounded-lg hover:bg-white/5 transition-colors"
            >
              <BarChart3 className="w-4 h-4 text-accent-violetGlow" />
              <span className="hidden sm:inline">Dashboard</span>
            </Link>
            <div className="h-5 w-[1px] bg-white/10 mx-1 hidden sm:block" />
            <div className="hidden md:flex items-center gap-2 text-xs font-mono text-slate-400 bg-white/5 px-3 py-1.5 rounded-full border border-white/10">
              <User className="w-3.5 h-3.5 text-accent-cyan" />
              <span className="max-w-[120px] truncate">{userEmail}</span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 text-xs text-rose-400 hover:text-rose-300 px-3 py-1.5 rounded-full border border-rose-500/20 hover:border-rose-500/40 hover:bg-rose-500/10 transition-all"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </>
        ) : (
          <>
            <Link
              href="/login"
              className="text-sm font-medium text-slate-300 hover:text-white px-4 py-2 rounded-full hover:bg-white/5 transition-colors"
            >
              Login
            </Link>
            <Link
              href="/signup"
              className="glass-button-primary text-xs sm:text-sm py-2 px-5"
            >
              Get Started
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
