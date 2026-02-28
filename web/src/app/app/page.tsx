'use client';

import { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send, Bot, User as UserIcon, Loader2, Sparkles, Zap, Clock, ChevronRight,
  BarChart3, CheckCircle2, AlertCircle, ArrowRight, Plus, X, MessageSquare,
  Trash2, MoreHorizontal, Play, Cpu,
} from 'lucide-react';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import { api } from '@/lib/api';
import { useAuthStore } from '@/stores/authStore';
import { formatDate } from '@/lib/utils';
import type { Workflow, Approval } from '@/types';

// --- Types ---

interface StepEvent {
  index: number;
  label: string;
  status: 'running' | 'done' | 'error';
  detail?: string;
  workflow_name?: string;
  workflow_id?: string;
  workflow_steps?: { type: string; label: string; requires?: string | null; connected?: boolean; requirement_description?: string }[];
  summary?: string;
  missing_connections?: string[];
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  steps?: StepEvent[];
  metadata?: any;
}

interface Conversation {
  id: string;
  title: string;
  updated_at: string;
  message_count: number;
  last_message?: string;
}

// --- Markdown renderer ---

function renderMessageContent(content: string) {
  const paragraphs = content.split(/\n\n+/);
  return (
    <div className="space-y-2">
      {paragraphs.map((para, pi) => {
        const trimmed = para.trim();
        if (!trimmed) return null;
        const listItems = trimmed.split('\n').filter(l => /^\d+\.\s/.test(l.trim()));
        if (listItems.length > 1) {
          return (
            <ol key={pi} className="space-y-1.5 my-1">
              {listItems.map((item, li) => {
                const text = item.replace(/^\d+\.\s*/, '');
                return (
                  <li key={li} className="flex items-start gap-2.5">
                    <span className="flex-shrink-0 w-5 h-5 rounded-full bg-primary-100 text-primary-700 text-xs font-semibold flex items-center justify-center mt-0.5">
                      {li + 1}
                    </span>
                    <span className="text-sm leading-relaxed">{renderInline(text)}</span>
                  </li>
                );
              })}
            </ol>
          );
        }
        const bullets = trimmed.split('\n').filter(l => /^[-•]\s/.test(l.trim()));
        if (bullets.length > 1) {
          return (
            <ul key={pi} className="space-y-1 my-1">
              {bullets.map((item, li) => (
                <li key={li} className="flex items-start gap-2">
                  <span className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-primary-400 mt-2" />
                  <span className="text-sm leading-relaxed">{renderInline(item.replace(/^[-•]\s*/, ''))}</span>
                </li>
              ))}
            </ul>
          );
        }
        return <p key={pi} className="text-sm leading-relaxed">{renderInline(trimmed)}</p>;
      })}
    </div>
  );
}

function renderInline(text: string) {
  const parts = text.split(/(\*\*.*?\*\*|\*.*?\*|\[.*?\]\(.*?\)|`[^`]+`)/g);
  return parts.map((part, i) => {
    const boldMatch = part.match(/^\*\*(.*?)\*\*$/);
    if (boldMatch) return <strong key={i} className="font-semibold">{boldMatch[1]}</strong>;
    const italicMatch = part.match(/^\*(.*?)\*$/);
    if (italicMatch) return <em key={i}>{italicMatch[1]}</em>;
    const linkMatch = part.match(/^\[(.*?)\]\((.*?)\)$/);
    if (linkMatch) return <Link key={i} href={linkMatch[2]} className="text-primary-600 underline underline-offset-2 font-medium hover:text-primary-800">{linkMatch[1]}</Link>;
    const codeMatch = part.match(/^`([^`]+)`$/);
    if (codeMatch) return <code key={i} className="px-1.5 py-0.5 bg-gray-200 rounded text-xs font-mono">{codeMatch[1]}</code>;
    return <span key={i}>{part}</span>;
  });
}

// --- Step Progress ---

