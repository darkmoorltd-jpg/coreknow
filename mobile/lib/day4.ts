import Constants from "expo-constants";

const BASE =
  (Constants.expoConfig?.extra?.apiUrl as string) ||
  "https://coreknow.onrender.com";

async function get(path: string) {
  const r = await fetch(BASE + path);
  return r.json();
}

async function post(path: string, body: any) {
  const r = await fetch(BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return r.json();
}

export const day4 = {
  registerPush: (userId: string, token: string, platform: string) =>
    post('/api/push/register', { user_id: userId, token, platform }),
  getLeaderboard: () => get('/api/leaderboard'),
  addPoints: (userId: string, points: number) =>
    post('/api/leaderboard/add-points', { user_id: userId, points }),
  savePrefs: (userId: string, theme: string, biometricEnabled: boolean) =>
    post('/api/prefs/save', { user_id: userId, theme, biometric_enabled: biometricEnabled }),
  getPrefs: (userId: string) => get('/api/prefs/' + userId),
  reportError: (userId: string, message: string, stack: string, platform: string, version: string) =>
    post('/api/errors/report', { user_id: userId, message, stack, platform, app_version: version }),
  recentErrors: () => get('/api/errors/recent'),
  analyticsSummary: () => get('/api/analytics/summary'),
};