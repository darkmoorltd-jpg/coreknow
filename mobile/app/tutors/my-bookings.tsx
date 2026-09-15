import { useState, useCallback } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, RefreshControl, Linking } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useFocusEffect } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../lib/store";
import { tutors } from "../../lib/tutors";
import { colors, radius } from "../../constants/theme";

export default function MyBookings() {
  const user = useAuth((s) => s.user);
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    if (!user?.id) return;
    const d = await tutors.bookings(user.id, false);
    if (d.ok) setRows(d.bookings || []);
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
        <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700", marginLeft: 16 }}>My Bookings</Text>
      </View>
      <ScrollView
        contentContainerStyle={{ padding: 20, paddingBottom: 60 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />}
      >
        {loading ? <ActivityIndicator color={colors.accent} /> : null}
        {!loading && rows.length === 0 ? (
          <View style={{ alignItems: "center", paddingVertical: 60 }}>
            <Ionicons name="calendar-outline" size={64} color={colors.textFaint} />
            <Text style={{ color: colors.textDim, marginTop: 16 }}>No bookings yet</Text>
          </View>
        ) : null}
        {rows.map((b) => (
          <View key={b.id} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: b.status === "confirmed" ? colors.green : colors.yellow, padding: 16, marginBottom: 12 }}>
            <Text style={{ color: colors.accentHi, fontSize: 11, letterSpacing: 1.5 }}>{b.subject}</Text>
            <Text style={{ color: colors.text, fontSize: 16, fontWeight: "700", marginTop: 4 }}>{b.topic || "Session"}</Text>
            <Text style={{ color: colors.textDim, fontSize: 13, marginTop: 4 }}>{b.scheduled_at?.slice(0, 16)} · {b.duration_minutes} min</Text>
            <Text style={{ color: colors.green, fontSize: 14, fontWeight: "800", marginTop: 6 }}>N{b.amount} · {b.payment_status}</Text>
            {b.room_url && b.status === 'confirmed' ? (
              <Pressable onPress={() => Linking.openURL(b.room_url)} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 12, alignItems: "center", marginTop: 12 }}>
                <Text style={{ color: "#fff", fontWeight: "800" }}>JOIN SESSION</Text>
              </Pressable>
            ) : null}
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
