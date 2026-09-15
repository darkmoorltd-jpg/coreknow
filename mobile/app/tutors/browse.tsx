import { useState, useCallback } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, RefreshControl } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useFocusEffect } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { tutors } from "../../lib/tutors";
import { colors, radius } from "../../constants/theme";

export default function TutorBrowse() {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    const d = await tutors.list();
    if (d.ok) setRows(d.tutors || []);
    setLoading(false);
  }, []);

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
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16, flex: 1 }}>Find a Tutor</Text>
        <Pressable onPress={() => router.push("/tutors/become")}><Ionicons name="person-add" size={24} color={colors.accent} /></Pressable>
      </View>
      <ScrollView
        contentContainerStyle={{ padding: 20, paddingBottom: 60 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />}
      >
        <Pressable onPress={() => router.push('/tutors/my-bookings')} style={{ backgroundColor: colors.card, borderRadius: radius.md, padding: 14, marginBottom: 20, flexDirection: 'row', alignItems: 'center' }}>
          <Ionicons name="calendar" size={22} color={colors.accent} />
          <Text style={{ color: colors.text, fontWeight: "700", marginLeft: 12, flex: 1 }}>My bookings</Text>
          <Text style={{ color: colors.textFaint, fontSize: 22 }}>›</Text>
        </Pressable>
        <Pressable onPress={() => router.push('/live')} style={{ backgroundColor: colors.card, borderRadius: radius.md, padding: 14, marginBottom: 24, flexDirection: 'row', alignItems: 'center' }}>
          <Ionicons name="videocam" size={22} color={colors.pink} />
          <Text style={{ color: colors.text, fontWeight: "700", marginLeft: 12, flex: 1 }}>Live group classes</Text>
          <Text style={{ color: colors.textFaint, fontSize: 22 }}>›</Text>
        </Pressable>
        {loading ? <ActivityIndicator color={colors.accent} /> : null}
        {!loading && rows.length === 0 ? (
          <View style={{ alignItems: "center", paddingVertical: 60 }}>
            <Ionicons name="people-outline" size={64} color={colors.textFaint} />
            <Text style={{ color: colors.textDim, marginTop: 16 }}>No tutors yet</Text>
            <Text style={{ color: colors.textFaint, fontSize: 13, marginTop: 6, textAlign: "center", paddingHorizontal: 40 }}>Tutors appear here after verification.</Text>
          </View>
        ) : null}
        {rows.map((t) => (
          <Pressable key={t.id} onPress={() => router.push("/tutors/detail/" + t.id)} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 16, marginBottom: 12 }}>
            <View style={{ flexDirection: "row", alignItems: "center" }}>
              <View style={{ width: 56, height: 56, borderRadius: 28, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center" }}>
                <Text style={{ color: "#fff", fontSize: 22, fontWeight: "800" }}>{t.full_name?.[0] || "T"}</Text>
              </View>
              <View style={{ flex: 1, marginLeft: 14 }}>
                <Text style={{ color: colors.text, fontSize: 16, fontWeight: "700" }}>{t.full_name}</Text>
                <Text style={{ color: colors.textDim, fontSize: 12, marginTop: 2 }}>{(t.subjects || []).join(" · ") || t.qualification}</Text>
                <View style={{ flexDirection: "row", alignItems: "center", marginTop: 6, gap: 12 }}>
                  <Text style={{ color: colors.yellow, fontSize: 12, fontWeight: "700" }}>★ {t.avg_rating || "—"}</Text>
                  <Text style={{ color: colors.textFaint, fontSize: 12 }}>{t.total_sessions || 0} sessions</Text>
                </View>
              </View>
              <View style={{ alignItems: "flex-end" }}>
                <Text style={{ color: colors.green, fontSize: 16, fontWeight: "800" }}>N{t.rate_per_hour}</Text>
                <Text style={{ color: colors.textFaint, fontSize: 10 }}>per hour</Text>
              </View>
            </View>
          </Pressable>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
