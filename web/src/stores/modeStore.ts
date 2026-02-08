'use client';

import { create } from 'zustand';

interface ModeState {
  isAdvancedMode: boolean;
  toggleMode: () => void;
  setMode: (advanced: boolean) => void;
}

export const useModeStore = create<ModeState>((set) => ({
  isAdvancedMode: false,
  toggleMode: () => set((state) => ({ isAdvancedMode: !state.isAdvancedMode })),
  setMode: (advanced: boolean) => set({ isAdvancedMode: advanced }),
}));
