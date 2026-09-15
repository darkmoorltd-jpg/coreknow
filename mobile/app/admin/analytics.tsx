import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../lib/store";
import { admin } from "../../lib/admin";
import { colors, radius } from "../../constants/theme";

export default function AdminAnalytics() {
  const user = useAuth((s) => s.user);
  const [top, setTop] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) { setLoading(false); return; }
    admin.analytics(user.id).then((d) => {
      if (d.ok) setTop(d.top || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [user]);

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700", marginLeft: 16 }}>Content Analytics</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        <Text style={{ color: colors.textDim, fontSize: 13, marginBottom: 16 }}>Top lessons by read count (last 30 days)</Text>
        {loading && <ActivityIndicator color={colors.accent} />}
        {!loading && top.length === 0 && (
          <View style={{ alignItems: "center", paddingVertical: 60 }}>
            <Ionicons name="bar-chart-outline" size={56} color={colors.textFaint} />
            <Text style={{ color: colors.textDim, marginTop: 16 }}>No reads recorded yet</Text>
          </View>
        )}
        {top.map((row, i) => {
          const rate = row.reads > 0 ? Math.round(row.completed / row.reads * 100) : 0;
          return (
            <View key={row.lesson_id} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 16, marginBottom: 10 }}>
              <View style={{ flexDirection: "row", alignItems: "center" }}>
                <Text style={{ color: colors.textFaint, fontSize: 12, fontWeight: "800", width: 28 }}>#{i + 1}</Text>
                <View style={{ flex: 1 }}>
                  <Text style={{ color: colors.text, fontSize: 15, fontWeight: "600" }} numberOfLines={1}>{row.title}</Text>
                  <Text style={{ color: colors.textFaint, fontSize: 11, marginTop: 4 }}>{row.reads} reads · {rate}% completed · {row.avg_seconds}s avg</Text>
                </View>
              </View>
              <View style={{ height: 6, backgroundColor: colors.stroke, borderRadius: 3, marginTop: 10, overflow: "hidden" }}>
                <View style={{ width: rate + "%", height: "100%", backgroundColor: rate > 60 ? colors.green : rate > 30 ? colors.yellow : colors.red }} />
              </View>
            </View>
          );
        })}
      </ScrollView>
    </SafeAreaView>
  );
}
