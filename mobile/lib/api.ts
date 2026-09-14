import Constants from "expo-constants";

const BASE_URL = (Constants.expoConfig?.extra?.apiUrl as string) || "https://coreknow-api.onrender.com";

async function get<T = any>(path: string): Promise<T> {
  const r = await fetch(BASE_URL + path);
  if (!r.ok) throw new Error("API error " + r.status);
  return r.json();
}

async function post<T = any>(path: string, body: any): Promise<T> {
  const r = await fetch(BASE_URL + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error("API error " + r.status);
  return r.json();
}

export type Topic = { id: number; topic_number: number; topic_title: string; subtopics: string[] };

export const api = {
  getSubjects: (exam: string) => get<{ subjects: string[] }>("/api/subjects?exam=" + exam).then((d) => d.subjects),
  getTopics: (subject: string, exam = "JAMB") => get<{ topics: Topic[] }>("/api/subjects/" + subject + "/topics?exam=" + exam).then((d) => d.topics),
  getLesson: (id: number) => get("/api/lessons/" + id),
  chat: (message: string, history: any[] = []) => post("/api/chat", { message, history }),
};