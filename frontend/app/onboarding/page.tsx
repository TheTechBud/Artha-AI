"use client";

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { useUploadTransactions } from "@/hooks/useTransactions";

const STEPS = ["Welcome", "Upload", "Ready"];

export default function OnboardingPage() {
  const [step, setStep] = useState(0);
  const [dragging, setDragging] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const upload = useUploadTransactions();
  const router = useRouter();

  const handleFile = (file: File) => {
    upload.mutate(file, {
      onSuccess: () => setStep(2),
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-lg w-full">
        {/* Step indicator */}
        <div className="flex items-center gap-2 mb-8 justify-center">
          {STEPS.map((s, i) => (
            <div key={s} className="flex items-center gap-2">
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium transition-all ${
                  i < step ? "bg-teal-500 text-white" :
                  i === step ? "bg-teal-500/20 text-teal-400 ring-1 ring-teal-500/50" :
                  "bg-white/5 text-muted"
                }`}
              >
                {i < step ? "✓" : i + 1}
              </div>
              {i < STEPS.length - 1 && (
                <div className={`w-12 h-px ${i < step ? "bg-teal-500" : "bg-border"}`} />
              )}
            </div>
          ))}
        </div>

        {/* Step 0: Welcome */}
        {step === 0 && (
          <div className="card text-center space-y-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-teal-500 to-teal-700 flex items-center justify-center text-3xl mx-auto">
              A
            </div>
            <div>
              <h1 className="text-2xl font-semibold text-white mb-2">Welcome to Artha AI</h1>
              <p className="text-muted text-sm leading-relaxed">
                Your behavioral finance copilot. Artha analyzes your spending patterns,
                detects risk signals, and gives you AI-powered guidance to make better
                financial decisions.
              </p>
            </div>
            <div className="grid grid-cols-3 gap-3 text-left">
              {[
                { icon: "◎", label: "DRS Score", desc: "Real-time financial health metric" },
                { icon: "⚡", label: "Interventions", desc: "AI actions tailored to your patterns" },
                { icon: "✦", label: "Narrative", desc: "Weekly stories about your money" },
              ].map((f) => (
                <div key={f.label} className="bg-white/3 rounded-xl p-3 border border-border">
                  <span className="text-teal-400 text-lg">{f.icon}</span>
                  <p className="text-xs font-medium text-white mt-1">{f.label}</p>
                  <p className="text-xs text-muted mt-0.5 leading-relaxed">{f.desc}</p>
                </div>
              ))}
            </div>
            <button
              onClick={() => setStep(1)}
              className="w-full py-2.5 bg-teal-500 text-white rounded-xl font-medium hover:bg-teal-400 transition-colors"
            >
              Get Started
            </button>
          </div>
        )}

        {/* Step 1: Upload */}
        {step === 1 && (
          <div className="card space-y-6">
            <div>
              <h2 className="text-lg font-semibold text-white">Upload your transactions</h2>
              <p className="text-sm text-muted mt-1">
                Upload a CSV file with your bank transactions. We'll analyze the patterns
                and calculate your DRS score.
              </p>
            </div>

            {/* Drop zone */}
            <div
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragging(false);
                const f = e.dataTransfer.files[0];
                if (f) handleFile(f);
              }}
              onClick={() => fileRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${
                dragging
                  ? "border-teal-500 bg-teal-500/5"
                  : "border-border hover:border-white/30 hover:bg-white/3"
              }`}
            >
              <input
                ref={fileRef}
                type="file"
                accept=".csv"
                className="hidden"
                onChange={(e) => { if (e.target.files?.[0]) handleFile(e.target.files[0]); }}
              />
              {upload.isPending ? (
                <div className="space-y-2">
                  <div className="w-8 h-8 border-2 border-teal-500 border-t-transparent rounded-full animate-spin mx-auto" />
                  <p className="text-sm text-teal-400">Processing transactions…</p>
                </div>
              ) : (
                <>
                  <p className="text-3xl mb-3">↑</p>
                  <p className="text-sm text-white font-medium">Drop CSV here or click to browse</p>
                  <p className="text-xs text-muted mt-1">
                    Columns: date, description, amount, type (debit/credit)
                  </p>
                </>
              )}
            </div>

            <div className="flex items-center gap-3">
              <div className="flex-1 h-px bg-border" />
              <span className="text-xs text-muted">or</span>
              <div className="flex-1 h-px bg-border" />
            </div>

            <button
              onClick={() => router.push("/dashboard")}
              className="w-full py-2.5 bg-white/5 text-muted rounded-xl text-sm hover:text-white hover:bg-white/8 transition-colors"
            >
              Skip — explore with sample data
            </button>
          </div>
        )}

        {/* Step 2: Ready */}
        {step === 2 && (
          <div className="card text-center space-y-6">
            <div className="w-16 h-16 rounded-2xl bg-teal-500/15 border border-teal-500/30 flex items-center justify-center text-3xl mx-auto">
              ✓
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">You're all set!</h2>
              <p className="text-sm text-muted mt-1">
                Transactions imported. Your DRS score and analysis are ready.
              </p>
            </div>
            <button
              onClick={() => router.push("/dashboard")}
              className="w-full py-2.5 bg-teal-500 text-white rounded-xl font-medium hover:bg-teal-400 transition-colors"
            >
              Go to Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
