'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  UploadCloud, FileText, CheckCircle2, ArrowRight, Sparkles, Briefcase,
  Award, Layers, Target, ChevronDown, ChevronUp, AlertCircle, TrendingUp
} from 'lucide-react';
import { api, getAuthToken, JobMatchData, RecommendedRoleData } from '@/lib/api';

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [targetRole, setTargetRole] = useState<string>('Senior Full Stack Engineer');
  const [uploading, setUploading] = useState<boolean>(false);
  const [resumeData, setResumeData] = useState<any>(null);
  const [jobMatches, setJobMatches] = useState<JobMatchData | null>(null);
  const [expandedRoleIdx, setExpandedRoleIdx] = useState<number | null>(null);
  const [startingSession, setStartingSession] = useState<boolean>(false);
  const [startingRoleTitle, setStartingRoleTitle] = useState<string>('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (!getAuthToken()) {
      router.push('/login');
    }
  }, [router]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError('');
    }
  };

  const handleUploadResume = async () => {
    if (!file) {
      setError('Please select a resume file (PDF or DOCX)');
      return;
    }
    if (!targetRole.trim()) {
      setError('Please specify your target role or select a recommended role below');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const data = await api.uploadResume(file, targetRole);
      setResumeData(data);
      if (data.job_matches) {
        setJobMatches(data.job_matches);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to upload and analyze resume');
    } finally {
      setUploading(false);
    }
  };

  const handleStartInterview = async (roleToUse?: string) => {
    if (!resumeData) return;
    const finalRole = roleToUse || targetRole;
    if (!finalRole.trim()) return;

    setStartingRoleTitle(finalRole);
    setStartingSession(true);
    setError('');

    try {
      const sessionResponse = await api.startSession(resumeData.id, finalRole);
      router.push(`/interview/${sessionResponse.session_id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to initialize interview session');
      setStartingSession(false);
    }
  };

  const getScoreBadgeColor = (score: number) => {
    if (score < 70) return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
    if (score < 85) return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
    return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="text-center space-y-3">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Upload Resume & Discover <span className="bg-clip-text text-transparent bg-gradient-to-r from-accent-violetGlow to-accent-cyan">Matched Roles</span>
        </h1>
        <p className="text-sm sm:text-base text-slate-300 max-w-xl mx-auto">
          Upload your resume to extract candidate skills and get AI-matched target role recommendations with 1-click mock interview startup.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm text-center">
          {error}
        </div>
      )}

      {/* Upload Form & AI Profile Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
        {/* Upload Form */}
        <div className="glass-panel p-6 sm:p-8 space-y-6">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Briefcase className="w-4 h-4 text-accent-cyan" />
              <span>Target Role (or select from recommendations below)</span>
            </label>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              placeholder="e.g. Senior Backend Developer, AI Engineer"
              className="glass-input w-full text-sm"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <FileText className="w-4 h-4 text-accent-violetGlow" />
              <span>Resume File (PDF / DOCX)</span>
            </label>

            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              className="border-2 border-dashed border-white/15 hover:border-accent-violet/50 rounded-2xl p-8 text-center bg-white/[0.02] hover:bg-white/[0.05] transition-all cursor-pointer relative group"
            >
              <input
                type="file"
                accept=".pdf,.docx,.doc"
                onChange={handleFileChange}
                className="absolute inset-0 opacity-0 cursor-pointer"
              />
              <div className="flex flex-col items-center gap-3">
                <div className="w-14 h-14 rounded-2xl bg-accent-violet/10 border border-accent-violet/30 flex items-center justify-center text-accent-violetGlow group-hover:scale-110 transition-transform">
                  <UploadCloud className="w-7 h-7" />
                </div>
                {file ? (
                  <div className="flex items-center gap-2 text-sm text-accent-cyan font-medium">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{file.name}</span>
                  </div>
                ) : (
                  <div>
                    <p className="text-sm font-medium text-slate-200">
                      Click to upload or drag & drop
                    </p>
                    <p className="text-xs text-slate-400 mt-1">PDF or DOCX (Max 10MB)</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          <button
            onClick={handleUploadResume}
            disabled={uploading || !file}
            className="glass-button-primary w-full py-3.5 flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {uploading ? (
              <span className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 animate-spin text-accent-cyan" />
                Analyzing Resume & Matching Roles...
              </span>
            ) : (
              <span>Analyze Resume & Match Roles</span>
            )}
          </button>
        </div>

        {/* AI Candidate Profile Summary */}
        <div className="glass-panel p-6 sm:p-8 space-y-6 min-h-[380px] flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-white/10">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-accent-cyan" />
                <span>AI Candidate Profile</span>
              </h3>
              {resumeData && (
                <span className="px-3 py-1 rounded-full text-xs font-mono font-semibold bg-accent-violet/20 border border-accent-violet/40 text-accent-violetGlow">
                  {resumeData.seniority}
                </span>
              )}
            </div>

            {resumeData ? (
              <div className="mt-6 space-y-5">
                <div className="space-y-2">
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5 text-accent-cyan" />
                    <span>Detected Skills</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(resumeData.parsed_json.skills || []).map((skill: string, idx: number) => (
                      <span
                        key={idx}
                        className="px-2.5 py-1 rounded-lg bg-white/5 border border-white/10 text-xs text-slate-200"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Award className="w-3.5 h-3.5 text-accent-emerald" />
                    <span>Experience Summary</span>
                  </div>
                  <p className="text-sm text-slate-300">
                    Estimated {resumeData.parsed_json.years_experience || '3+'} years of experience across past roles:{' '}
                    <span className="text-white font-medium">
                      {(resumeData.parsed_json.past_roles || []).join(', ') || 'Software Engineer'}
                    </span>
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center text-center h-48 text-slate-400 space-y-2">
                <FileText className="w-10 h-10 opacity-30 text-accent-cyan" />
                <p className="text-sm">Upload your resume to view AI parsed skills and profile estimate</p>
              </div>
            )}
          </div>

          {resumeData && (
            <button
              onClick={() => handleStartInterview(targetRole)}
              disabled={startingSession}
              className="glass-button-primary w-full py-4 flex items-center justify-center gap-2 mt-6 shadow-xl shadow-accent-violet/30"
            >
              {startingSession && startingRoleTitle === targetRole ? (
                <span>Generating Question Queue for {targetRole}...</span>
              ) : (
                <>
                  <span>Practice for "{targetRole}"</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* NEW SECTION: AI Recommended Job Roles Grid */}
      {jobMatches && jobMatches.recommended_roles && (
        <div className="space-y-6 pt-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <Target className="w-6 h-6 text-accent-cyan" />
                <span>AI Recommended Job Roles</span>
              </h2>
              <p className="text-sm text-slate-400">
                Ranked role recommendations tailored to your resume's skill set and career trajectory.
              </p>
            </div>
            <span className="text-xs font-mono text-slate-400">
              {jobMatches.recommended_roles.length} Roles Identified
            </span>
          </div>

          {/* Market Positioning Summary Banner */}
          {jobMatches.summary && (
            <div className="glass-panel p-5 border-l-4 border-l-accent-cyan space-y-1">
              <span className="text-xs font-mono font-bold text-accent-cyan uppercase">Market Positioning Overview</span>
              <p className="text-sm text-slate-200 leading-relaxed">{jobMatches.summary}</p>
            </div>
          )}

          {/* Grid of Recommended Role Glass Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {jobMatches.recommended_roles.map((role: RecommendedRoleData, idx: number) => {
              const isExpanded = expandedRoleIdx === idx;
              const isLaunchingThis = startingSession && startingRoleTitle === role.title;

              return (
                <div
                  key={idx}
                  className="glass-panel-interactive p-6 space-y-4 flex flex-col justify-between shadow-xl"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-1">
                        <h3 className="text-lg font-bold text-white leading-snug">{role.title}</h3>
                        <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-mono uppercase bg-white/5 border border-white/10 text-slate-300">
                          {role.seniority_fit}
                        </span>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-xs font-extrabold border shrink-0 ${getScoreBadgeColor(role.match_score)}`}>
                        {role.match_score}% Match
                      </div>
                    </div>

                    <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                      {role.reasoning}
                    </p>

                    {/* Expandable Skills vs Skill Gaps */}
                    <div className="space-y-2 pt-2">
                      <button
                        onClick={() => setExpandedRoleIdx(isExpanded ? null : idx)}
                        className="text-xs font-semibold text-accent-cyan hover:underline flex items-center gap-1"
                      >
                        <span>{isExpanded ? 'Hide Skill Breakdown' : 'View Matching Skills & Gaps'}</span>
                        {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                      </button>

                      {isExpanded && (
                        <div className="space-y-3 p-3 rounded-xl bg-white/5 border border-white/10 text-xs">
                          <div>
                            <span className="block font-semibold text-emerald-400 mb-1">Matching Skills:</span>
                            <div className="flex flex-wrap gap-1.5">
                              {role.matching_skills.map((s, sIdx) => (
                                <span key={sIdx} className="px-2 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-[11px]">
                                  {s}
                                </span>
                              ))}
                            </div>
                          </div>

                          <div>
                            <span className="block font-semibold text-rose-400 mb-1">Skill Gaps:</span>
                            <div className="flex flex-wrap gap-1.5">
                              {role.skill_gaps.map((g, gIdx) => (
                                <span key={gIdx} className="px-2 py-0.5 rounded bg-rose-500/10 border border-rose-500/20 text-rose-300 text-[11px]">
                                  {g}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      setTargetRole(role.title);
                      handleStartInterview(role.title);
                    }}
                    disabled={startingSession}
                    className="glass-button-primary w-full py-2.5 text-xs flex items-center justify-center gap-2 mt-4"
                  >
                    {isLaunchingThis ? (
                      <span>Starting Interview for {role.title}...</span>
                    ) : (
                      <>
                        <span>Practice for this Role</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
