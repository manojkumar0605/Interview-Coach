'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Send, Sparkles, CheckCircle, ArrowRight, MessageSquare, ChevronDown,
  ChevronUp, AlertCircle, Sparkle, ShieldCheck, CheckCircle2, Edit3, Volume2
} from 'lucide-react';
import { api, getAuthToken, GrammarEvaluationData } from '@/lib/api';

interface QuestionItem {
  id: number;
  text: string;
  topic_tag: string;
  difficulty: string;
  type: string;
  order_index: number;
  answer?: string | null;
  evaluation?: {
    score: number;
    criteria_json: any;
    rationale: string;
    ideal_answer_json: string[];
    topic_tag: string;
  } | null;
  grammar_evaluation?: GrammarEvaluationData | null;
}

export default function InterviewSessionPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = parseInt(params.sessionId as string, 10);

  const [session, setSession] = useState<any>(null);
  const [questions, setQuestions] = useState<QuestionItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [userAnswer, setUserAnswer] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [completing, setCompleting] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [showRationale, setShowRationale] = useState<boolean>(true);
  const [showGrammarNotes, setShowGrammarNotes] = useState<boolean>(true);
  const [showCorrectedMap, setShowCorrectedMap] = useState<Record<number, boolean>>({});

  const chatBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!getAuthToken()) {
      router.push('/login');
      return;
    }
    loadSession();
  }, [sessionId]);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [questions, currentIndex, submitting]);

  const loadSession = async () => {
    try {
      const data = await api.getSession(sessionId);
      setSession(data);
      setQuestions(data.questions || []);

      const firstUnanswered = (data.questions || []).findIndex((q: any) => !q.answer);
      if (firstUnanswered !== -1) {
        setCurrentIndex(firstUnanswered);
      } else {
        setCurrentIndex((data.questions || []).length - 1);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load interview session');
    }
  };

  const handleAnswerSubmit = async () => {
    if (!userAnswer.trim() || submitting) return;

    setSubmitting(true);
    setError('');

    try {
      const resp = await api.submitAnswer(sessionId, userAnswer.trim());

      setQuestions((prev) => {
        const updated = [...prev];
        updated[currentIndex] = {
          ...updated[currentIndex],
          answer: userAnswer.trim(),
          evaluation: resp.evaluation,
          grammar_evaluation: resp.grammar_evaluation,
        };

        if (resp.follow_up_question) {
          updated.splice(currentIndex + 1, 0, resp.follow_up_question);
        }

        return updated;
      });

      setUserAnswer('');
    } catch (err: any) {
      setError(err.message || 'Failed to submit answer');
    } finally {
      setSubmitting(false);
    }
  };

  const handleNextQuestion = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const handleCompleteSession = async () => {
    setCompleting(true);
    try {
      await api.completeSession(sessionId);
      router.push(`/results/${sessionId}`);
    } catch (err: any) {
      setError(err.message || 'Failed to finalize interview session');
      setCompleting(false);
    }
  };

  const toggleCorrectedVersion = (qIdx: number) => {
    setShowCorrectedMap((prev) => ({
      ...prev,
      [qIdx]: !prev[qIdx],
    }));
  };

  const getScoreBadgeColor = (score: number) => {
    if (score < 5.0) return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
    if (score < 8.0) return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
    return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
  };

  const currentQ = questions[currentIndex];
  const allAnswered = questions.length > 0 && questions.every((q) => !!q.answer);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header bar */}
      <div className="glass-panel px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-mono text-accent-cyan uppercase tracking-wider">
            Mock Interview Session #{sessionId}
          </span>
          <h2 className="text-xl font-bold text-white">
            Role Target: {session?.role_target || 'Software Engineer'}
          </h2>
        </div>
        <div className="flex items-center gap-3">
          <div className="text-xs font-mono text-slate-300 bg-white/5 px-3 py-1.5 rounded-full border border-white/10">
            Question {Math.min(currentIndex + 1, questions.length)} of {questions.length}
          </div>
          {allAnswered && (
            <button
              onClick={handleCompleteSession}
              disabled={completing}
              className="glass-button-primary py-2 px-5 text-xs flex items-center gap-1.5"
            >
              <span>{completing ? 'Finalizing...' : 'View Results & Study Plan'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* Main Q&A Chat Feed */}
      <div className="space-y-6">
        {questions.slice(0, currentIndex + 1).map((q, idx) => {
          const isCurrentActive = idx === currentIndex;
          const isShowingCorrected = !!showCorrectedMap[idx];

          return (
            <div key={q.id || idx} className="space-y-4 transition-all duration-300">
              {/* Question Bubble (Left Offset Glass Card) */}
              <div className="glass-panel p-6 border-l-4 border-l-accent-violet max-w-3xl space-y-3 shadow-xl">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-semibold bg-accent-violet/20 border border-accent-violet/40 text-accent-violetGlow">
                      {q.topic_tag}
                    </span>
                    <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono text-slate-400 bg-white/5 border border-white/10 uppercase">
                      {q.type}
                    </span>
                  </div>
                  <span className="text-xs text-slate-400 capitalize">Difficulty: {q.difficulty}</span>
                </div>
                <p className="text-base sm:text-lg text-white font-medium leading-relaxed">
                  {q.text}
                </p>
              </div>

              {/* Answer Bubble & Dual Evaluation Panels */}
              {q.answer ? (
                <div className="ml-auto glass-panel p-6 border-r-4 border-r-accent-cyan max-w-3xl space-y-5 shadow-xl bg-white/[0.08]">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-xs font-semibold text-accent-cyan uppercase tracking-wider flex items-center gap-1.5">
                      <MessageSquare className="w-3.5 h-3.5" />
                      <span>Your Response</span>
                    </span>

                    <div className="flex flex-wrap items-center gap-2">
                      {q.evaluation && (
                        <div
                          className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1.5 ${getScoreBadgeColor(
                            q.evaluation.score
                          )}`}
                        >
                          <Sparkles className="w-3.5 h-3.5" />
                          <span>Content Score: {q.evaluation.score.toFixed(1)} / 10</span>
                        </div>
                      )}
                      {q.grammar_evaluation && (
                        <div
                          className={`px-3 py-1 rounded-full text-xs font-bold border flex items-center gap-1.5 ${getScoreBadgeColor(
                            q.grammar_evaluation.grammar_score
                          )}`}
                        >
                          <Volume2 className="w-3.5 h-3.5" />
                          <span>Communication: {q.grammar_evaluation.grammar_score.toFixed(1)} / 10</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Candidate Answer / Toggle Corrected Version */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-mono text-slate-400">
                        {isShowingCorrected ? 'AI Rewritten Clean Version:' : 'Original Submitted Response:'}
                      </span>
                      {q.grammar_evaluation?.corrected_version && (
                        <button
                          onClick={() => toggleCorrectedVersion(idx)}
                          className="text-xs font-medium text-accent-cyan hover:underline flex items-center gap-1"
                        >
                          <Edit3 className="w-3 h-3" />
                          <span>{isShowingCorrected ? 'Show Original' : 'Show AI Polish'}</span>
                        </button>
                      )}
                    </div>
                    <p className={`text-sm sm:text-base whitespace-pre-wrap leading-relaxed ${isShowingCorrected ? 'text-accent-cyan bg-accent-cyan/10 p-4 rounded-xl border border-accent-cyan/20 font-sans' : 'text-slate-200'}`}>
                      {isShowingCorrected ? q.grammar_evaluation?.corrected_version : q.answer}
                    </p>
                  </div>

                  {/* Grid of Content Evaluation & Grammar Coach Panels */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-3 border-t border-white/10">
                    {/* Content Evaluation Panel */}
                    {q.evaluation && (
                      <div className="glass-panel p-4 rounded-2xl space-y-3 bg-white/[0.03]">
                        <span className="text-xs font-bold text-white flex items-center gap-1.5">
                          <Sparkles className="w-3.5 h-3.5 text-accent-violetGlow" />
                          <span>Content Quality Rubric</span>
                        </span>

                        <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
                          <div className="bg-white/5 p-2 rounded-lg">
                            <span className="block text-slate-400">Clarity</span>
                            <span className="font-bold text-white">{q.evaluation.criteria_json?.clarity || 7}/10</span>
                          </div>
                          <div className="bg-white/5 p-2 rounded-lg">
                            <span className="block text-slate-400">Specific</span>
                            <span className="font-bold text-white">{q.evaluation.criteria_json?.specificity || 7}/10</span>
                          </div>
                          <div className="bg-white/5 p-2 rounded-lg">
                            <span className="block text-slate-400">Relevance</span>
                            <span className="font-bold text-white">{q.evaluation.criteria_json?.relevance || 7}/10</span>
                          </div>
                        </div>

                        <p className="text-xs text-slate-300 leading-relaxed bg-white/5 p-3 rounded-xl border border-white/10">
                          {q.evaluation.rationale}
                        </p>
                      </div>
                    )}

                    {/* Grammar & Communication Coach Panel */}
                    {q.grammar_evaluation && (
                      <div className="glass-panel p-4 rounded-2xl space-y-3 bg-white/[0.03] border-l-2 border-l-accent-cyan">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-white flex items-center gap-1.5">
                            <Volume2 className="w-3.5 h-3.5 text-accent-cyan" />
                            <span>Grammar & Speech Coach</span>
                          </span>
                          <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-white/10 text-slate-300">
                            Tone: {q.grammar_evaluation.tone}
                          </span>
                        </div>

                        <div className="flex items-center justify-between text-xs bg-white/5 p-2.5 rounded-xl border border-white/10">
                          <span className="text-slate-400">Filler Words Detected:</span>
                          <span className="font-bold text-amber-300 font-mono">
                            {q.grammar_evaluation.filler_word_count} found
                          </span>
                        </div>

                        {/* Collapsible Grammar Notes */}
                        <div className="space-y-2">
                          <button
                            onClick={() => setShowGrammarNotes(!showGrammarNotes)}
                            className="flex items-center gap-1 text-[11px] text-slate-300 hover:text-white font-medium"
                          >
                            <span>Grammar Notes & Suggestions ({q.grammar_evaluation.issues.length})</span>
                            {showGrammarNotes ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                          </button>

                          {showGrammarNotes && (
                            <div className="space-y-2 max-h-44 overflow-y-auto pr-1">
                              {q.grammar_evaluation.issues.length > 0 ? (
                                q.grammar_evaluation.issues.map((issue, iIdx) => (
                                  <div key={iIdx} className="text-xs p-2.5 rounded-xl bg-white/5 border border-white/10 space-y-1">
                                    <div className="flex items-center gap-1.5">
                                      <span className="px-1.5 py-0.5 text-[9px] uppercase font-mono rounded bg-accent-violet/20 text-accent-violetGlow">
                                        {issue.type}
                                      </span>
                                      <span className="text-rose-300 line-through truncate max-w-[120px]">
                                        "{issue.original}"
                                      </span>
                                      <span className="text-slate-400">→</span>
                                      <span className="text-emerald-300 font-medium truncate max-w-[120px]">
                                        "{issue.suggestion}"
                                      </span>
                                    </div>
                                    <p className="text-[11px] text-slate-400">{issue.explanation}</p>
                                  </div>
                                ))
                              ) : (
                                <p className="text-xs text-emerald-300 italic p-2 bg-emerald-500/10 rounded-lg">
                                  No grammatical flaws or filler word issues detected!
                                </p>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ) : isCurrentActive ? (
                /* Textarea for current unanswered question */
                <div className="ml-auto glass-panel p-6 max-w-3xl space-y-4 shadow-2xl border-accent-cyan/30">
                  <div className="space-y-2">
                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center justify-between">
                      <span>Formulate Your Answer</span>
                      <span className="text-slate-400 font-mono text-[11px]">Evaluated for Content & Grammar</span>
                    </label>
                    <textarea
                      rows={5}
                      value={userAnswer}
                      onChange={(e) => setUserAnswer(e.target.value)}
                      placeholder="Structure your answer clearly. Highlight specific tech stack, architecture decisions, STAR framework metrics, or tradeoffs..."
                      className="glass-input w-full text-sm resize-y"
                    />
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <span className="text-xs text-slate-400">
                      Evaluated for technical depth and grammar precision
                    </span>
                    <button
                      onClick={handleAnswerSubmit}
                      disabled={submitting || !userAnswer.trim()}
                      className="glass-button-primary py-2.5 px-6 text-sm flex items-center gap-2 disabled:opacity-50"
                    >
                      {submitting ? (
                        <span>Analyzing Content & Grammar...</span>
                      ) : (
                        <>
                          <span>Submit Answer</span>
                          <Send className="w-4 h-4" />
                        </>
                      )}
                    </button>
                  </div>
                </div>
              ) : null}

              {/* Navigation button to next question if answered */}
              {q.answer && isCurrentActive && currentIndex < questions.length - 1 && (
                <div className="flex justify-end pt-2">
                  <button
                    onClick={handleNextQuestion}
                    className="glass-button-primary py-2.5 px-6 text-sm flex items-center gap-2"
                  >
                    <span>Proceed to Next Question</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          );
        })}

        <div ref={chatBottomRef} />
      </div>
    </div>
  );
}
