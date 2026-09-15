import AsyncStorage from "@react-native-async-storage/async-storage";
import * as FileSystem from "expo-file-system";
import Constants from "expo-constants";

const BASE =
  (Constants.expoConfig?.extra?.apiUrl as string) ||
  "https://coreknow.onrender.com";

const DIR = FileSystem.documentDirectory + "coreknow/";

export type OfflineLesson = {
  id: number;
  title: string;
  text: string;
  syllabus: any;
  mcqs: any[];
  videos: string[];
  version: number;
  downloadedAt: number;
};

async function ensureDir() {
  const info = await FileSystem.getInfoAsync(DIR);
  if (!info.exists) {
    await FileSystem.makeDirectoryAsync(DIR, { intermediates: true });
  }
}

function key(id: number) { return '@ck_lesson_' + id; }

export async function isDownloaded(id: number): Promise<boolean> {
  const v = await AsyncStorage.getItem(key(id));
  return !!v;
}

export async function getOffline(id: number): Promise<OfflineLesson | null> {
  const raw = await AsyncStorage.getItem(key(id));
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export async function listOffline(): Promise<OfflineLesson[]> {
  const keys = await AsyncStorage.getAllKeys();
  const lessonKeys = keys.filter((k) => k.startsWith('@ck_lesson_'));
  if (!lessonKeys.length) return [];
  const rows = await AsyncStorage.multiGet(lessonKeys);
  const out: OfflineLesson[] = [];
  for (const [, v] of rows) {
    if (v) {
      try { out.push(JSON.parse(v)); } catch {}
    }
  }
  return out.sort((a, b) => b.downloadedAt - a.downloadedAt);
}

export async function download(
  lessonId: number,
  userId: string,
  dataSaver: boolean = false
): Promise<{ ok: boolean; error?: string; size_kb?: number }> {
  try {
    await ensureDir();
    const url = BASE + "/api/offline/bundle/" + lessonId + (dataSaver ? "?data_saver=true" : "");
    const r = await fetch(url);
    const d = await r.json();
    if (!d.ok) return { ok: false, error: d.error };

    const payload: OfflineLesson = {
      id: lessonId,
      title: d.lesson.title,
      text: d.lesson.text,
      syllabus: d.syllabus,
      mcqs: d.mcqs || [],
      videos: dataSaver ? [] : (d.videos || []),
      version: d.version || 1,
      downloadedAt: Date.now(),
    };

    const json = JSON.stringify(payload);
    const size_kb = Math.round(json.length / 1024);
    await AsyncStorage.setItem(key(lessonId), json);

    try {
      await fetch(BASE + "/api/offline/track", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          email: String(lessonId),
          tier: String(size_kb),
        }),
      });
    } catch {}

    return { ok: true, size_kb };
  } catch (e: any) {
    return { ok: false, error: e.message };
  }
}

export async function remove(id: number) {
  await AsyncStorage.removeItem(key(id));
}

export async function totalSize(): Promise<number> {
  const all = await listOffline();
  let total = 0;
  for (const l of all) {
    total += JSON.stringify(l).length;
  }
  return Math.round(total / 1024);
}