'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line
} from 'recharts';
import {
  BarChart3, AlertTriangle, CheckCircle, TrendingUp, Sparkles, Plus,
  Layers, Volume2, MessageSquare, Target, ArrowRight, Briefcase
} from 'lucide-react';
import { api, getAuthToken, JobMatchData } from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const [topicScores, setTopicScores] = useState<any[]>([]);
  const [weakTopics, setWeakTopics] = useState<string[]>([]);
  const [grammarOverallAvg, setGrammarOverallAvg] = useState<number>(8.0);
  const [commonGrammarIssues, setCommonGrammarIssues] = useState<any[]>([]);
  const [latestJobMatches, setLatestJobMatches] = useState<JobMatchData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (!getAuthToken()) {
      router.push('/login');
      return;
    }
    loadProgress();
  }, []);

  const loadProgress = async () => {
    setLoading(true);
    try {
      const data = await api.getProgress();
      setTopicScores(data.topic_scores || []);
      setWeakTopics(data.weak_topics || []);
      setGrammarOverallAvg(data.grammar_overall_avg || 8.0);
      setCommonGrammarIssues(data.common_grammar_issues || []);
      if (data.latest_job_matches) {
        setLatestJobMatches(data.latest_job_matches);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load progress data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <Sparkles className="w-10 h-10 text-accent-cyan animate-spin" />
        <p className="text-sm text-slate-300">Loading progress analytics, topic scores & job recommendations...</p>
      </div>
    );
  }

  // Custom Glass Tooltip for Recharts Content Score
  const CustomTopicTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="glass-panel p-3 border border-white/20 shadow-2xl text-xs space-y-1">
          <p className="font-bold text-white">{data.topic_tag}</p>
          <p className="text-accent-cyan font-mono">
            Content Score: <span className="font-bold text-white">{data.rolling_avg_score.toFixed(1)} / 10</span>
          </p>
          <p className="text-slate-400">Total Evaluations: {data.sessions_count}</p>
        </div>
      );
    }
    return null;
  };

  // Custom Glass Tooltip for Recharts Grammar Score
  const CustomGrammarTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="glass-panel p-3 border border-white/20 shadow-2xl text-xs space-y-1">
          <p className="font-bold text-white">{data.topic_tag}</p>
          <p className="text-accent-violetGlow font-mono">
            Grammar Score: <span className="font-bold text-white">{data.grammar_rolling_avg?.toFixed(1) || '8.0'} / 10</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header Banner */}
      <div className="glass-panel p-8 flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-accent-violetGlow" />
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Skill & Communication Dashboard</h1>
          </div>
          <p className="text-sm text-slate-300">
            Real-time rolling averages for Technical Domain Mastery, Grammar Quality, and Role Matching.
          </p>
        </div>

        <Link
          href="/upload"
          className="glass-button-primary py-3 px-6 text-xs flex items-center justify-center gap-2 self-start md:self-center"
        >
          <Plus className="w-4 h-4" />
          <span>New Mock Interview</span>
        </Link>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* Recommended Roles Widget (Top 3 Matches from Resume) */}
      {latestJobMatches && latestJobMatches.recommended_roles && (
        <div className="glass-panel p-6 sm:p-8 space-y-4 border-l-4 border-l-accent-cyan">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-accent-cyan" />
                <span>Top Recommended Roles for Your Profile</span>
              </h3>
              <p className="text-xs text-slate-400">
                {latestJobMatches.summary || 'Based on your latest uploaded resume analysis'}
              </p>
            </div>
            <Link href="/upload" className="text-xs font-semibold text-accent-cyan hover:underline self-start sm:self-center">
              Re-analyze Resume →
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            {latestJobMatches.recommended_roles.slice(0, 3).map((role, rIdx) => (
              <div key={rIdx} className="glass-panel-interactive p-4 space-y-3 flex flex-col justify-between">
                <div className="space-y-1.5">
                  <div className="flex items-start justify-between gap-1">
                    <h4 className="text-sm font-bold text-white leading-snug">{role.title}</h4>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/40">
                      {role.match_score}%
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 line-clamp-2">{role.reasoning}</p>
                </div>
                <Link
                  href="/upload"
                  className="glass-button-secondary py-2 text-[11px] text-center w-full flex items-center justify-center gap-1 mt-2"
                >
                  <span>Practice for Role</span>
                  <ArrowRight className="w-3 h-3 text-accent-cyan" />
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Overview Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-panel p-6 space-y-2 border-l-4 border-l-accent-cyan">
          <span className="text-xs uppercase font-mono text-slate-400">Topics Analyzed</span>
          <p className="text-3xl font-extrabold text-white">{topicScores.length}</p>
          <p className="text-xs text-slate-400">Tracked across mock interviews</p>
        </div>

        <div className="glass-panel p-6 space-y-2 border-l-4 border-l-accent-violet">
          <span className="text-xs uppercase font-mono text-slate-400">Current Weak Topics</span>
          <p className="text-3xl font-extrabold text-accent-violetGlow">{weakTopics.length}</p>
          <p className="text-xs text-slate-400">Rolling avg &lt; 6.0 (2+ sessions)</p>
        </div>

        <div className="glass-panel p-6 space-y-2 border-l-4 border-l-emerald-500">
          <span className="text-xs uppercase font-mono text-slate-400">Content Readiness</span>
          <p className="text-3xl font-extrabold text-emerald-400">
            {topicScores.length > 0
              ? (
                  topicScores.reduce((acc, curr) => acc + curr.rolling_avg_score, 0) / topicScores.length
                ).toFixed(1)
              : '0.0'}{' '}
            <span className="text-sm font-normal text-slate-400">/ 10</span>
          </p>
          <p className="text-xs text-slate-400">Average content score</p>
        </div>

        <div className="glass-panel p-6 space-y-2 border-l-4 border-l-indigo-400">
          <span className="text-xs uppercase font-mono text-slate-400">Communication Score</span>
          <p className="text-3xl font-extrabold text-indigo-300">
            {grammarOverallAvg.toFixed(1)}{' '}
            <span className="text-sm font-normal text-slate-400">/ 10</span>
          </p>
          <p className="text-xs text-slate-400">Average speech/grammar rating</p>
        </div>
      </div>

      {/* Main Dual Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Chart 1: Technical Domain Content Scores */}
        <div className="glass-panel p-6 sm:p-8 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-base sm:text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-accent-cyan" />
              <span>Technical Domain Scores</span>
            </h3>
            <span className="text-xs font-mono text-slate-400">Benchmark: 6.0</span>
          </div>

          {topicScores.length > 0 ? (
            <div className="h-[280px] w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topicScores} margin={{ top: 10, right: 10, left: -15, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis
                    dataKey="topic_tag"
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    angle={-20}
                    textAnchor="end"
                  />
                  <YAxis domain={[0, 10]} stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip content={<CustomTopicTooltip />} />
                  <Bar dataKey="rolling_avg_score" radius={[8, 8, 0, 0]}>
                    {topicScores.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={
                          entry.rolling_avg_score < 6.0
                            ? '#f43f5e'
                            : entry.rolling_avg_score < 8.0
                            ? '#f59e0b'
                            : '#06b6d4'
                        }
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-center text-slate-400 space-y-2">
              <Layers className="w-10 h-10 opacity-30 text-accent-violet" />
              <p className="text-sm">No technical topic scores recorded yet.</p>
            </div>
          )}
        </div>

        {/* Chart 2: Grammar & Communication Scores */}
        <div className="glass-panel p-6 sm:p-8 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-base sm:text-lg font-bold text-white flex items-center gap-2">
              <Volume2 className="w-5 h-5 text-accent-violetGlow" />
              <span>Communication & Grammar Trend</span>
            </h3>
            <span className="text-xs font-mono text-slate-400">Target: &ge; 8.0</span>
          </div>

          {topicScores.length > 0 ? (
            <div className="h-[280px] w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={topicScores} margin={{ top: 10, right: 10, left: -15, bottom: 25 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis
                    dataKey="topic_tag"
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 11 }}
                    angle={-20}
                    textAnchor="end"
                  />
                  <YAxis domain={[0, 10]} stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip content={<CustomGrammarTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="grammar_rolling_avg"
                    stroke="#8b5cf6"
                    strokeWidth={3}
                    dot={{ fill: '#a78bfa', r: 5 }}
                    activeDot={{ r: 8 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-center text-slate-400 space-y-2">
              <MessageSquare className="w-10 h-10 opacity-30 text-accent-cyan" />
              <p className="text-sm">No communication data recorded yet.</p>
            </div>
          )}
        </div>
      </div>

      {/* Weak Technical Topics & Grammar Issue Insights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Technical Weak Topics Card */}
        <div className="glass-panel p-6 sm:p-8 space-y-6">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-rose-400" />
            <span>Currently Weak Content Topics</span>
          </h3>

          {weakTopics.length > 0 ? (
            <div className="space-y-3">
              {weakTopics.map((topic, idx) => (
                <div
                  key={idx}
                  className="glass-panel-interactive p-4 border-l-4 border-l-rose-500 flex items-center justify-between"
                >
                  <div className="space-y-1">
                    <p className="text-sm font-bold text-white">{topic}</p>
                    <p className="text-xs text-rose-300">Requires dedicated practice</p>
                  </div>
                  <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/40">
                    Weak Focus
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center text-center h-40 text-slate-400 space-y-2">
              <CheckCircle className="w-9 h-9 text-emerald-400 opacity-60" />
              <p className="text-sm font-medium text-slate-300">No weak topics flagged!</p>
            </div>
          )}
        </div>

        {/* Common Grammar Issue Patterns Card */}
        <div className="glass-panel p-6 sm:p-8 space-y-6">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <Volume2 className="w-5 h-5 text-accent-cyan" />
            <span>Recurring Speech & Grammar Patterns</span>
          </h3>

          {commonGrammarIssues.length > 0 ? (
            <div className="space-y-3">
              {commonGrammarIssues.map((issue, idx) => (
                <div
                  key={idx}
                  className="glass-panel-interactive p-4 border-l-4 border-l-accent-cyan flex items-center justify-between"
                >
                  <div className="space-y-1">
                    <p className="text-sm font-bold text-white capitalize">{issue.type.replace('_', ' ')}</p>
                    <p className="text-xs text-slate-300">Logged across past interview answers</p>
                  </div>
                  <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-accent-cyan/20 text-accent-cyan border border-accent-cyan/40">
                    {issue.count} occurrences
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center text-center h-40 text-slate-400 space-y-2">
              <CheckCircle className="w-9 h-9 text-emerald-400 opacity-60" />
              <p className="text-sm font-medium text-slate-300">Grammar & tone look great!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
