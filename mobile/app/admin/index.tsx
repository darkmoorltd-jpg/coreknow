import { useState, useCallback } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, RefreshControl } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useFocusEffect } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../lib/store";
import { admin } from "../../lib/admin";
import { colors, radius } from "../../constants/theme";

const STATUS_COLOR: Record<string, string> = {
  published: colors.green,
  draft: colors.yellow,
  scheduled: colors.cyan,
};

export default function AdminHome() {
  const user = useAuth((s) => s.user);
  const [lessons, setLessons] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    if (!user?.id) { setLoading(false); return; }
    const d = await admin.listLessons(user.id);
    if (d.ok) setLessons(d.lessons || []);
    setLoading(false);
  }, [user]);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16, flex: 1 }}>Admin</Text>
        <Pressable onPress={() => router.push("/admin/analytics")}><Ionicons name="bar-chart" size={24} color={colors.accent} /></Pressable>
      </View>
      <ScrollView
        contentContainerStyle={{ padding: 20, paddingBottom: 60 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />}
      >
        <View style={{ flexDirection: "row", gap: 12, marginBottom: 24 }}>
          <Pressable onPress={() => router.push("/admin/edit")} style={{ flex: 1, backgroundColor: colors.accent, borderRadius: radius.md, padding: 18, alignItems: "center" }}>
            <Ionicons name="create" size={24} color="#fff" />
            <Text style={{ color: "#fff", fontWeight: "700", marginTop: 6, fontSize: 13 }}>New Lesson</Text>
          </Pressable>
          <Pressable onPress={() => router.push("/admin/bulk")} style={{ flex: 1, backgroundColor: colors.violet, borderRadius: radius.md, padding: 18, alignItems: "center" }}>
            <Ionicons name="layers" size={24} color="#fff" />
            <Text style={{ color: "#fff", fontWeight: "700", marginTop: 6, fontSize: 13 }}>Bulk Import</Text>
          </Pressable>
        </View>

        {loading && <ActivityIndicator color={colors.accent} />}
        {!loading && lessons.length === 0 && (
          <Text style={{ color: colors.textDim, textAlign: "center", marginTop: 40 }}>No lessons found.</Text>
        )}

        {lessons.map((l) => (
          <Pressable key={l.id} onPress={() => router.push("/admin/edit?lesson_id=" + l.id)} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 16, marginBottom: 10 }}>
            <View style={{ flexDirection: "row", alignItems: "center" }}>
              <View style={{ width: 8, height: 40, borderRadius: 4, backgroundColor: STATUS_COLOR[l.status] || colors.textFaint, marginRight: 12 }} />
              <View style={{ flex: 1 }}>
                <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1 }}>{l.exam} · {l.subject} · TOPIC {l.topic_number}</Text>
                <Text style={{ color: colors.text, fontSize: 15, fontWeight: "600", marginTop: 4 }} numberOfLines={1}>{l.title}</Text>
                <Text style={{ color: STATUS_COLOR[l.status] || colors.textDim, fontSize: 11, fontWeight: "700", marginTop: 4 }}>{l.status.toUpperCase()} · v{l.version}</Text>
              </View>
              <Text style={{ color: colors.textFaint, fontSize: 22 }}>›</Text>
            </View>
          </Pressable>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
