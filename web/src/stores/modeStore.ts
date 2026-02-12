'use client';

import { create } from 'zustand';

interface ModeState {
  isAdvancedMode: boolean;
  toggleMode: () => void;
  setMode: (advanced: boolean) => void;
}

// Always advanced mode - no toggling needed
export const useModeStore = create<ModeState>((set) => ({
  isAdvancedMode: true, // Always true now
  toggleMode: () => {}, // No-op
  setMode: () => {}, // No-op
}));
