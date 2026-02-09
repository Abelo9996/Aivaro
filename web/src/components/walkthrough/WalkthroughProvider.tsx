'use client';

import { createContext, useContext, ReactNode } from 'react';
import Walkthrough from './Walkthrough';
import { WALKTHROUGH_STEPS } from './walkthroughSteps';
import { useWalkthrough } from './useWalkthrough';

interface WalkthroughContextValue {
  isOpen: boolean;
  hasCompleted: boolean;
  startWalkthrough: () => void;
  resetWalkthrough: () => void;
}

const WalkthroughContext = createContext<WalkthroughContextValue | null>(null);

export function useWalkthroughContext() {
  const context = useContext(WalkthroughContext);
  if (!context) {
    throw new Error('useWalkthroughContext must be used within WalkthroughProvider');
  }
  return context;
}

interface WalkthroughProviderProps {
  children: ReactNode;
  autoStart?: boolean;
}

export function WalkthroughProvider({ children, autoStart = true }: WalkthroughProviderProps) {
  const {
    isOpen,
    hasCompleted,
    startWalkthrough,
    completeWalkthrough,
    skipWalkthrough,
    resetWalkthrough,
  } = useWalkthrough({ autoStart });

  return (
    <WalkthroughContext.Provider
      value={{
        isOpen,
        hasCompleted,
        startWalkthrough,
        resetWalkthrough,
      }}
    >
      {children}
      <Walkthrough
        steps={WALKTHROUGH_STEPS}
        isOpen={isOpen}
        onComplete={completeWalkthrough}
        onSkip={skipWalkthrough}
      />
    </WalkthroughContext.Provider>
  );
}
