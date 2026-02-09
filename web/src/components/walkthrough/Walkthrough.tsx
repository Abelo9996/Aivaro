'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';

export interface WalkthroughStep {
  id: string;
  title: string;
  description: string;
  targetSelector?: string;
  position?: 'top' | 'bottom' | 'left' | 'right' | 'center';
  spotlightPadding?: number;
  path?: string;
}

interface WalkthroughProps {
  steps: WalkthroughStep[];
  isOpen: boolean;
  onComplete: () => void;
  onSkip: () => void;
}

interface TooltipPosition {
  top: number;
  left: number;
  arrowPosition: 'top' | 'bottom' | 'left' | 'right' | 'none';
}

export default function Walkthrough({ steps, isOpen, onComplete, onSkip }: WalkthroughProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [currentStep, setCurrentStep] = useState(0);
  const [tooltipPosition, setTooltipPosition] = useState<TooltipPosition>({ top: 0, left: 0, arrowPosition: 'none' });
  const [spotlightRect, setSpotlightRect] = useState<DOMRect | null>(null);
  const [mounted, setMounted] = useState(false);
  const [isNavigating, setIsNavigating] = useState(false);

  const step = steps[currentStep];
  const isLastStep = currentStep === steps.length - 1;
  const isFirstStep = currentStep === 0;

  useEffect(() => {
    setMounted(true);
  }, []);

  // Handle navigation when step changes
  useEffect(() => {
    if (!isOpen || !step?.path) return;
    
    if (pathname !== step.path) {
      setIsNavigating(true);
      router.push(step.path);
    }
  }, [currentStep, step?.path, pathname, router, isOpen]);

  // Wait for navigation to complete and element to appear
  useEffect(() => {
    if (!isOpen || !step) return;

    const checkAndCalculate = () => {
      // If we're on the right page, try to find the target
      if (step.path && pathname !== step.path) {
        return; // Still navigating
      }

      setIsNavigating(false);

      if (!step.targetSelector || step.position === 'center') {
        setSpotlightRect(null);
        setTooltipPosition({
          top: window.innerHeight / 2 - 100,
          left: window.innerWidth / 2 - 160,
          arrowPosition: 'none',
        });
        return;
      }

      const target = document.querySelector(step.targetSelector);
      if (!target) {
        // Element not found yet, use center position temporarily
        setSpotlightRect(null);
        setTooltipPosition({
          top: window.innerHeight / 2 - 100,
          left: window.innerWidth / 2 - 160,
          arrowPosition: 'none',
        });
        return;
      }

      const rect = target.getBoundingClientRect();
      const padding = step.spotlightPadding ?? 8;
      
      setSpotlightRect(new DOMRect(
        rect.left - padding,
        rect.top - padding,
        rect.width + padding * 2,
        rect.height + padding * 2
      ));

      const tooltipWidth = 340;
      const tooltipHeight = 200;
      const gap = 16;

      let top = 0;
      let left = 0;
      let arrowPosition: 'top' | 'bottom' | 'left' | 'right' | 'none' = 'none';

      const position = step.position || 'bottom';

      switch (position) {
        case 'bottom':
          top = rect.bottom + gap + padding;
          left = rect.left + rect.width / 2 - tooltipWidth / 2;
          arrowPosition = 'top';
          break;
        case 'top':
          top = rect.top - tooltipHeight - gap - padding;
          left = rect.left + rect.width / 2 - tooltipWidth / 2;
          arrowPosition = 'bottom';
          break;
        case 'left':
          top = rect.top + rect.height / 2 - tooltipHeight / 2;
          left = rect.left - tooltipWidth - gap - padding;
          arrowPosition = 'right';
          break;
        case 'right':
          top = rect.top + rect.height / 2 - tooltipHeight / 2;
          left = rect.right + gap + padding;
          arrowPosition = 'left';
          break;
      }

      // Keep tooltip within viewport
      left = Math.max(16, Math.min(left, window.innerWidth - tooltipWidth - 16));
      top = Math.max(16, Math.min(top, window.innerHeight - tooltipHeight - 16));

      setTooltipPosition({ top, left, arrowPosition });
    };

    // Initial check
    checkAndCalculate();

    // Retry a few times in case elements are still loading
    const retryTimers = [
      setTimeout(checkAndCalculate, 100),
      setTimeout(checkAndCalculate, 300),
      setTimeout(checkAndCalculate, 500),
    ];

    window.addEventListener('resize', checkAndCalculate);
    window.addEventListener('scroll', checkAndCalculate);
    document.body.style.overflow = 'hidden';
    
    return () => {
      retryTimers.forEach(clearTimeout);
      window.removeEventListener('resize', checkAndCalculate);
      window.removeEventListener('scroll', checkAndCalculate);
      document.body.style.overflow = '';
    };
  }, [isOpen, currentStep, step, pathname]);

  const handleNext = useCallback(() => {
    if (isNavigating) return;
    if (isLastStep) {
      onComplete();
    } else {
      setCurrentStep(prev => prev + 1);
    }
  }, [isLastStep, isNavigating, onComplete]);

  const handlePrev = useCallback(() => {
    if (isNavigating) return;
    if (!isFirstStep) {
      setCurrentStep(prev => prev - 1);
    }
  }, [isFirstStep, isNavigating]);

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (isNavigating) return;
    if (e.key === 'Escape') {
      onSkip();
    } else if (e.key === 'ArrowRight' || e.key === 'Enter') {
      handleNext();
    } else if (e.key === 'ArrowLeft') {
      handlePrev();
    }
  }, [isNavigating, onSkip, handleNext, handlePrev]);

  useEffect(() => {
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, handleKeyDown]);

  if (!mounted || !isOpen || !step) return null;

  return createPortal(
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[9999]"
      >
        {/* Overlay with spotlight cutout */}
        <svg className="absolute inset-0 w-full h-full">
          <defs>
            <mask id="spotlight-mask">
              <rect x="0" y="0" width="100%" height="100%" fill="white" />
              {spotlightRect && (
                <rect
                  x={spotlightRect.left}
                  y={spotlightRect.top}
                  width={spotlightRect.width}
                  height={spotlightRect.height}
                  rx="8"
                  fill="black"
                />
              )}
            </mask>
          </defs>
          <rect
            x="0"
            y="0"
            width="100%"
            height="100%"
            fill="rgba(0, 0, 0, 0.75)"
            mask="url(#spotlight-mask)"
          />
        </svg>

        {/* Spotlight border glow */}
        {spotlightRect && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute rounded-lg ring-4 ring-primary-500 ring-opacity-50"
            style={{
              top: spotlightRect.top,
              left: spotlightRect.left,
              width: spotlightRect.width,
              height: spotlightRect.height,
            }}
          />
        )}

        {/* Tooltip */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          className="absolute bg-white rounded-xl shadow-2xl p-6 w-80"
          style={{
            top: tooltipPosition.top,
            left: tooltipPosition.left,
          }}
        >
          {/* Arrow */}
          {tooltipPosition.arrowPosition !== 'none' && (
            <div
              className={`absolute w-4 h-4 bg-white transform rotate-45 ${
                tooltipPosition.arrowPosition === 'top'
                  ? '-top-2 left-1/2 -translate-x-1/2'
                  : tooltipPosition.arrowPosition === 'bottom'
                  ? '-bottom-2 left-1/2 -translate-x-1/2'
                  : tooltipPosition.arrowPosition === 'left'
                  ? '-left-2 top-1/2 -translate-y-1/2'
                  : '-right-2 top-1/2 -translate-y-1/2'
              }`}
            />
          )}

          {/* Content */}
          <div className="relative">
            {/* Step indicator */}
            <div className="flex items-center gap-1 mb-3">
              {steps.map((_, idx) => (
                <div
                  key={idx}
                  className={`h-1.5 rounded-full transition-all ${
                    idx === currentStep
                      ? 'w-6 bg-primary-600'
                      : idx < currentStep
                      ? 'w-1.5 bg-primary-400'
                      : 'w-1.5 bg-gray-200'
                  }`}
                />
              ))}
            </div>

            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {step.title}
            </h3>
            <p className="text-gray-600 text-sm leading-relaxed mb-6">
              {step.description}
            </p>

            {/* Actions */}
            <div className="flex items-center justify-between">
              <button
                onClick={onSkip}
                className="text-sm text-gray-500 hover:text-gray-700 transition"
              >
                Skip tour
              </button>
              <div className="flex items-center gap-2">
                {!isFirstStep && (
                  <button
                    onClick={handlePrev}
                    className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition"
                  >
                    Back
                  </button>
                )}
                <button
                  onClick={handleNext}
                  className="px-4 py-2 text-sm font-medium bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
                >
                  {isLastStep ? 'Get Started' : 'Next'}
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>,
    document.body
  );
}
