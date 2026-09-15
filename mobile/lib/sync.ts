import AsyncStorage from "@react-native-async-storage/async-storage";
import Constants from "expo-constants";
import { listOffline, getOffline, download, remove } from "./offline";

const BASE =
  (Constants.expoConfig?.extra?.apiUrl as string) ||
  "https://coreknow.onrender.com";

export async function runSync(userId: string): Promise<{ updated: number; errors: number }> {
  let updated = 0;
  let errors = 0;

  try {
    const mRes = await fetch(BASE + "/api/offline/manifest/" + userId);
    const manifest = await mRes.json();
    const versions: Record<number, number> = {};
    for (const row of manifest.versions || []) {
      versions[row.lesson_id] = row.version;
    }

    const offline = await listOffline();
    for (const l of offline) {
      const serverV = versions[l.id] || 1;
      if (serverV > l.version) {
        const r = await download(l.id, userId, false);
        if (r.ok) updated++;
        else errors++;
      }
    }

    try {
      await fetch(BASE + "/api/sync/touch/" + userId + "?items=" + updated, { method: "POST" });
    } catch {}
  } catch (e) {
    errors++;
  }

  return { updated, errors };
}

export async function getLastSync(): Promise<number | null> {
  const v = await AsyncStorage.getItem('@ck_last_sync');
  return v ? parseInt(v) : null;
}

export async function setLastSync(ts: number) {
  await AsyncStorage.setItem('@ck_last_sync', String(ts));
}