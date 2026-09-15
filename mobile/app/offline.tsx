import { useState, useCallback } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useFocusEffect } from "expo-router";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../lib/store";
import { listOffline, remove, totalSize, OfflineLesson } from "../lib/offline";
import { runSync, getLastSync, setLastSync } from "../lib/sync";
import { colors, radius } from "../constants/theme";

export default function Offline() {
  const user = useAuth((s) => s.user);
  const [items, setItems] = useState<OfflineLesson[]>([]);
  const [sizeKb, setSizeKb] = useState(0);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [lastSync, setLastSyncState] = useState<number | null>(null);

  const load = useCallback(async () => {
    const all = await listOffline();
    setItems(all);
    setSizeKb(await totalSize());
    setLastSyncState(await getLastSync());
    setLoading(false);
  }, []);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  const del = (id: number, title: string) => {
    Alert.alert('Remove download', '"' + title + '"?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Remove', style: 'destructive', onPress: async () => {
        await remove(id);
        if (user?.id) {
          try { await fetch("https://coreknow.onrender.com/api/offline/remove/" + user.id + "/" + id, { method: "DELETE" }); } catch {}
        }
        load();
      }},
    ]);
  };

  const doSync = async () => {
    if (!user?.id) return;
    setSyncing(true);
    const r = await runSync(user.id);
    await setLastSync(Date.now());
    setSyncing(false);
    Alert.alert('Sync complete', r.updated + ' updated · ' + r.errors + ' errors');
    load();
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16, flex: 1 }}>Offline Library</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 2, borderColor: colors.strokeHi, padding: 20, marginBottom: 20 }}>
          <View style={{ position: "absolute", left: 0, top: 20, bottom: 20, width: 4, backgroundColor: colors.green, borderTopRightRadius: 4, borderBottomRightRadius: 4 }} />
          <Text style={{ color: colors.textFaint, fontSize: 11, fontWeight: "600", letterSpacing: 1.5 }}>STORED ON DEVICE</Text>
          <Text style={{ color: colors.text, fontSize: 32, fontWeight: "800", marginTop: 6 }}>{items.length} lessons · {sizeKb} KB</Text>
          {lastSync ? (
            <Text style={{ color: colors.textDim, fontSize: 13, marginTop: 6 }}>
              Last sync: {new Date(lastSync).toLocaleString()}
            </Text>
          ) : null}
        </View>

        <Pressable onPress={doSync} disabled={syncing} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 16, alignItems: "center", marginBottom: 24, flexDirection: "row", justifyContent: "center" }}>
          {syncing ? <ActivityIndicator color="#fff" /> : (
            <>
              <Ionicons name="sync" size={20} color="#fff" />
              <Text style={{ color: "#fff", fontWeight: "800", marginLeft: 8, letterSpacing: 1 }}>SYNC NOW</Text>
            </>
          )}
        </Pressable>

        {loading && <ActivityIndicator color={colors.accent} />}
        {!loading && items.length === 0 && (
          <View style={{ alignItems: "center", paddingVertical: 60 }}>
            <Ionicons name="cloud-download-outline" size={64} color={colors.textFaint} />
            <Text style={{ color: colors.textDim, fontSize: 16, marginTop: 16 }}>No lessons downloaded</Text>
            <Text style={{ color: colors.textFaint, fontSize: 13, marginTop: 6, textAlign: "center", paddingHorizontal: 40 }}>
              Open any lesson and tap the download icon to save it for offline use.
            </Text>
          </View>
        )}

        {items.map((l) => (
          <View key={l.id} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 16, marginBottom: 10, flexDirection: "row", alignItems: "center" }}>
            <Pressable onPress={() => router.push("/lesson/" + l.id)} style={{ flex: 1 }}>
              <Text style={{ color: colors.text, fontSize: 16, fontWeight: "600" }} numberOfLines={2}>{l.title}</Text>
              <Text style={{ color: colors.textFaint, fontSize: 12, marginTop: 4 }}>
                {l.mcqs.length} questions · v{l.version}
              </Text>
            </Pressable>
            <Pressable onPress={() => del(l.id, l.title)} style={{ padding: 10 }}>
              <Ionicons name="trash-outline" size={22} color={colors.red} />
            </Pressable>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}