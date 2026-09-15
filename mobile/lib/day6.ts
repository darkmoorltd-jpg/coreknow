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

export const day6 = {
  voiceAsk: (userId: string, transcript: string, language: string, durationMs: number) =>
    post('/api/voice/ask', { user_id: userId, transcript, language, duration_ms: durationMs }),
  voiceHistory: (userId: string) => get('/api/voice/history/' + userId),
  eli5: (concept: string, subject: string = '') =>
    post('/api/eli5', { concept, subject }),
  gradeEssay: (userId: string, subject: string, essayText: string, maxScore: number) =>
    post('/api/essay/grade', { user_id: userId, subject, essay_text: essayText, max_score: maxScore }),
  getCaptions: (lessonId: number) => get('/api/captions/' + lessonId),
  generateCaptions: (lessonId: number, lessonTitle: string, lessonText: string) =>
    post('/api/captions/generate', { lesson_id: lessonId, lesson_title: lessonTitle, lesson_text: lessonText }),
};