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

export const day3 = {
  askFromText: (userId: string, text: string, language: string = 'en') =>
    post('/api/scan/ask', { user_id: userId, text, language }),
  saveMemory: (userId: string, text: string, topic: string) =>
    post('/api/memory/save', { user_id: userId, text, language: topic }),
  getMemory: (userId: string) => get('/api/memory/' + userId),
  recordWeak: (userId: string, subject: string, topic: string, correct: boolean) =>
    post('/api/weak/record', { user_id: userId, subject, topic, correct }),
  getWeak: (userId: string) => get('/api/weak/' + userId),
  emailReport: (parentId: string) => post('/api/parent/email-report/' + parentId, {}),
  setFrequency: (parentId: string, freq: string) =>
    post('/api/parent/set-frequency', { user_id: parentId, text: freq }),
  setLanguage: (userId: string, lang: string) =>
    post('/api/language/set', { user_id: userId, text: lang }),
};