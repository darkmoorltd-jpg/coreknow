import { create } from "zustand";
import { supabase } from "./supabase";

type User = { id: string; email: string; name?: string } | null;

type AuthState = {
  user: User;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<string | null>;
  signUp: (email: string, password: string, name: string) => Promise<string | null>;
  signOut: () => Promise<void>;
  loadUser: () => Promise<void>;
};

export const useAuth = create<AuthState>((set) => ({
  user: null,
  loading: true,

  signIn: async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) return error.message;
    if (data.user) set({ user: { id: data.user.id, email: data.user.email || '' } });
    return null;
  },

  signUp: async (email, password, name) => {
    const { data, error } = await supabase.auth.signUp({
      email, password,
      options: { data: { name } },
    });
    if (error) return error.message;
    if (data.user) set({ user: { id: data.user.id, email: data.user.email || '', name } });
    return null;
  },

  signOut: async () => {
    await supabase.auth.signOut();
    set({ user: null });
  },

  loadUser: async () => {
    const { data } = await supabase.auth.getSession();
    if (data.session?.user) {
      set({
        user: {
          id: data.session.user.id,
          email: data.session.user.email || '',
          name: data.session.user.user_metadata?.name,
        },
        loading: false,
      });
    } else {
      set({ loading: false });
    }
  },
}));