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

export const day8 = {
  forgotPassword: (email: string) =>
    post('/api/auth/forgot-password', { email }),
  resetPassword: (email: string, code: string, newPassword: string) =>
    post('/api/auth/reset-password', { email, code, new_password: newPassword }),
  sendVerification: (userId: string, email: string) =>
    post('/api/auth/send-verification', { user_id: userId, email }),
  verifyEmail: (userId: string, code: string) =>
    post('/api/auth/verify-email', { user_id: userId, code }),
  getVariant: (testKey: string, userId: string) =>
    get('/api/ab/variant/' + testKey + '/' + userId),
  convert: (testKey: string, userId: string) =>
    post('/api/ab/convert/' + testKey + '/' + userId, {}),
  results: () => get('/api/ab/results'),
};
