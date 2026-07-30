'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Award, AlertTriangle, BookOpen, ArrowRight, BarChart2, CheckCircle2,
  Sparkles, RefreshCw, Volume2, MessageSquare, Edit3
} from 'lucide-react';
import { api, getAuthToken } from '@/lib/api';

export default function SessionResultsPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = parseInt(params.sessionId as string, 10);

  const [sessionData, setSessionData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (!getAuthToken()) {
      router.push('/login');
      return;
    }
    loadResults();
  }, [sessionId]);

  const loadResults = async () => {
    setLoading(true);
    try {
      const data = await api.getSession(sessionId);
      setSessionData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load session results');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Sparkles className="w-10 h-10 text-accent-cyan animate-spin" />
        <p className="text-sm text-slate-300">Generating session synthesis & personalized study plan...</p>
      </div>
    );
  }

  if (error || !sessionData) {
    return (
      <div className="glass-panel p-8 text-center max-w-md mx-auto space-y-4">
        <AlertTriangle className="w-10 h-10 text-rose-400 mx-auto" />
        <p className="text-slate-200">{error || 'Session not found'}</p>
        <Link href="/upload" className="glass-button-primary inline-block text-xs py-2 px-4">
          Start New Interview
        </Link>
      </div>
    );
  }

  const plan = sessionData.study_plan || {};
  const questions = sessionData.questions || [];

  // Calculate session overall average for content score & grammar score
  const scoredQs = questions.filter((q: any) => q.evaluation?.score !== undefined);
  const avgScore =
    scoredQs.length > 0
      ? (scoredQs.reduce((acc: number, q: any) => acc + q.evaluation.score, 0) / scoredQs.length).toFixed(1)
      : '7.5';

  const grammarScoredQs = questions.filter((q: any) => q.grammar_evaluation?.grammar_score !== undefined);
  const avgGrammarScore =
    grammarScoredQs.length > 0
      ? (grammarScoredQs.reduce((acc: number, q: any) => acc + q.grammar_evaluation.grammar_score, 0) / grammarScoredQs.length).toFixed(1)
      : '8.0';

  // Gather example corrections from session questions
  const exampleCorrections: any[] = [];
  questions.forEach((q: any) => {
    if (q.grammar_evaluation?.issues) {
      q.grammar_evaluation.issues.forEach((issue: any) => {
        if (exampleCorrections.length < 3 && issue.original && issue.suggestion) {
          exampleCorrections.push({
            original: issue.original,
            suggestion: issue.suggestion,
            explanation: issue.explanation,
          });
        }
      });
    }
  });

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header Banner */}
      <div className="glass-panel p-8 text-center relative overflow-hidden space-y-4">
        <div className="absolute top-0 right-0 w-64 h-64 bg-accent-violet/10 rounded-full blur-3xl pointer-events-none" />

        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono text-accent-cyan bg-accent-cyan/10 border border-accent-cyan/30">
          <Sparkles className="w-3.5 h-3.5" />
          Session #{sessionId} Complete
        </span>

        <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
          Performance Report & <span className="bg-clip-text text-transparent bg-gradient-to-r from-accent-violetGlow to-accent-cyan">Study Roadmap</span>
        </h1>

        <div className="flex flex-wrap items-center justify-center gap-6 pt-2">
          <div className="glass-panel px-6 py-3 rounded-2xl flex items-center gap-3">
            <span className="text-xs uppercase text-slate-400">Target Role</span>
            <span className="text-sm font-bold text-white">{sessionData.role_target}</span>
          </div>
          <div className="glass-panel px-6 py-3 rounded-2xl flex items-center gap-3">
            <span className="text-xs uppercase text-slate-400">Content Score</span>
            <span className="text-xl font-extrabold text-accent-violetGlow">{avgScore} / 10</span>
          </div>
          <div className="glass-panel px-6 py-3 rounded-2xl flex items-center gap-3">
            <span className="text-xs uppercase text-slate-400">Communication Score</span>
            <span className="text-xl font-extrabold text-accent-cyan">{avgGrammarScore} / 10</span>
          </div>
        </div>
      </div>

      {/* Narrative Performance Summary */}
      {plan.summary && (
        <div className="glass-panel p-6 sm:p-8 border-l-4 border-l-accent-cyan space-y-3">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-accent-cyan" />
            <span>AI Advisor Performance Summary</span>
          </h3>
          <p className="text-sm sm:text-base text-slate-300 leading-relaxed">{plan.summary}</p>
        </div>
      )}

      {/* Communication Summary Panel (NEW GRAMMAR COACH FEATURE) */}
      <div className="glass-panel p-6 sm:p-8 space-y-6 border-l-4 border-l-accent-violet">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Volume2 className="w-6 h-6 text-accent-violetGlow" />
            <span>Communication & Spoken Grammar Summary</span>
          </h3>
          <span className="text-xs font-mono font-bold px-3 py-1 rounded-full bg-accent-violet/20 text-accent-violetGlow border border-accent-violet/40">
            Average Score: {avgGrammarScore} / 10
          </span>
        </div>

        {plan.communication_feedback?.tone_summary && (
          <p className="text-sm text-slate-300 leading-relaxed">
            {plan.communication_feedback.tone_summary}
          </p>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          {/* Example Corrections */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-white flex items-center gap-1.5">
              <Edit3 className="w-4 h-4 text-accent-cyan" />
              <span>Example Speech & Grammar Corrections</span>
            </h4>
            {exampleCorrections.length > 0 ? (
              <div className="space-y-2">
                {exampleCorrections.map((corr, cIdx) => (
                  <div key={cIdx} className="text-xs p-3 rounded-xl bg-white/5 border border-white/10 space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-rose-300 line-through">"{corr.original}"</span>
                      <span className="text-slate-400">→</span>
                      <span className="text-emerald-300 font-medium">"{corr.suggestion}"</span>
                    </div>
                    <p className="text-[11px] text-slate-400">{corr.explanation}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-emerald-300 italic p-3 bg-emerald-500/10 rounded-xl">
                Clean grammatical delivery throughout the session with minimal filler words!
              </p>
            )}
          </div>

          {/* Actionable Speech Tips */}
          <div className="space-y-3">
            <h4 className="text-sm font-bold text-white flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Actionable Speech Tips</span>
            </h4>
            <div className="space-y-2">
              {(
                plan.communication_feedback?.actionable_tips || [
                  'Pause briefly before answering to structure thoughts without using "like/um".',
                  'Maintain clear subject-verb agreement during complex system design explanations.'
                ]
              ).map((tip: string, tIdx: number) => (
                <div key={tIdx} className="flex items-center gap-2 text-xs text-slate-200 bg-white/5 p-3 rounded-xl border border-white/10">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>{tip}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Technical Strengths vs Weak Topics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Key Strengths Card */}
        <div className="glass-panel p-6 space-y-4 border-t-4 border-t-emerald-500">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Award className="w-5 h-5 text-emerald-400" />
            <span>Identified Technical Strengths</span>
          </h3>
          <div className="space-y-2">
            {(plan.strengths || ['System Architecture', 'Problem Formulation']).map((item: string, idx: number) => (
              <div
                key={idx}
                className="flex items-center gap-2 text-sm text-slate-200 bg-emerald-500/10 border border-emerald-500/20 px-3.5 py-2.5 rounded-xl"
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Priority Weak Topics Card */}
        <div className="glass-panel p-6 space-y-4 border-t-4 border-t-rose-500">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-rose-400" />
            <span>Recurring Weak Content Topics</span>
          </h3>
          <div className="space-y-2">
            {(plan.weak_topics || []).length > 0 ? (
              (plan.weak_topics || []).map((item: string, idx: number) => (
                <div
                  key={idx}
                  className="flex items-center gap-2 text-sm text-rose-200 bg-rose-500/10 border border-rose-500/20 px-3.5 py-2.5 rounded-xl"
                >
                  <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                  <span>{item}</span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400 italic">No severe weak topics identified for this session!</p>
            )}
          </div>
        </div>
      </div>

      {/* Recommended Study Action Steps */}
      {plan.recommended_next_steps && (
        <div className="glass-panel p-6 sm:p-8 space-y-6">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-accent-violetGlow" />
            <span>Prioritized Study Recommendations</span>
          </h3>

          <div className="space-y-3">
            {plan.recommended_next_steps.map((step: any, idx: number) => (
              <div
                key={idx}
                className="glass-panel-interactive p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="space-y-1">
                  <span className="text-xs font-mono font-bold text-accent-cyan uppercase">{step.topic}</span>
                  <p className="text-sm text-slate-200">{step.action}</p>
                </div>
                <span
                  className={`self-start sm:self-center px-3 py-1 rounded-full text-xs font-mono font-semibold uppercase ${
                    step.priority === 'High'
                      ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                      : step.priority === 'Medium'
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                      : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                  }`}
                >
                  {step.priority || 'Medium'} Priority
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bottom Actions */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
        <Link
          href="/dashboard"
          className="glass-button-primary flex items-center justify-center gap-2 px-8 py-3.5 w-full sm:w-auto"
        >
          <BarChart2 className="w-4 h-4" />
          <span>View Progress Dashboard</span>
        </Link>
        <Link
          href="/upload"
          className="glass-button-secondary flex items-center justify-center gap-2 px-8 py-3.5 w-full sm:w-auto"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Start New Interview</span>
        </Link>
      </div>
    </div>
  );
}
