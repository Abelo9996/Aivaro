'use client';

import { useState } from 'react';
import { Sparkles, Wand2, RefreshCw, Bot, Loader2, CheckCircle, MessageCircle, ChevronRight, HelpCircle, Check } from 'lucide-react';
import { api } from '@/lib/api';
import ServiceIcon from '@/components/ui/ServiceIcon';

interface GeneratedWorkflow {
  workflowName: string;
  summary: string;
  nodes: any[];
  edges: any[];
}

interface ClarificationQuestion {
  id: string;
  question: string;
  why: string;
  options?: string[] | null;
  allow_multiple: boolean;
}

interface AIWorkflowGeneratorProps {
  onGenerate: (workflow: GeneratedWorkflow) => void;
  onCancel: () => void;
}

const EXAMPLE_PROMPTS = [
  "Send a welcome email when someone fills out my contact form, then follow up after 3 days if they haven't responded",
  "When I get a new order, log it to my spreadsheet and send a confirmation email to the customer",
  "Send me a daily summary of new leads from my website form",
  "When a booking is made, confirm with the customer and notify my team on Slack",
  "Follow up with customers who haven't purchased in 30 days",
];

type Step = 'input' | 'clarifying' | 'generating' | 'preview';

export default function AIWorkflowGenerator({ onGenerate, onCancel }: AIWorkflowGeneratorProps) {
  const [prompt, setPrompt] = useState('');
  const [step, setStep] = useState<Step>('input');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Clarification state
  const [questions, setQuestions] = useState<ClarificationQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [understood, setUnderstood] = useState<Record<string, any>>({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  
  // Generated workflow
  const [generatedWorkflow, setGeneratedWorkflow] = useState<GeneratedWorkflow | null>(null);

  const handleStartGeneration = async () => {
    if (!prompt.trim() || prompt.length < 10) {
      setError('Please describe your workflow in more detail (at least 10 characters)');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // First, check if we need clarification
      const clarification = await api.clarifyWorkflow(prompt);
      
      if (!clarification.is_complete && clarification.questions.length > 0) {
        // Need to ask clarifying questions
        setQuestions(clarification.questions);
        setUnderstood(clarification.understood);
        setCurrentQuestionIndex(0);
        setAnswers({});
        setStep('clarifying');
      } else {
        // Prompt is clear enough, generate directly
        setStep('generating');
        const result = await api.generateWorkflow(prompt, {}, true);
        
        if (result.needs_clarification) {
          // Backend still wants clarification
          setQuestions(result.questions || []);
          setUnderstood(result.understood || {});
          setCurrentQuestionIndex(0);
          setStep('clarifying');
        } else {
          setGeneratedWorkflow(result);
          setStep('preview');
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to analyze your request. Please try again.');
      setStep('input');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnswerQuestion = (questionId: string, answer: any) => {
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const handleToggleMultipleChoice = (questionId: string, option: string) => {
    setAnswers(prev => {
      const current = prev[questionId] || [];
      if (current.includes(option)) {
        return { ...prev, [questionId]: current.filter((o: string) => o !== option) };
      } else {
        return { ...prev, [questionId]: [...current, option] };
      }
    });
  };

  const handleNextQuestion = async () => {
    const currentQuestion = questions[currentQuestionIndex];
    
    // Validate answer
    if (!answers[currentQuestion.id] || 
        (Array.isArray(answers[currentQuestion.id]) && answers[currentQuestion.id].length === 0)) {
      setError('Please select an answer to continue');
      return;
    }
    
    setError(null);
    
    if (currentQuestionIndex < questions.length - 1) {
      // More questions to ask
      setCurrentQuestionIndex(prev => prev + 1);
    } else {
      // All questions answered, generate workflow
      await handleGenerateWithClarifications();
    }
  };

  const handleGenerateWithClarifications = async () => {
    setStep('generating');
    setIsLoading(true);
    setError(null);

    try {
      const result = await api.generateWorkflow(prompt, answers);
      
      if (result.needs_clarification) {
        // Still needs more info (shouldn't happen often)
        setQuestions(result.questions || []);
        setCurrentQuestionIndex(0);
        setStep('clarifying');
      } else {
        setGeneratedWorkflow(result);
        setStep('preview');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to generate workflow. Please try again.');
      setStep('clarifying');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUseWorkflow = () => {
    if (generatedWorkflow) {
      onGenerate(generatedWorkflow);
    }
  };

  const handleRegenerate = () => {
    setGeneratedWorkflow(null);
    setAnswers({});
    setQuestions([]);
    setCurrentQuestionIndex(0);
    setStep('input');
  };

  const handleSkipClarification = async () => {
    setStep('generating');
    setIsLoading(true);
    setError(null);

    try {
      const result = await api.generateWorkflow(prompt, {}, true);
      setGeneratedWorkflow(result);
      setStep('preview');
    } catch (err: any) {
      setError(err.message || 'Failed to generate workflow. Please try again.');
      setStep('input');
    } finally {
      setIsLoading(false);
    }
  };

  // ==================== RENDER: PREVIEW ====================
  if (step === 'preview' && generatedWorkflow) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
        <div className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-500 to-purple-600 text-white p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold">{generatedWorkflow.workflowName}</h2>
                <p className="text-white/80 text-sm">{generatedWorkflow.summary}</p>
              </div>
            </div>
          </div>

          {/* Workflow Preview */}
          <div className="p-6 max-h-[400px] overflow-y-auto">
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-4">Workflow Steps</h3>
            <div className="space-y-3">
              {generatedWorkflow.nodes.map((node, index) => (
                <div 
                  key={node.id} 
                  className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100"
                >
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                    <ServiceIcon type={node.type} size={18} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-900 truncate">{node.label}</div>
                    <div className="text-xs text-gray-500 capitalize">{node.type.replace('_', ' ')}</div>
                  </div>
                  <div className="text-xs text-gray-400">
                    Step {index + 1}
                  </div>
                </div>
              ))}
            </div>

            {/* Connection visualization */}
            <div className="mt-4 p-3 bg-primary-50 rounded-lg">
              <div className="text-xs text-primary-700">
                <strong>{generatedWorkflow.nodes.length} steps</strong> connected with{' '}
                <strong>{generatedWorkflow.edges.length} connections</strong>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="p-6 bg-gray-50 border-t border-gray-100 flex gap-3">
            <button
              onClick={handleRegenerate}
              className="flex-1 px-4 py-3 border border-gray-200 rounded-xl text-gray-700 hover:bg-gray-100 transition-colors font-medium flex items-center justify-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Start Over
            </button>
            <button
              onClick={onCancel}
              className="px-4 py-3 border border-gray-200 rounded-xl text-gray-700 hover:bg-gray-100 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleUseWorkflow}
              className="flex-1 px-4 py-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors font-medium flex items-center justify-center gap-2"
            >
              <CheckCircle className="w-4 h-4" />
              Use This Workflow
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ==================== RENDER: GENERATING ====================
  if (step === 'generating') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
        <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in">
          <div className="p-8 text-center">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Bot className="w-8 h-8 text-primary-500 animate-pulse" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Building Your Workflow</h2>
            <p className="text-gray-600 mb-4">AI is crafting the perfect automation based on your requirements...</p>
            <div className="flex justify-center">
              <Loader2 className="w-6 h-6 text-primary-500 animate-spin" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ==================== RENDER: CLARIFYING ====================
  if (step === 'clarifying' && questions.length > 0) {
    const currentQuestion = questions[currentQuestionIndex];
    const currentAnswer = answers[currentQuestion.id];
    const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
        <div className="w-full max-w-xl bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4">
          {/* Header with progress */}
          <div className="bg-gradient-to-r from-primary-500 to-purple-600 text-white p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                <MessageCircle className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-lg font-bold">Let me understand better</h2>
                <p className="text-white/80 text-sm">Question {currentQuestionIndex + 1} of {questions.length}</p>
              </div>
            </div>
            {/* Progress bar */}
            <div className="w-full bg-white/20 rounded-full h-2">
              <div 
                className="bg-white rounded-full h-2 transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* What we understood so far */}
          {Object.keys(understood).length > 0 && currentQuestionIndex === 0 && (
            <div className="px-6 pt-4">
              <div className="p-3 bg-green-50 border border-green-100 rounded-lg">
                <p className="text-sm text-green-800 font-medium mb-1">✓ I understood:</p>
                <ul className="text-sm text-green-700 space-y-0.5">
                  {understood.trigger && <li>Trigger: {understood.trigger}</li>}
                  {understood.actions?.length > 0 && <li>Actions: {understood.actions.join(', ')}</li>}
                  {understood.integrations?.length > 0 && <li>Tools: {understood.integrations.join(', ')}</li>}
                </ul>
              </div>
            </div>
          )}

          {/* Question */}
          <div className="p-6">
            <div className="mb-2">
              <h3 className="text-lg font-semibold text-gray-900">{currentQuestion.question}</h3>
              <p className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                <HelpCircle className="w-3.5 h-3.5" />
                {currentQuestion.why}
              </p>
            </div>

            {error && (
              <p className="text-sm text-red-500 mb-3">{error}</p>
            )}

            {/* Options */}
            {currentQuestion.options ? (
              <div className="space-y-2 mt-4">
                {currentQuestion.options.map((option, index) => {
                  const isSelected = currentQuestion.allow_multiple
                    ? (currentAnswer || []).includes(option)
                    : currentAnswer === option;
                  
                  return (
                    <button
                      key={index}
                      onClick={() => {
                        if (currentQuestion.allow_multiple) {
                          handleToggleMultipleChoice(currentQuestion.id, option);
                        } else {
                          handleAnswerQuestion(currentQuestion.id, option);
                        }
                      }}
                      className={`w-full text-left p-3 rounded-lg border-2 transition-all flex items-center gap-3 ${
                        isSelected
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                        isSelected ? 'border-primary-500 bg-primary-500' : 'border-gray-300'
                      }`}>
                        {isSelected && <Check className="w-3 h-3 text-white" />}
                      </div>
                      <span className={`text-sm ${isSelected ? 'text-primary-900 font-medium' : 'text-gray-700'}`}>
                        {option}
                      </span>
                    </button>
                  );
                })}
              </div>
            ) : (
              // Free text input
              <div className="mt-4">
                <input
                  type="text"
                  value={currentAnswer || ''}
                  onChange={(e) => handleAnswerQuestion(currentQuestion.id, e.target.value)}
                  placeholder="Type your answer..."
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-gray-900"
                />
              </div>
            )}

            {currentQuestion.allow_multiple && (
              <p className="text-xs text-gray-500 mt-2">You can select multiple options</p>
            )}
          </div>

          {/* Actions */}
          <div className="p-6 bg-gray-50 border-t border-gray-100 flex gap-3">
            <button
              onClick={handleSkipClarification}
              className="px-4 py-3 text-gray-500 hover:text-gray-700 text-sm transition-colors"
            >
              Skip & Generate
            </button>
            <div className="flex-1" />
            <button
              onClick={handleNextQuestion}
              disabled={isLoading}
              className="px-6 py-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors font-medium flex items-center gap-2 disabled:opacity-50"
            >
              {currentQuestionIndex < questions.length - 1 ? (
                <>
                  Next
                  <ChevronRight className="w-4 h-4" />
                </>
              ) : (
                <>
                  Generate Workflow
                  <Sparkles className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ==================== RENDER: INPUT ====================
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-xl bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-bottom-4">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-500 to-purple-600 text-white p-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <Wand2 className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold">Generate Workflow with AI</h2>
              <p className="text-white/80 text-sm">Describe what you want to automate in plain English</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              What would you like to automate?
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g., When someone fills out my contact form, send them a welcome email and add their info to my spreadsheet..."
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none text-gray-900"
              rows={4}
              disabled={isLoading}
            />
            {error && (
              <p className="mt-2 text-sm text-red-500">{error}</p>
            )}
          </div>

          {/* Example prompts */}
          <div className="mb-4">
            <p className="text-xs text-gray-500 mb-2">Try one of these examples:</p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_PROMPTS.slice(0, 3).map((example, index) => (
                <button
                  key={index}
                  onClick={() => setPrompt(example)}
                  disabled={isLoading}
                  className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600 transition-colors truncate max-w-[200px]"
                  title={example}
                >
                  {example.slice(0, 40)}...
                </button>
              ))}
            </div>
          </div>

          {/* Info box */}
          <div className="p-3 bg-blue-50 border border-blue-100 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>💡 Tip:</strong> I'll ask a few quick questions to make sure I build exactly what you need.
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="p-6 bg-gray-50 border-t border-gray-100 flex gap-3">
          <button
            onClick={onCancel}
            disabled={isLoading}
            className="flex-1 px-4 py-3 border border-gray-200 rounded-xl text-gray-700 hover:bg-gray-100 transition-colors font-medium disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleStartGeneration}
            disabled={isLoading || !prompt.trim()}
            className="flex-1 px-4 py-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                Continue
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
