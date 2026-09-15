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

export const day2 = {
  getFormulas: (subject: string = '') =>
    get('/api/formulas' + (subject ? '?subject=' + encodeURIComponent(subject) : '')),
  getPastQuestions: (exam: string, subject: string, year: number) =>
    get('/api/past-questions?exam=' + exam + '&subject=' + subject + '&year=' + year),
  getPastYears: (exam: string, subject: string) =>
    get('/api/past-questions/years?exam=' + exam + '&subject=' + subject),
  generateQuestions: (subject: string, topic_number: number, topic_title: string, count: number, user_id: string) =>
    post('/api/ai/questions/generate', { subject, topic_number, topic_title, count, user_id }),
  importLesson: (data: any) => post('/api/import/lesson', data),
  importStats: () => get('/api/import/stats'),
};