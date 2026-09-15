import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { day4 } from "../lib/day4";
import { colors, radius } from "../constants/theme";

export default function Admin() {
  const [stats, setStats] = useState<any>(null);
  const [errors, setErrors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      day4.analyticsSummary(),
      day4.recentErrors(),
    ]).then(([s, e]) => {
      setStats(s);
      setErrors(e.errors || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const stat = (label: string, value: any, color: string) => (
    <View style={{ flex: 1, backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 16 }}>
      <View style={{ width: 10, height: 10, borderRadius: 5, backgroundColor: color, marginBottom: 12 }} />
      <Text style={{ color: colors.text, fontSize: 26, fontWeight: "800" }}>{value}</Text>
      <Text style={{ color: colors.textFaint, fontSize: 11, marginTop: 4 }}>{label}</Text>
    </View>
  );

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Admin</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        {loading && <ActivityIndicator color={colors.accent} />}
        {stats && (
          <>
            <View style={{ flexDirection: "row", gap: 12, marginBottom: 12 }}>
              {stat("Users", stats.users, colors.accent)}
              {stat("Paid", stats.paid_transactions, colors.green)}
            </View>
            <View style={{ flexDirection: "row", gap: 12, marginBottom: 24 }}>
              {stat("Lessons", stats.total_lessons, colors.yellow)}
              {stat("MCQs", stats.total_mcqs, colors.cyan)}
            </View>

            <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 12 }}>RECENT ERRORS</Text>
            {errors.length === 0 && <Text style={{ color: colors.textDim }}>No errors. 🎉</Text>}
            {errors.slice(0, 10).map((e) => (
              <View key={e.id} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: colors.red, padding: 14, marginBottom: 8 }}>
                <Text style={{ color: colors.text, fontSize: 14, fontWeight: "600" }}>{e.message}</Text>
                <Text style={{ color: colors.textFaint, fontSize: 11, marginTop: 4 }}>{e.platform} · {e.created_at?.slice(0, 16)}</Text>
              </View>
            ))}
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}