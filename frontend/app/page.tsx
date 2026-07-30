'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowRight, Sparkles, Target, BrainCircuit, BarChart2, ShieldCheck, Zap } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[75vh] text-center space-y-12">
      {/* Top Pill Badge */}
      <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-panel border-accent-violet/30 text-accent-violetGlow text-xs sm:text-sm font-medium tracking-wide shadow-lg shadow-accent-violet/10">
        <Sparkles className="w-4 h-4 text-accent-cyan animate-pulse" />
        <span>Powered by OpenRouter Multi-Model Intelligence</span>
      </div>

      {/* Hero Headline */}
      <div className="max-w-4xl space-y-6">
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
          Ace Your Next Interview with{' '}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-accent-violetGlow via-accent-cyan to-indigo-300">
            Real-Time AI Feedback
          </span>
        </h1>
        <p className="text-base sm:text-xl text-slate-300 font-normal max-w-2xl mx-auto leading-relaxed">
          Upload your resume, select your target role, and participate in tailored mock Q&A sessions. Get instant rubric evaluation, weak topic identification, and customized study roadmaps.
        </p>
      </div>

      {/* Call to Action Buttons */}
      <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
        <Link
          href="/upload"
          className="glass-button-primary flex items-center justify-center gap-2 text-base px-8 py-4 w-full sm:w-auto group"
        >
          <span>Start Mock Interview</span>
          <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </Link>
        <Link
          href="/dashboard"
          className="glass-button-secondary flex items-center justify-center gap-2 text-base px-8 py-4 w-full sm:w-auto"
        >
          <BarChart2 className="w-5 h-5 text-accent-cyan" />
          <span>View Progress Dashboard</span>
        </Link>
      </div>

      {/* Feature Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-5xl mt-12 text-left">
        <div className="glass-panel-interactive p-6 space-y-3">
          <div className="w-12 h-12 rounded-xl bg-accent-violet/20 border border-accent-violet/40 flex items-center justify-center text-accent-violetGlow">
            <Target className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Targeted Question Queues</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            AI customizes questions based on your resume, target position seniority, and historical weak areas.
          </p>
        </div>

        <div className="glass-panel-interactive p-6 space-y-3">
          <div className="w-12 h-12 rounded-xl bg-accent-cyan/20 border border-accent-cyan/40 flex items-center justify-center text-accent-cyan">
            <Zap className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Instant Rubric Scoring</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Get immediate feedback on clarity, specificity, and relevance, paired with ideal solution points.
          </p>
        </div>

        <div className="glass-panel-interactive p-6 space-y-3">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">Personalized Study Plan</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Track rolling averages across sessions and receive prioritized study recommendations to bridge skill gaps.
          </p>
        </div>
      </div>
    </div>
  );
}
