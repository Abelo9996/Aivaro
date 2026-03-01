'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '@/stores/authStore';
import { api } from '@/lib/api';
import {
  ArrowRight, ArrowLeft, Check, Zap, Mail, Calendar, DollarSign,
  FileSpreadsheet, MessageSquare, Loader2, Shield, Sparkles,
  ChevronRight, Building2, ShoppingBag, Briefcase, Wrench, MoreHorizontal,
} from 'lucide-react';

const colors = {
  primary: '#8b5cf6',
  primaryLight: '#a78bfa',
  accent: '#10b981',
  textPrimary: '#e2e8f0',
  textSecondary: 'rgba(226, 232, 240, 0.8)',
  textMuted: 'rgba(226, 232, 240, 0.6)',
  darkBg: '#0a0a1a',
  darkerBg: '#050510',
  cardBg: 'rgba(15, 15, 35, 0.6)',
  cardBorder: 'rgba(139, 92, 246, 0.2)',
};

const BUSINESS_TYPES = [
  { id: 'service', label: 'Service Business', description: 'Cleaning, HVAC, consulting, coaching, personal training', icon: <Wrench size={22} /> },
  { id: 'resale', label: 'Resale / E-commerce', description: 'Selling products online, at auctions, or on marketplaces', icon: <ShoppingBag size={22} /> },
  { id: 'agency', label: 'Agency / Freelance', description: 'Creative, marketing, development, or consulting work', icon: <Briefcase size={22} /> },
  { id: 'local', label: 'Local / Brick & Mortar', description: 'Restaurant, salon, gym, retail store', icon: <Building2 size={22} /> },
  { id: 'other', label: 'Something Else', description: "We'll figure it out together", icon: <MoreHorizontal size={22} /> },
];

const WORKFLOW_TEMPLATES = [
  {
    id: 'booking-deposit',
    title: 'Booking → Deposit → Reminder',
    description: 'Collect deposits when someone books, send reminders before appointments, track no-shows.',
    icon: <Calendar size={20} />,
    color: '#8b5cf6',
    tools: ['gmail', 'stripe', 'calendar', 'sheets'],
    popular: true,
  },
  {
    id: 'lead-followup',
    title: 'Lead → Follow-up → Close',
    description: 'Auto-respond to inquiries, send follow-up sequences, notify you when leads are hot.',
    icon: <Mail size={20} />,
    color: '#3b82f6',
    tools: ['gmail', 'sheets'],
    popular: true,
  },
  {
    id: 'payment-invoice',
    title: 'Payment → Invoice → Report',
    description: 'Track payments, log revenue, get weekly profit/loss summaries automatically.',
    icon: <DollarSign size={20} />,
    color: '#10b981',
    tools: ['stripe', 'gmail', 'sheets'],
    popular: false,
  },
  {
    id: 'custom',
    title: 'Describe Your Own',
    description: "Tell Aivaro what you need in plain English. We'll build it.",
    icon: <MessageSquare size={20} />,
    color: '#f59e0b',
    tools: [],
    popular: false,
  },
];

const TOOLS = [
  { id: 'google', name: 'Google', description: 'Gmail, Sheets, Calendar', icon: '/icons/gmail.svg', authType: 'oauth' },
  { id: 'stripe', name: 'Stripe', description: 'Payments & invoicing', icon: '/icons/stripe.svg', authType: 'api_key' },
];

