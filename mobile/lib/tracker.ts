import Constants from "expo-constants";
import { useAuth } from "./store";

const BASE_URL = (Constants.expoConfig?.extra?.apiUrl as string) ||
  "https://coreknow.onrender.com";

export async function track(event: string, data: Record<string, any> = {}) {
  try {
    const userId = useAuth.getState().user?.id || "";
    await fetch(BASE_URL + "/api/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event, user_id: userId, data }),
    });
  } catch (e) {
    // silent
  }
}
