"use client";

import { useState } from "react";
import { CopilotPopup } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";
import { MessageCircle, X, Minimize2, Maximize2, Sparkles } from "lucide-react";

interface CopilotChatSidebarProps {
  auditUrl?: string;
  currentScore?: number;
  maxScore?: number;
}

export default function CopilotChatSidebar({
  auditUrl,
  currentScore,
  maxScore,
}: CopilotChatSidebarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);

  const suggestedQuestions = [
    "What should I fix first?",
    "Why is my AEO score low?",
    "How do I beat my competitors?",
    "Explain my overall score",
    "Show me quick wins",
    "What's the easiest issue to fix?",
  ];

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full shadow-2xl hover:shadow-3xl hover:scale-105 transition-all duration-300 group"
        aria-label="Open SEO Assistant"
      >
        <Sparkles className="w-5 h-5 animate-pulse" />
        <span className="font-semibold">Ask SEO Assistant</span>
        <MessageCircle className="w-5 h-5 group-hover:scale-110 transition-transform" />
      </button>
    );
  }

  return (
    <>
      {/* Mobile: Full screen overlay */}
      <div className="fixed inset-0 z-50 md:hidden bg-white dark:bg-gray-900 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-600 to-purple-600">
          <div className="flex items-center gap-2 text-white">
            <Sparkles className="w-5 h-5" />
            <h2 className="font-semibold">SEO Assistant</h2>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            aria-label="Close chat"
          >
            <X className="w-5 h-5 text-white" />
          </button>
        </div>

        {/* Context Info */}
        {auditUrl && (
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border-b border-blue-200 dark:border-blue-800">
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Analyzing: <span className="font-semibold">{auditUrl}</span>
            </p>
            {currentScore !== undefined && maxScore !== undefined && (
              <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                Current Score: <span className="font-semibold">{currentScore}/{maxScore}</span>
              </p>
            )}
          </div>
        )}

        {/* Suggested Questions */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
            Suggested Questions
          </p>
          <div className="grid grid-cols-2 gap-2">
            {suggestedQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => {
                  // This will trigger the chat input with the question
                  const event = new CustomEvent("copilotkit:send-message", {
                    detail: { message: question },
                  });
                  window.dispatchEvent(event);
                }}
                className="text-left text-xs px-3 py-2 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg transition-colors text-gray-700 dark:text-gray-300"
              >
                {question}
              </button>
            ))}
          </div>
        </div>

        {/* Chat Interface */}
        <div className="flex-1 overflow-hidden">
          <CopilotPopup
            labels={{
              title: "SEO Assistant",
              initial: "Hi! I'm your SEO assistant. I can help you understand your audit results and prioritize improvements. What would you like to know?",
            }}
            instructions={`You are an expert SEO consultant helping users understand and improve their website's search engine optimization.

You have access to their complete audit results including:
- Overall score and grade
- SEO, AEO (Answer Engine Optimization), and GEO (Generative Engine Optimization) scores
- Detailed issues categorized by severity
- Quick wins and improvement opportunities

Your role:
1. Explain SEO concepts in clear, non-technical language
2. Prioritize actionable recommendations
3. Provide step-by-step guidance for fixes
4. Help users understand competitive positioning
5. Focus on practical, implementable advice

Communication style:
- Friendly and encouraging
- Use emojis sparingly but effectively
- Break complex topics into digestible pieces
- Always provide specific, actionable next steps
- Celebrate improvements and progress

When users ask questions:
- Use the available CopilotKit actions to provide detailed, data-driven answers
- Reference specific scores and issues from their audit
- Prioritize based on their goals (quick wins, max impact, or easy fixes)
- Provide code examples when appropriate
- Explain the "why" behind recommendations

Remember: You're helping small business owners who may not be SEO experts. Be patient, clear, and practical.`}
          />
        </div>
      </div>

      {/* Desktop: Sidebar */}
      <div className="hidden md:block">
        <div
          className={`fixed top-0 right-0 h-full z-50 bg-white dark:bg-gray-900 shadow-2xl transition-all duration-300 ${
            isMinimized ? "w-16" : "w-[400px]"
          } border-l border-gray-200 dark:border-gray-700`}
        >
          {isMinimized ? (
            // Minimized State
            <div className="flex flex-col items-center p-4 space-y-4">
              <button
                onClick={() => setIsMinimized(false)}
                className="p-3 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors group"
                aria-label="Maximize chat"
              >
                <Maximize2 className="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-blue-600" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-3 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors group"
                aria-label="Close chat"
              >
                <X className="w-5 h-5 text-gray-600 dark:text-gray-400 group-hover:text-red-600" />
              </button>
              <div className="flex-1 flex items-center">
                <Sparkles className="w-6 h-6 text-blue-600 animate-pulse" />
              </div>
            </div>
          ) : (
            // Expanded State
            <div className="flex flex-col h-full">
              {/* Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-600 to-purple-600">
                <div className="flex items-center gap-2 text-white">
                  <Sparkles className="w-5 h-5" />
                  <h2 className="font-semibold">SEO Assistant</h2>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setIsMinimized(true)}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                    aria-label="Minimize chat"
                  >
                    <Minimize2 className="w-4 h-4 text-white" />
                  </button>
                  <button
                    onClick={() => setIsOpen(false)}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                    aria-label="Close chat"
                  >
                    <X className="w-4 h-4 text-white" />
                  </button>
                </div>
              </div>

              {/* Context Info */}
              {auditUrl && (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border-b border-blue-200 dark:border-blue-800">
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Analyzing: <span className="font-semibold truncate block">{auditUrl}</span>
                  </p>
                  {currentScore !== undefined && maxScore !== undefined && (
                    <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                      Score: <span className="font-semibold">{currentScore}/{maxScore}</span>
                    </p>
                  )}
                </div>
              )}

              {/* Suggested Questions */}
              <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-3">
                  Quick Questions
                </p>
                <div className="space-y-2">
                  {suggestedQuestions.slice(0, 4).map((question, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        const event = new CustomEvent("copilotkit:send-message", {
                          detail: { message: question },
                        });
                        window.dispatchEvent(event);
                      }}
                      className="w-full text-left text-sm px-3 py-2 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600 hover:border-blue-400"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>

              {/* Chat Interface */}
              <div className="flex-1 overflow-hidden">
                <CopilotPopup
                  labels={{
                    title: "SEO Assistant",
                    initial: "Hi! 👋 I'm your SEO assistant. I've analyzed your audit results and I'm here to help you improve your rankings.\n\nYou can ask me anything about:\n• Your scores and what they mean\n• Which issues to fix first\n• How to implement specific fixes\n• Competitive analysis\n• AEO and GEO optimization\n\nWhat would you like to know?",
                  }}
                  instructions={`You are an expert SEO consultant helping users understand and improve their website's search engine optimization.

You have access to their complete audit results including:
- Overall score and grade
- SEO, AEO (Answer Engine Optimization), and GEO (Generative Engine Optimization) scores
- Detailed issues categorized by severity
- Quick wins and improvement opportunities

Your role:
1. Explain SEO concepts in clear, non-technical language
2. Prioritize actionable recommendations
3. Provide step-by-step guidance for fixes
4. Help users understand competitive positioning
5. Focus on practical, implementable advice

Communication style:
- Friendly and encouraging
- Use emojis sparingly but effectively (✅ 🎯 💡 ⚡ 🚀)
- Break complex topics into digestible pieces
- Always provide specific, actionable next steps
- Celebrate improvements and progress

When users ask questions:
- Use the available CopilotKit actions (explainScore, prioritizeIssues, generateFixInstructions, compareToCompetitors) to provide detailed, data-driven answers
- Reference specific scores and issues from their audit
- Prioritize based on their goals (quick wins, max impact, or easy fixes)
- Provide code examples when appropriate
- Explain the "why" behind recommendations

Example responses:
- "Your AEO score is 18/25 (72%). You're doing well but missing FAQ schema. Let me show you how to add it..."
- "I recommend starting with these 3 quick wins that will boost your score by 12 points..."
- "Here's why your competitor is ranking higher and exactly how to catch up..."

Remember: You're helping small business owners who may not be SEO experts. Be patient, clear, and practical. Focus on ROI and business impact.`}
                />
              </div>

              {/* Footer */}
              <div className="p-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                <p className="text-xs text-center text-gray-500 dark:text-gray-400">
                  Powered by AI • Always verify recommendations
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
