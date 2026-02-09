'use client';

import { useState, useEffect, useCallback } from 'react';
import { WALKTHROUGH_STORAGE_KEY } from './walkthroughSteps';

interface UseWalkthroughOptions {
  autoStart?: boolean;
  onComplete?: () => void;
  onSkip?: () => void;
}

export function useWalkthrough(options: UseWalkthroughOptions = {}) {
  const { autoStart = false, onComplete, onSkip } = options;
  const [isOpen, setIsOpen] = useState(false);
  const [hasCompleted, setHasCompleted] = useState(true); // Default to true to prevent flash

  useEffect(() => {
    // Check localStorage on mount
    const completed = localStorage.getItem(WALKTHROUGH_STORAGE_KEY);
    setHasCompleted(completed === 'true');

    // Auto-start if not completed
    if (autoStart && completed !== 'true') {
      // Delay slightly to let the page render first
      const timer = setTimeout(() => {
        setIsOpen(true);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [autoStart]);

  const startWalkthrough = useCallback(() => {
    setIsOpen(true);
  }, []);

  const completeWalkthrough = useCallback(() => {
    localStorage.setItem(WALKTHROUGH_STORAGE_KEY, 'true');
    setHasCompleted(true);
    setIsOpen(false);
    onComplete?.();
  }, [onComplete]);

  const skipWalkthrough = useCallback(() => {
    localStorage.setItem(WALKTHROUGH_STORAGE_KEY, 'true');
    setHasCompleted(true);
    setIsOpen(false);
    onSkip?.();
  }, [onSkip]);

  const resetWalkthrough = useCallback(() => {
    localStorage.removeItem(WALKTHROUGH_STORAGE_KEY);
    setHasCompleted(false);
  }, []);

  return {
    isOpen,
    hasCompleted,
    startWalkthrough,
    completeWalkthrough,
    skipWalkthrough,
    resetWalkthrough,
  };
}
