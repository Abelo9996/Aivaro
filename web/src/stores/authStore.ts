'use client';

import { create } from 'zustand';
import { api } from '@/lib/api';
import type { User } from '@/types';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  updateUser: (data: Partial<User>) => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    const response = await api.login(email, password);
    api.setToken(response.access_token);
    set({ user: response.user, isAuthenticated: true });
  },

  signup: async (email: string, password: string, fullName?: string) => {
    const response = await api.signup(email, password, fullName);
    if (response.requires_verification) {
      // Don't log in — throw so the UI can show verification message
      throw { requiresVerification: true, email: response.email, message: response.message };
    }
    api.setToken(response.access_token);
    set({ user: response.user, isAuthenticated: true });
  },

  logout: () => {
    api.setToken(null);
    set({ user: null, isAuthenticated: false });
  },

  checkAuth: async () => {
    const token = api.getToken();
    if (!token) {
      set({ isLoading: false, isAuthenticated: false });
      return;
    }

    try {
      const user = await api.getMe();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      api.setToken(null);
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  updateUser: async (data: Partial<User>) => {
    const user = await api.updateMe(data as any);
    set({ user });
  },
}));
