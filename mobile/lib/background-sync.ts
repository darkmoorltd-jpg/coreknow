import { useEffect } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { runSync, getLastSync, setLastSync } from "./sync";
import { useAuth } from "./store";

let TaskManager: any = null;
let BackgroundFetch: any = null;
try {
  TaskManager = require("expo-task-manager");
  BackgroundFetch = require("expo-background-fetch");
} catch (e) {}

const TASK = "coreknow-background-sync";

if (TaskManager && !TaskManager.isTaskDefined(TASK)) {
  TaskManager.defineTask(TASK, async () => {
    try {
      const uid = await AsyncStorage.getItem('@ck_uid');
      if (!uid) return BackgroundFetch.BackgroundFetchResult.NoData;
      const r = await runSync(uid);
      await setLastSync(Date.now());
      return r.updated > 0
        ? BackgroundFetch.BackgroundFetchResult.NewData
        : BackgroundFetch.BackgroundFetchResult.NoData;
    } catch {
      return BackgroundFetch.BackgroundFetchResult.Failed;
    }
  });
}

export function useBackgroundSync() {
  const user = useAuth((s) => s.user);

  useEffect(() => {
    if (!user?.id) return;
    AsyncStorage.setItem('@ck_uid', user.id);

    (async () => {
      if (!BackgroundFetch) return;
      try {
        const status = await BackgroundFetch.getStatusAsync();
        if (status === BackgroundFetch.BackgroundFetchStatus.Restricted) return;
        await BackgroundFetch.registerTaskAsync(TASK, {
          minimumInterval: 60 * 60,  // 1 hour
          stopOnTerminate: false,
          startOnBoot: true,
        });
      } catch (e) {}
    })();
  }, [user]);
}