export default function OnboardingPage() {
  const router = useRouter();
  const { user, checkAuth, updateUser } = useAuthStore();
  const [step, setStep] = useState(1);
  const [businessType, setBusinessType] = useState('');
  const [selectedWorkflow, setSelectedWorkflow] = useState('');
  const [customPrompt, setCustomPrompt] = useState('');
  const [connectedTools, setConnectedTools] = useState<string[]>([]);
  const [connectingTool, setConnectingTool] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [connections, setConnections] = useState<any[]>([]);

  const totalSteps = 4;

  useEffect(() => {
    checkAuth();
    loadConnections();
  }, []);

  const loadConnections = async () => {
    try {
      const data = await api.getConnections();
      setConnections(data);
      setConnectedTools(data.map((c: any) => c.service_type));
    } catch (err) {
      // Not connected yet, that's fine
    }
  };

  const handleBusinessSelect = async (type: string) => {
    setBusinessType(type);
    try {
      await updateUser({ business_type: type });
    } catch (err) {
      // Continue anyway
    }
    setStep(2);
  };

  const handleWorkflowSelect = (id: string) => {
    setSelectedWorkflow(id);
    if (id === 'custom') {
      // Stay on step 2 to show text input, then advance
      return;
    }
    setStep(3);
  };

  const handleCustomSubmit = () => {
    if (customPrompt.trim()) {
      setStep(3);
    }
  };

  const handleConnectTool = async (toolId: string) => {
    setConnectingTool(toolId);
    try {
      const result = await api.authorizeConnection(toolId);
      if (result.authorization_url) {
        const popup = window.open(result.authorization_url, 'oauth', 'width=500,height=600');
        
        // Listen for postMessage from the OAuth callback page
        const handleMessage = async (event: MessageEvent) => {
          if (event.origin !== window.location.origin) return;
          if (event.data?.type === 'oauth_callback') {
            window.removeEventListener('message', handleMessage);
            clearInterval(interval);
            await loadConnections();
            setConnectingTool(null);
          }
        };
        window.addEventListener('message', handleMessage);
        
        // Fallback: poll for popup close (in case postMessage fails)
        const interval = setInterval(async () => {
          try {
            if (popup?.closed) {
              clearInterval(interval);
              window.removeEventListener('message', handleMessage);
              await loadConnections();
              setConnectingTool(null);
            }
          } catch {
            // Cross-origin, keep waiting
          }
        }, 1000);
        setTimeout(() => { clearInterval(interval); window.removeEventListener('message', handleMessage); setConnectingTool(null); }, 120000);
      } else if (result.demo_mode) {
        // Demo mode — simulate connection
        setConnectedTools(prev => [...prev, toolId]);
        setConnectingTool(null);
      } else {
        setConnectingTool(null);
      }
    } catch (err) {
      console.error('Failed to connect:', err);
      setConnectingTool(null);
    }
  };

  const handleComplete = async () => {
    setLoading(true);
    try {
      // Store onboarding context for the chat to pick up
      const onboardingContext = {
        businessType,
        selectedWorkflow,
        customPrompt: customPrompt.trim() || null,
        connectedTools: connectedTools,
        templateName: selectedWorkflow !== 'custom' 
          ? WORKFLOW_TEMPLATES.find(w => w.id === selectedWorkflow)?.title 
          : null,
      };
      localStorage.setItem('aivaro_onboarding_context', JSON.stringify(onboardingContext));

      // If they selected a template, create the workflow
      if (selectedWorkflow && selectedWorkflow !== 'custom') {
        try {
          const templates = await api.getTemplates();
          const match = templates.find((t: any) =>
            t.name?.toLowerCase().includes(selectedWorkflow.replace('-', ' ')) ||
            t.id === selectedWorkflow
          );
          if (match) {
            const workflow = await api.useTemplate(match.id);
            await updateUser({ onboarding_completed: true });
            // Store the created workflow info for chat context
            localStorage.setItem('aivaro_onboarding_workflow', JSON.stringify({
              id: workflow.id,
              name: workflow.name || match.name,
            }));
            router.push('/app');
            return;
          }
        } catch (err) {
          // Fall through to AI generation
        }
      }

      // If custom prompt or no template match, use AI to generate
      if (selectedWorkflow === 'custom' && customPrompt.trim()) {
        try {
          const workflow = await api.createWorkflow({
            name: 'My First Workflow',
            prompt: customPrompt,
          });
          await updateUser({ onboarding_completed: true });
          localStorage.setItem('aivaro_onboarding_workflow', JSON.stringify({
            id: workflow.id,
            name: workflow.name || 'My First Workflow',
          }));
          router.push('/app');
          return;
        } catch (err) {
          // Fall through to dashboard
        }
      }

      await updateUser({ onboarding_completed: true });
      router.push('/app');
    } catch (err) {
      console.error('Failed to complete onboarding:', err);
      router.push('/app');
    } finally {
      setLoading(false);
    }
  };

  const canProceedFromStep3 = true; // Connections are optional

  return (
    <div style={{
      minHeight: '100vh',
      background: `linear-gradient(135deg, ${colors.darkerBg} 0%, ${colors.darkBg} 50%, ${colors.darkerBg} 100%)`,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '40px 16px',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Background */}
      <div style={{ position: 'absolute', top: '-20%', left: '10%', width: '600px', height: '600px', background: 'radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%)', filter: 'blur(80px)', pointerEvents: 'none' }} />
      <div style={{ position: 'absolute', bottom: '-20%', right: '10%', width: '500px', height: '500px', background: 'radial-gradient(circle, rgba(59, 130, 246, 0.08) 0%, transparent 70%)', filter: 'blur(80px)', pointerEvents: 'none' }} />

      {/* Logo */}
      <div style={{ marginBottom: 32 }}>
        <img src="/logo.png" alt="Aivaro" style={{ height: 40, width: 'auto' }} />
      </div>

      {/* Progress Bar */}
      <div style={{ width: '100%', maxWidth: 560, marginBottom: 40 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
          <span style={{ fontSize: 13, color: colors.textMuted }}>Step {step} of {totalSteps}</span>
          <span style={{ fontSize: 13, color: colors.textMuted }}>{Math.round((step / totalSteps) * 100)}%</span>
        </div>
        <div style={{ height: 4, borderRadius: 2, background: 'rgba(139, 92, 246, 0.15)', overflow: 'hidden' }}>
          <motion.div
            style={{ height: '100%', borderRadius: 2, background: `linear-gradient(90deg, ${colors.primary}, ${colors.accent})` }}
            animate={{ width: `${(step / totalSteps) * 100}%` }}
            transition={{ duration: 0.4, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Content */}
      <div style={{ width: '100%', maxWidth: 560 }}>
        <AnimatePresence mode="wait">

          {/* Step 1: Business Type */}
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              transition={{ duration: 0.3 }}
            >
              <h1 style={{ fontSize: 28, fontWeight: 800, color: colors.textPrimary, marginBottom: 8, textAlign: 'center' }}>
                What kind of business do you run?
              </h1>
              <p style={{ fontSize: 16, color: colors.textMuted, textAlign: 'center', marginBottom: 32 }}>
                We'll tailor your automations to fit.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {BUSINESS_TYPES.map((type) => (
                  <motion.button
                    key={type.id}
                    onClick={() => handleBusinessSelect(type.id)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 16,
                      width: '100%', textAlign: 'left',
                      padding: '16px 20px',
                      background: colors.cardBg,
                      border: `1.5px solid ${colors.cardBorder}`,
                      borderRadius: 14,
                      cursor: 'pointer',
                      color: colors.textPrimary,
                    }}
                    whileHover={{ borderColor: colors.primary, background: 'rgba(139, 92, 246, 0.08)', x: 4 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div style={{ width: 44, height: 44, borderRadius: 10, background: 'rgba(139, 92, 246, 0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: colors.primary, flexShrink: 0 }}>
                      {type.icon}
                    </div>
                    <div>
                      <div style={{ fontSize: 16, fontWeight: 600 }}>{type.label}</div>
                      <div style={{ fontSize: 13, color: colors.textMuted, marginTop: 2 }}>{type.description}</div>
                    </div>
                    <ChevronRight size={18} style={{ marginLeft: 'auto', color: colors.textMuted }} />
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}

          {/* Step 2: Pick Workflow */}
          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              transition={{ duration: 0.3 }}
            >
              <h1 style={{ fontSize: 28, fontWeight: 800, color: colors.textPrimary, marginBottom: 8, textAlign: 'center' }}>
                What do you want to automate first?
              </h1>
              <p style={{ fontSize: 16, color: colors.textMuted, textAlign: 'center', marginBottom: 32 }}>
                Pick a revenue loop or describe your own. You can always add more later.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {WORKFLOW_TEMPLATES.map((wf) => (
                  <motion.button
                    key={wf.id}
                    onClick={() => handleWorkflowSelect(wf.id)}
                    style={{
                      display: 'flex', alignItems: 'flex-start', gap: 16,
                      width: '100%', textAlign: 'left',
                      padding: '16px 20px',
                      background: selectedWorkflow === wf.id ? 'rgba(139, 92, 246, 0.1)' : colors.cardBg,
                      border: `1.5px solid ${selectedWorkflow === wf.id ? colors.primary : colors.cardBorder}`,
                      borderRadius: 14,
                      cursor: 'pointer',
                      color: colors.textPrimary,
                      position: 'relative',
                    }}
                    whileHover={{ borderColor: colors.primary, background: 'rgba(139, 92, 246, 0.08)' }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {wf.popular && (
                      <div style={{ position: 'absolute', top: -8, right: 16, background: colors.accent, color: '#fff', fontSize: 11, fontWeight: 700, padding: '2px 10px', borderRadius: 999 }}>
                        Popular
                      </div>
                    )}
                    <div style={{ width: 40, height: 40, borderRadius: 10, background: `${wf.color}20`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: wf.color, flexShrink: 0, marginTop: 2 }}>
                      {wf.icon}
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: 16, fontWeight: 600 }}>{wf.title}</div>
                      <div style={{ fontSize: 13, color: colors.textMuted, marginTop: 2, lineHeight: 1.5 }}>{wf.description}</div>
                      {wf.tools.length > 0 && (
                        <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
                          {wf.tools.map((tool) => (
                            <div key={tool} style={{ fontSize: 11, color: colors.textMuted, padding: '2px 8px', borderRadius: 6, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.08)' }}>
                              {tool}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </motion.button>
                ))}
              </div>

              {/* Custom prompt input */}
              {selectedWorkflow === 'custom' && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  style={{ marginTop: 16 }}
                >
                  <textarea
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    placeholder="e.g., When someone fills out my contact form, add them to a spreadsheet, send them a welcome email, and notify me on Slack..."
                    style={{
                      width: '100%',
                      minHeight: 100,
                      padding: 16,
                      background: 'rgba(10, 10, 26, 0.6)',
                      border: `1.5px solid ${colors.cardBorder}`,
                      borderRadius: 12,
                      color: colors.textPrimary,
                      fontSize: 15,
                      lineHeight: 1.6,
                      resize: 'vertical',
                      outline: 'none',
                      fontFamily: 'inherit',
                    }}
                    onFocus={(e) => { e.target.style.borderColor = colors.primary; }}
                    onBlur={(e) => { e.target.style.borderColor = colors.cardBorder; }}
                  />
                  <motion.button
                    onClick={handleCustomSubmit}
                    disabled={!customPrompt.trim()}
                    style={{
                      marginTop: 12, width: '100%',
                      padding: '14px 24px',
                      background: customPrompt.trim() ? `linear-gradient(135deg, ${colors.primary}, #7c3aed)` : 'rgba(139, 92, 246, 0.2)',
                      border: 'none', borderRadius: 12,
                      color: customPrompt.trim() ? '#fff' : colors.textMuted,
                      fontSize: 16, fontWeight: 600,
                      cursor: customPrompt.trim() ? 'pointer' : 'not-allowed',
                      display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                    }}
                    whileHover={customPrompt.trim() ? { scale: 1.02 } : {}}
                    whileTap={customPrompt.trim() ? { scale: 0.98 } : {}}
                  >
                    Continue <ArrowRight size={18} />
                  </motion.button>
                </motion.div>
              )}

              {/* Back button */}
              <button
                onClick={() => { setStep(1); setSelectedWorkflow(''); }}
                style={{ marginTop: 16, background: 'none', border: 'none', color: colors.textMuted, cursor: 'pointer', fontSize: 14, display: 'flex', alignItems: 'center', gap: 6, padding: 0 }}
              >
                <ArrowLeft size={16} /> Back
              </button>
            </motion.div>
          )}

          {/* Step 3: Connect Tools */}
          {step === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              transition={{ duration: 0.3 }}
            >
              <h1 style={{ fontSize: 28, fontWeight: 800, color: colors.textPrimary, marginBottom: 8, textAlign: 'center' }}>
                Connect your tools
              </h1>
              <p style={{ fontSize: 16, color: colors.textMuted, textAlign: 'center', marginBottom: 32 }}>
                One-click OAuth. Your data stays yours. You can also do this later.
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {TOOLS.map((tool) => {
                  const isConnected = connectedTools.includes(tool.id);
                  const isConnecting = connectingTool === tool.id;

                  return (
                    <div
                      key={tool.id}
                      style={{
                        display: 'flex', alignItems: 'center', gap: 16,
                        padding: '18px 20px',
                        background: isConnected ? 'rgba(16, 185, 129, 0.06)' : colors.cardBg,
                        border: `1.5px solid ${isConnected ? 'rgba(16, 185, 129, 0.3)' : colors.cardBorder}`,
                        borderRadius: 14,
                      }}
                    >
                      <img src={tool.icon} alt={tool.name} style={{ width: 36, height: 36, objectFit: 'contain' }} />
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 16, fontWeight: 600, color: colors.textPrimary }}>{tool.name}</div>
                        <div style={{ fontSize: 13, color: colors.textMuted }}>{tool.description}</div>
                      </div>
                      {isConnected ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: colors.accent, fontSize: 14, fontWeight: 600 }}>
                          <Check size={18} /> Connected
                        </div>
                      ) : (
                        <motion.button
                          onClick={() => handleConnectTool(tool.id)}
                          disabled={isConnecting}
                          style={{
                            padding: '8px 18px',
                            background: 'rgba(139, 92, 246, 0.12)',
                            border: `1px solid ${colors.primary}`,
                            borderRadius: 10,
                            color: colors.primary,
                            fontSize: 14,
                            fontWeight: 600,
                            cursor: isConnecting ? 'wait' : 'pointer',
                            display: 'flex', alignItems: 'center', gap: 6,
                          }}
                          whileHover={!isConnecting ? { background: 'rgba(139, 92, 246, 0.2)' } : {}}
                          whileTap={!isConnecting ? { scale: 0.96 } : {}}
                        >
                          {isConnecting ? (
                            <><Loader2 size={16} className="animate-spin" /> Connecting...</>
                          ) : (
                            'Connect'
                          )}
                        </motion.button>
                      )}
                    </div>
                  );
                })}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 16, padding: '12px 16px', background: 'rgba(139, 92, 246, 0.04)', borderRadius: 10, border: '1px solid rgba(139, 92, 246, 0.1)' }}>
                <Shield size={16} color={colors.textMuted} />
                <span style={{ fontSize: 13, color: colors.textMuted }}>
                  Secure OAuth — we never see your passwords. Revoke access anytime.
                </span>
              </div>

              <div style={{ display: 'flex', gap: 12, marginTop: 24 }}>
                <button
                  onClick={() => setStep(2)}
                  style={{ padding: '14px 20px', background: 'none', border: `1.5px solid ${colors.cardBorder}`, borderRadius: 12, color: colors.textMuted, fontSize: 15, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                >
                  <ArrowLeft size={16} /> Back
                </button>
                <motion.button
                  onClick={() => setStep(4)}
                  style={{
                    flex: 1, padding: '14px 24px',
                    background: `linear-gradient(135deg, ${colors.primary}, #7c3aed)`,
                    border: 'none', borderRadius: 12,
                    color: '#fff', fontSize: 16, fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                    boxShadow: '0 4px 16px rgba(139, 92, 246, 0.3)',
                  }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {connectedTools.length > 0 ? 'Continue' : 'Skip for now'} <ArrowRight size={18} />
                </motion.button>
              </div>
            </motion.div>
          )}

          {/* Step 4: Ready to go */}
          {step === 4 && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              transition={{ duration: 0.3 }}
              style={{ textAlign: 'center' }}
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
                style={{ fontSize: 64, marginBottom: 16 }}
              >
                🚀
              </motion.div>
              <h1 style={{ fontSize: 28, fontWeight: 800, color: colors.textPrimary, marginBottom: 8 }}>
                You're ready to go
              </h1>
              <p style={{ fontSize: 16, color: colors.textMuted, marginBottom: 32, maxWidth: 400, margin: '0 auto 32px' }}>
                {selectedWorkflow === 'custom'
                  ? "We'll build your custom workflow and take you straight to it."
                  : selectedWorkflow
                    ? "We'll set up your first workflow. You can test it before turning it on."
                    : "Let's get your first automation running."
                }
              </p>

              {/* Summary */}
              <div style={{
                background: colors.cardBg, borderRadius: 14, border: `1.5px solid ${colors.cardBorder}`,
                padding: 20, marginBottom: 24, textAlign: 'left',
              }}>
                <div style={{ fontSize: 13, color: colors.textMuted, textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600, marginBottom: 14 }}>Setup Summary</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <Check size={16} color={colors.accent} />
                    <span style={{ fontSize: 14, color: colors.textSecondary }}>
                      Business type: <strong style={{ color: colors.textPrimary }}>{BUSINESS_TYPES.find(b => b.id === businessType)?.label || 'Selected'}</strong>
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <Check size={16} color={colors.accent} />
                    <span style={{ fontSize: 14, color: colors.textSecondary }}>
                      First workflow: <strong style={{ color: colors.textPrimary }}>
                        {selectedWorkflow === 'custom' ? 'Custom' : WORKFLOW_TEMPLATES.find(w => w.id === selectedWorkflow)?.title || 'Selected'}
                      </strong>
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    {connectedTools.length > 0 ? (
                      <Check size={16} color={colors.accent} />
                    ) : (
                      <div style={{ width: 16, height: 16, borderRadius: 4, border: `1.5px solid ${colors.textMuted}`, flexShrink: 0 }} />
                    )}
                    <span style={{ fontSize: 14, color: colors.textSecondary }}>
                      Tools connected: <strong style={{ color: colors.textPrimary }}>
                        {connectedTools.length > 0 ? connectedTools.join(', ') : 'None yet (can do later)'}
                      </strong>
                    </span>
                  </div>
                </div>
              </div>

              <motion.button
                onClick={handleComplete}
                disabled={loading}
                style={{
                  width: '100%', padding: '16px 24px',
                  background: `linear-gradient(135deg, ${colors.primary}, #7c3aed)`,
                  border: 'none', borderRadius: 12,
                  color: '#fff', fontSize: 17, fontWeight: 700,
                  cursor: loading ? 'wait' : 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                  boxShadow: '0 4px 20px rgba(139, 92, 246, 0.4)',
                }}
                whileHover={!loading ? { scale: 1.02, boxShadow: '0 6px 24px rgba(139, 92, 246, 0.5)' } : {}}
                whileTap={!loading ? { scale: 0.98 } : {}}
              >
                {loading ? (
                  <><Loader2 size={20} className="animate-spin" /> Setting up...</>
                ) : (
                  <>Launch Aivaro <Sparkles size={20} /></>
                )}
              </motion.button>

              <button
                onClick={() => setStep(3)}
                style={{ marginTop: 16, background: 'none', border: 'none', color: colors.textMuted, cursor: 'pointer', fontSize: 14, display: 'flex', alignItems: 'center', gap: 6, margin: '16px auto 0', padding: 0 }}
              >
                <ArrowLeft size={16} /> Back
              </button>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  );
}