function StepProgress({ steps }: { steps: StepEvent[] }) {
  return (
    <div className="space-y-2 py-1">
      {steps.map((step, i) => (
        <div key={i}>
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2 }}
            className={`flex items-center gap-2.5 px-3 py-2 rounded-lg ${
              step.status === 'running' ? 'bg-primary-50 border border-primary-100' :
              step.status === 'done' ? 'bg-green-50 border border-green-100' :
              'bg-red-50 border border-red-100'
            }`}
          >
            <div className="flex-shrink-0">
              {step.status === 'running' && <Loader2 className="w-4 h-4 text-primary-500 animate-spin" />}
              {step.status === 'done' && <CheckCircle2 className="w-4 h-4 text-green-500" />}
              {step.status === 'error' && <X className="w-4 h-4 text-red-500" />}
            </div>
            <div className="flex-1 min-w-0">
              <span className={`text-sm font-medium ${
                step.status === 'running' ? 'text-primary-700' :
                step.status === 'done' ? 'text-green-700' :
                'text-red-700'
              }`}>
                {step.label?.startsWith('Agent:') && (
                  <Cpu className="w-3.5 h-3.5 inline mr-1 -mt-0.5" />
                )}
                {step.label}
              </span>
              {step.detail && !step.workflow_steps && (
                <span className="text-xs text-gray-500 ml-1.5">• {step.detail}</span>
              )}
            </div>
          </motion.div>
          {step.status === 'done' && step.workflow_steps && step.workflow_steps.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1 }}
              className="mt-2 bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm"
            >
              <div className="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-semibold text-gray-900">{step.workflow_name}</h4>
                  {step.summary && <p className="text-xs text-gray-500 mt-0.5">{step.summary}</p>}
                </div>
                <span className="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-500 font-medium">Draft</span>
              </div>
              {/* Steps with connection status */}
              <div className="px-4 py-3 space-y-2">
                {step.workflow_steps.map((ws, si) => (
                  <div key={si} className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-primary-100 text-primary-600 text-[10px] font-bold flex items-center justify-center flex-shrink-0">
                      {si + 1}
                    </span>
                    <span className="text-sm text-gray-700 font-medium flex-1">{ws.label}</span>
                    {ws.requires ? (
                      ws.connected ? (
                        <span className="flex items-center gap-1 text-xs text-green-600">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          {ws.requires}
                        </span>
                      ) : (
                        <Link href="/app/connections" className="flex items-center gap-1 text-xs text-amber-600 hover:text-amber-700 font-medium">
                          <AlertCircle className="w-3.5 h-3.5" />
                          Connect {ws.requires}
                        </Link>
                      )
                    ) : (
                      <span className="text-xs text-gray-400">Built-in</span>
                    )}
                  </div>
                ))}
              </div>
              {/* Missing connections banner */}
              {step.missing_connections && step.missing_connections.length > 0 && (
                <div className="px-4 py-3 border-t border-amber-100 bg-amber-50">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-xs font-medium text-amber-800">
                        Connect {step.missing_connections.join(', ')} to activate this workflow
                      </p>
                      <Link href="/app/connections" className="text-xs text-amber-600 hover:text-amber-700 font-medium underline underline-offset-2 mt-0.5 inline-block">
                        Go to Connections →
                      </Link>
                    </div>
                  </div>
                </div>
              )}
              {step.workflow_id && (
                <div className="px-4 py-2.5 border-t border-gray-100 bg-gray-50">
                  <Link href={`/app/workflows/${step.workflow_id}`} className="text-xs text-primary-600 font-medium hover:text-primary-800 flex items-center gap-1">
                    View & edit workflow <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              )}
            </motion.div>
          )}
        </div>
      ))}
    </div>
  );
}

// --- Thinking Indicator ---
function ThinkingIndicator({ text }: { text: string }) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-2 text-sm text-gray-400">
      <Loader2 className="w-3.5 h-3.5 animate-spin" />
      <span>{text}</span>
    </motion.div>
  );
}

// --- Suggestions ---
const SUGGESTIONS = [
  { text: 'Create a booking & deposit workflow', icon: <Zap size={14} /> },
  { text: 'Set up automatic lead follow-ups', icon: <Sparkles size={14} /> },
  { text: 'Send a test reminder to confirm an appointment', icon: <Play size={14} /> },
  { text: 'Show me my active workflows', icon: <CheckCircle2 size={14} /> },
];

