import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { day8 } from "../lib/day8";
import { colors, radius } from "../constants/theme";

export default function ABResults() {
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    day8.results().then((d) => {
      setResults(d.results || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>A/B Tests</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        {loading && <ActivityIndicator color={colors.accent} />}
        {results.map((r) => (
          <View key={r.test_key} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 18, marginBottom: 14 }}>
            <Text style={{ color: colors.text, fontSize: 16, fontWeight: "700" }}>{r.test_key}</Text>
            <View style={{ height: 1, backgroundColor: colors.stroke, marginVertical: 12 }} />
            {Object.entries(r.variants).map(([v, c]: any) => {
              const rate = c.assigned > 0 ? Math.round(c.converted / c.assigned * 100) : 0;
              return (
                <View key={v} style={{ marginBottom: 12 }}>
                  <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 4 }}>
                    <Text style={{ color: colors.accentHi, fontSize: 14, fontWeight: "700" }}>{v}</Text>
                    <Text style={{ color: colors.text, fontSize: 14 }}>{rate}% conversion</Text>
                  </View>
                  <View style={{ height: 6, backgroundColor: colors.stroke, borderRadius: 3, overflow: "hidden" }}>
                    <View style={{ width: rate + "%", height: "100%", backgroundColor: rate > 30 ? colors.green : colors.accent }} />
                  </View>
                  <Text style={{ color: colors.textFaint, fontSize: 11, marginTop: 4 }}>{c.assigned} assigned · {c.converted} converted</Text>
                </View>
              );
            })}
          </View>
        ))}
        {!loading && results.length === 0 && (
          <View style={{ alignItems: "center", paddingVertical: 60 }}>
            <Ionicons name="flask-outline" size={64} color={colors.textFaint} />
            <Text style={{ color: colors.textDim, fontSize: 16, marginTop: 16 }}>No active tests</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
