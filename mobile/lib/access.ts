import { create } from "zustand";
import Constants from "expo-constants";
import { useAuth } from "./store";

const BASE_URL =
  (Constants.expoConfig?.extra?.apiUrl as string) ||
  "https://coreknow.onrender.com";

type AccessState = {
  hasAccess: boolean;
  loading: boolean;
  trialUsed: boolean;
  periodEndsAt: string | null;
  refresh: () => Promise<void>;
};

export const useAccess = create<AccessState>((set) => ({
  hasAccess: false,
  loading: true,
  trialUsed: false,
  periodEndsAt: null,
  refresh: async () => {
    const userId = useAuth.getState().user?.id;
    if (!userId) {
      set({ hasAccess: false, loading: false });
      return;
    }
    try {
      const r = await fetch(BASE_URL + "/api/access/" + userId);
      const d = await r.json();
      const sub = d.subscription || {};
      set({
        hasAccess: d.hasAccess === true,
        loading: false,
        trialUsed: !!sub.trial_ends_at,
        periodEndsAt: sub.current_period_ends_at || sub.trial_ends_at || null,
      });
    } catch (e) {
      set({ hasAccess: false, loading: false });
    }
  },
}));