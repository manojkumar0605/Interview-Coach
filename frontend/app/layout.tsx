import './globals.css';
import type { Metadata } from 'next';
import Navbar from '@/components/Navbar';

export const metadata: Metadata = {
  title: 'AI Interview Coach — Master Your Technical & Behavioral Interviews',
  description: 'AI-powered mock interviews, instant answer scoring, weak topic tracking, and personalized study plans driven by OpenRouter.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased selection:bg-accent-violet/30 selection:text-accent-violetGlow min-h-screen flex flex-col">
        {/* Ambient Dark Gradient Background with Soft Glowing Orbs */}
        <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
          <div className="absolute -top-[20%] -left-[10%] w-[600px] h-[600px] rounded-full bg-accent-violet/15 blur-[130px] animate-float-slow" />
          <div className="absolute top-[40%] -right-[15%] w-[700px] h-[700px] rounded-full bg-accent-cyan/15 blur-[150px] animate-float-reverse" />
          <div className="absolute -bottom-[20%] left-[20%] w-[800px] h-[800px] rounded-full bg-indigo-900/20 blur-[160px] animate-pulse-glow" />
        </div>

        {/* Global Navigation Header */}
        <Navbar />

        {/* Main Content Body */}
        <main className="flex-1 relative z-10 pt-28 pb-16 px-4 sm:px-8 max-w-7xl mx-auto w-full">
          {children}
        </main>
      </body>
    </html>
  );
}
