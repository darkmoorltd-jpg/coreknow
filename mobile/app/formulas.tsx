import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { day2 } from "../lib/day2";
import { colors, radius } from "../constants/theme";

export default function Formulas() {
  const [sheets, setSheets] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    day2.getFormulas().then((d) => {
      setSheets(d.sheets || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Formula Sheets</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        {loading && <ActivityIndicator color={colors.accent} />}
        {sheets.map((s) => (
          <View key={s.id} style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.stroke, padding: 20, marginBottom: 20 }}>
            <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 4 }}>
              <Text style={{ color: colors.accentHi, fontSize: 11, fontWeight: "600", letterSpacing: 1.5 }}>{s.subject.toUpperCase()}</Text>
            </View>
            <Text style={{ color: colors.text, fontSize: 22, fontWeight: "800", marginBottom: 16 }}>{s.topic_title}</Text>
            {(s.formulas || []).map((f: any, i: number) => (
              <View key={i} style={{ marginBottom: 14 }}>
                <Text style={{ color: colors.textDim, fontSize: 13, fontWeight: "600" }}>{f.name}</Text>
                <View style={{ backgroundColor: colors.bg2, borderRadius: radius.sm, borderLeftWidth: 3, borderLeftColor: colors.accent, padding: 12, marginTop: 4 }}>
                  <Text style={{ color: colors.accentLt, fontSize: 15, fontWeight: "600", fontFamily: "monospace" }}>{f.formula}</Text>
                </View>
                {f.note && (
                  <Text style={{ color: colors.textFaint, fontSize: 12, marginTop: 4 }}>{f.note}</Text>
                )}
              </View>
            ))}
            {s.notes && (
              <View style={{ borderTopWidth: 1, borderTopColor: colors.stroke, paddingTop: 12, marginTop: 4 }}>
                <Text style={{ color: colors.textDim, fontSize: 13, lineHeight: 20 }}>{s.notes}</Text>
              </View>
            )}
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}