// =====================
// MAIN COMPONENT
// =====================

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentThinking, setCurrentThinking] = useState<string | null>(null);
  const [currentSteps, setCurrentSteps] = useState<StepEvent[]>([]);

  // Conversations
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConvoId, setActiveConvoId] = useState<string | null>(null);
  const [convosLoading, setConvosLoading] = useState(true);

  // Right sidebar
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [sidebarLoading, setSidebarLoading] = useState(true);
  const [deleteConvoTarget, setDeleteConvoTarget] = useState<string | null>(null);
  const [connections, setConnections] = useState<any[]>([]);
  const [knowledgeCount, setKnowledgeCount] = useState(0);
  const [gettingStartedDismissed, setGettingStartedDismissed] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const firstName = user?.full_name?.split(' ')[0] || 'there';

  useEffect(() => {
    loadConversations();
    loadSidebarData();
    checkOnboardingContext();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentSteps, currentThinking]);

  const loadConversations = async () => {
    try {
      const convos = await api.request<Conversation[]>('/api/chat/conversations', { method: 'GET' });
      if (convos && Array.isArray(convos)) {
        setConversations(convos);
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
    } finally {
      setConvosLoading(false);
    }
  };

  const loadConversationMessages = async (convoId: string) => {
    setActiveConvoId(convoId);
    try {
      const msgs = await api.request<any[]>(`/api/chat/conversations/${convoId}/messages`, { method: 'GET' });
      if (msgs && Array.isArray(msgs)) {
        setMessages(msgs.map((m: any) => ({
          role: m.role as 'user' | 'assistant',
          content: m.content,
          timestamp: new Date(m.timestamp),
          steps: m.metadata?.steps || undefined,
        })));
      }
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  const startNewConversation = () => {
    setActiveConvoId(null);
    setMessages([]);
    inputRef.current?.focus();
  };

  const deleteConversation = async (convoId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setDeleteConvoTarget(convoId);
  };

  const confirmDeleteConversation = async () => {
    if (!deleteConvoTarget) return;
    try {
      await api.request(`/api/chat/conversations/${deleteConvoTarget}`, { method: 'DELETE' });
      setConversations(prev => prev.filter(c => c.id !== deleteConvoTarget));
      if (activeConvoId === deleteConvoTarget) {
        startNewConversation();
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    } finally {
      setDeleteConvoTarget(null);
    }
  };

  const loadSidebarData = async () => {
    try {
      const [wf, ap] = await Promise.all([api.getWorkflows(), api.getApprovals('pending')]);
      setWorkflows(wf);
      setApprovals(ap);
      // Load connections and knowledge for getting started
      try {
        const conns = await api.getConnections();
        setConnections(conns.filter((c: any) => c.is_connected));
      } catch { setConnections([]); }
      try {
        const kb = await api.request<any[]>('/api/knowledge/', { method: 'GET' });
        setKnowledgeCount(Array.isArray(kb) ? kb.length : 0);
      } catch { setKnowledgeCount(0); }
      // Check if dismissed
      try {
        const dismissed = localStorage.getItem('aivaro_getting_started_dismissed');
        if (dismissed) setGettingStartedDismissed(true);
      } catch {}
    } catch (err) {
      console.error('Failed to load sidebar:', err);
    } finally {
      setSidebarLoading(false);
    }
  };

  const checkOnboardingContext = () => {
    try {
      const ctxStr = localStorage.getItem('aivaro_onboarding_context');
      if (!ctxStr) return;
      
      const ctx = JSON.parse(ctxStr);
      const wfStr = localStorage.getItem('aivaro_onboarding_workflow');
      const wf = wfStr ? JSON.parse(wfStr) : null;
      
      // Clear immediately so it only fires once
      localStorage.removeItem('aivaro_onboarding_context');
      localStorage.removeItem('aivaro_onboarding_workflow');
      
      // Build a contextual welcome message
      let welcomeMsg = '';
      if (wf) {
        welcomeMsg = `I just set up my ${ctx.businessType || ''} business and created a "${wf.name}" workflow during onboarding. Can you walk me through what I need to do to get it running?`;
      } else if (ctx.selectedWorkflow === 'custom' && ctx.customPrompt) {
        welcomeMsg = ctx.customPrompt;
      } else if (ctx.businessType) {
        welcomeMsg = `I just set up my ${ctx.businessType} business. What workflows would you recommend to get started?`;
      }
      
      if (welcomeMsg) {
        // Small delay to let the UI mount
        setTimeout(() => handleSend(welcomeMsg), 500);
      }
    } catch (err) {
      console.error('Failed to parse onboarding context:', err);
    }
  };

  const handleSend = async (text?: string) => {
    const message = text || input.trim();
    if (!message || isLoading) return;

    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: message, timestamp: new Date() }]);
    setIsLoading(true);
    setCurrentThinking(null);
    setCurrentSteps([]);

    try {
      const token = api.getToken();
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      const response = await fetch(`${apiUrl}/api/chat/assistant/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ message, conversation_id: activeConvoId }),
      });

      if (!response.ok || !response.body) throw new Error(`Stream failed: ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let collectedSteps: StepEvent[] = [];
      let finalMessage = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const event = JSON.parse(line.slice(6));
            if (event.type === 'conversation') {
              // Server created/confirmed conversation
              if (event.conversation_id && !activeConvoId) {
                setActiveConvoId(event.conversation_id);
              }
            } else if (event.type === 'thinking' || event.type === 'agent_thinking') {
              setCurrentThinking(event.content);
            } else if (event.type === 'step') {
              setCurrentThinking(null);
              setCurrentSteps(prev => {
                const updated = [...prev];
                const existing = updated.findIndex(s => s.index === event.index);
                if (existing >= 0) updated[existing] = event;
                else updated.push(event);
                collectedSteps = updated;
                return updated;
              });
            } else if (event.type === 'agent_message') {
              // Agent reasoning — show as thinking text
              setCurrentThinking(event.content);
            } else if (event.type === 'agent_escalate') {
              setCurrentThinking(null);
              const escalateStep = {
                index: collectedSteps.length,
                label: `Needs input: ${event.question || event.reason}`,
                status: 'error' as const,
                detail: event.reason,
              };
              setCurrentSteps(prev => {
                const updated = [...prev, escalateStep];
                collectedSteps = updated;
                return updated;
              });
            } else if (event.type === 'message') {
              finalMessage = event.content;
            } else if (event.type === 'done') {
              setCurrentThinking(null);
              setCurrentSteps([]);
              setMessages(prev => [...prev, {
                role: 'assistant',
                content: finalMessage,
                timestamp: new Date(),
                steps: collectedSteps.length > 0 ? collectedSteps : undefined,
              }]);
              loadSidebarData();
              loadConversations(); // Refresh conversation list
            }
          } catch {}
        }
      }
    } catch (err) {
      console.error('Chat error:', err);
      setCurrentThinking(null);
      setCurrentSteps([]);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Something went wrong. Make sure the backend is running and try again.",
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="h-[calc(100vh-64px)] flex">
      {/* Left: Conversation List */}
      <div className="w-64 flex-shrink-0 border-r border-gray-200 bg-gray-50 flex flex-col hidden lg:flex">
        <div className="p-3 border-b border-gray-200">
          <button
            onClick={startNewConversation}
            className="w-full flex items-center gap-2 px-3 py-2.5 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition"
          >
            <Plus className="w-4 h-4" />
            New conversation
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {convosLoading ? (
            <div className="p-4 text-center text-sm text-gray-400">Loading...</div>
          ) : conversations.length === 0 ? (
            <div className="p-4 text-center text-sm text-gray-400">
              No conversations yet.<br />Start one above!
            </div>
          ) : (
            <div className="py-1">
              {conversations.map((c) => (
                <button
                  key={c.id}
                  onClick={() => loadConversationMessages(c.id)}
                  className={`w-full text-left px-3 py-2.5 flex items-start gap-2.5 hover:bg-gray-100 transition group ${
                    activeConvoId === c.id ? 'bg-white border-r-2 border-primary-500' : ''
                  }`}
                >
                  <MessageSquare className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{c.title}</p>
                    {c.last_message && (
                      <p className="text-xs text-gray-400 truncate mt-0.5">{c.last_message}</p>
                    )}
                    <p className="text-xs text-gray-300 mt-0.5">{c.message_count} messages</p>
                  </div>
                  <button
                    onClick={(e) => deleteConversation(c.id, e)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 rounded transition flex-shrink-0"
                  >
                    <Trash2 className="w-3.5 h-3.5 text-gray-400" />
                  </button>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Center: Chat */}
      <div className="flex-1 flex flex-col min-w-0">
        {!hasMessages ? (
          <div className="flex-1 flex flex-col items-center justify-center px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center max-w-lg"
            >
              <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center shadow-lg">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Hey {firstName}, what should we automate?
              </h1>
              <p className="text-gray-500 mb-8">
                Describe what you need in plain English — I'll build and run it for you.
              </p>
              <div className="flex flex-wrap justify-center gap-2 mb-8">
                {SUGGESTIONS.map((s, i) => (
                  <motion.button
                    key={i}
                    onClick={() => handleSend(s.text)}
                    className="flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-200 rounded-full text-sm text-gray-700 hover:border-primary-400 hover:bg-primary-50 hover:text-primary-700 transition-all"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 + i * 0.08 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {s.icon}
                    {s.text}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto px-4 py-6">
            <div className="max-w-2xl mx-auto space-y-6">
              {messages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center flex-shrink-0 mt-1">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                  )}
                  <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    msg.role === 'user'
                      ? 'bg-primary-600 text-white rounded-br-md'
                      : 'bg-gray-100 text-gray-900 rounded-bl-md'
                  }`}>
                    {msg.steps && msg.steps.length > 0 && (
                      <div className="mb-1"><StepProgress steps={msg.steps} /></div>
                    )}
                    {msg.content && (
                      <div className={msg.steps ? 'mt-3 pt-3 border-t border-gray-200' : ''}>
                        {renderMessageContent(msg.content)}
                      </div>
                    )}
                    <p className={`text-xs mt-1.5 ${msg.role === 'user' ? 'text-primary-200' : 'text-gray-400'}`}>
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  {msg.role === 'user' && (
                    <div className="w-8 h-8 rounded-lg bg-gray-200 flex items-center justify-center flex-shrink-0 mt-1">
                      <UserIcon className="w-4 h-4 text-gray-600" />
                    </div>
                  )}
                </motion.div>
              ))}

              {isLoading && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3 max-w-[80%]">
                    {currentThinking && <ThinkingIndicator text={currentThinking} />}
                    {currentSteps.length > 0 && <StepProgress steps={currentSteps} />}
                    {!currentThinking && currentSteps.length === 0 && (
                      <div className="flex space-x-1.5">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>
          </div>
        )}

        {/* Input */}
        <div className="px-4 pb-4">
          <div className="max-w-2xl mx-auto">
            <div className="relative bg-white border border-gray-200 rounded-2xl shadow-sm focus-within:border-primary-400 focus-within:ring-2 focus-within:ring-primary-100 transition-all">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Tell Aivaro what to automate..."
                rows={1}
                className="w-full px-4 py-3.5 pr-12 text-sm text-gray-900 placeholder-gray-400 bg-transparent border-none outline-none resize-none"
                style={{ minHeight: 48, maxHeight: 120 }}
              />
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                className="absolute right-2 bottom-2 w-8 h-8 bg-primary-600 text-white rounded-lg flex items-center justify-center hover:bg-primary-700 disabled:opacity-30 disabled:hover:bg-primary-600 transition-all"
              >
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-xs text-gray-400 text-center mt-2">
              Aivaro can build workflows, check your data, and run automations.
            </p>
          </div>
        </div>
      </div>

      {/* Right Sidebar */}
      <div className="w-72 flex-shrink-0 border-l border-gray-200 bg-white overflow-y-auto hidden xl:block">
        <div className="p-5">
          {approvals.length > 0 && (
            <div className="mb-6">
              <Link href="/app/approvals">
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 hover:border-amber-300 transition">
                  <div className="flex items-center gap-2 mb-1">
                    <AlertCircle className="w-4 h-4 text-amber-600" />
                    <span className="text-sm font-semibold text-amber-900">
                      {approvals.length} pending approval{approvals.length !== 1 ? 's' : ''}
                    </span>
                  </div>
                  <p className="text-xs text-amber-700">Review before they can proceed</p>
                </div>
              </Link>
            </div>
          )}

          {/* Getting Started Checklist */}
          {!gettingStartedDismissed && !sidebarLoading && (() => {
            const steps = [
              { label: 'Connect an integration', done: connections.length > 0, href: '/app/connections', icon: <Zap className="w-3.5 h-3.5" /> },
              { label: 'Create your first workflow', done: workflows.length > 0, href: '/app/workflows', icon: <Plus className="w-3.5 h-3.5" /> },
              { label: 'Add business knowledge', done: knowledgeCount > 0, href: '/app/knowledge', icon: <Sparkles className="w-3.5 h-3.5" /> },
              { label: 'Run a workflow', done: workflows.some(w => w.is_active), href: '/app/workflows', icon: <Play className="w-3.5 h-3.5" /> },
              { label: 'Review an approval', done: false, href: '/app/approvals', icon: <CheckCircle2 className="w-3.5 h-3.5" /> },
            ];
            const doneCount = steps.filter(s => s.done).length;
            const allDone = doneCount === steps.length;
            
            return (
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-sm font-semibold text-gray-900">Getting Started</h3>
                  <button
                    onClick={() => {
                      setGettingStartedDismissed(true);
                      localStorage.setItem('aivaro_getting_started_dismissed', 'true');
                    }}
                    className="text-xs text-gray-400 hover:text-gray-600"
                  >
                    Dismiss
                  </button>
                </div>
                {/* Progress bar */}
                <div className="mb-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-500">{doneCount}/{steps.length} complete</span>
                    {allDone && <span className="text-xs text-green-600 font-medium">All done! 🎉</span>}
                  </div>
                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-primary-500 to-green-500 rounded-full transition-all duration-500"
                      style={{ width: `${(doneCount / steps.length) * 100}%` }}
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  {steps.map((step, i) => (
                    <Link
                      key={i}
                      href={step.href}
                      className={`flex items-center gap-2.5 px-2.5 py-2 rounded-lg transition text-sm ${
                        step.done
                          ? 'text-gray-400'
                          : 'text-gray-700 hover:bg-primary-50 hover:text-primary-700'
                      }`}
                    >
                      {step.done ? (
                        <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border-2 border-gray-300 flex-shrink-0" />
                      )}
                      <span className={step.done ? 'line-through' : ''}>{step.label}</span>
                    </Link>
                  ))}
                </div>
              </div>
            );
          })()}

          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-semibold text-gray-900">Your Workflows</h3>
              <Link href="/app/workflows" className="text-xs text-primary-600 hover:underline">View all</Link>
            </div>
            {sidebarLoading ? (
              <div className="text-sm text-gray-400 py-4 text-center">Loading...</div>
            ) : workflows.length === 0 ? (
              <div className="text-center py-6 px-2">
                <div className="w-10 h-10 mx-auto mb-3 bg-primary-50 rounded-xl flex items-center justify-center">
                  <Zap className="w-5 h-5 text-primary-500" />
                </div>
                <p className="text-sm text-gray-500 mb-3">No workflows yet</p>
                <p className="text-xs text-gray-400">Ask Aivaro to build your first one ←</p>
              </div>
            ) : (
              <div className="space-y-2">
                {workflows.slice(0, 5).map((wf) => (
                  <Link key={wf.id} href={`/app/workflows/${wf.id}`} className="block p-3 rounded-lg border border-gray-100 hover:border-primary-200 hover:bg-primary-50/30 transition">
                    <div className="flex items-center justify-between">
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900 truncate">{wf.name}</p>
                        <p className="text-xs text-gray-400 mt-0.5">{wf.nodes?.length || 0} steps • {formatDate(wf.updated_at)}</p>
                      </div>
                      <span className={`ml-2 px-2 py-0.5 text-xs rounded-full flex-shrink-0 ${wf.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                        {wf.is_active ? 'Active' : 'Draft'}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Quick Links</h3>
            <div className="space-y-1">
              {[
                { href: '/app/templates', label: 'Browse Templates', icon: <Sparkles className="w-4 h-4" /> },
                { href: '/app/connections', label: 'Manage Connections', icon: <Zap className="w-4 h-4" /> },
                { href: '/app/knowledge', label: 'Knowledge Base', icon: <Bot className="w-4 h-4" /> },
                { href: '/app/executions', label: 'Run History', icon: <Clock className="w-4 h-4" /> },
                { href: '/app/approvals', label: 'Approvals', icon: <CheckCircle2 className="w-4 h-4" /> },
              ].map((link) => (
                <Link key={link.href} href={link.href} className="flex items-center gap-3 px-3 py-2 text-sm text-gray-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition">
                  {link.icon}
                  {link.label}
                  <ChevronRight className="w-3.5 h-3.5 ml-auto text-gray-300" />
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>

      <ConfirmDialog
        open={!!deleteConvoTarget}
        title="Delete conversation"
        message="This will permanently delete this conversation and all its messages. This cannot be undone."
        confirmLabel="Delete"
        onConfirm={confirmDeleteConversation}
        onCancel={() => setDeleteConvoTarget(null)}
      />
    </div>
  );
}
