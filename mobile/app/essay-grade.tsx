import { useState } from "react";
import { View, Text, TextInput, Pressable, ScrollView, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../lib/store";
import { day6 } from "../lib/day6";
import { colors, radius } from "../constants/theme";

export default function EssayGrade() {
  const user = useAuth((s) => s.user);
  const [subject, setSubject] = useState("Chemistry");
  const [essay, setEssay] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const grade = async () => {
    if (!essay.trim()) { setError('Write your essay'); return; }
    setLoading(true); setError(null); setResult(null);
    const d = await day6.gradeEssay(user?.id || '', subject, essay, 100);
    setLoading(false);
    if (!d.ok) { setError(d.error); return; }
    setResult(d.result);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Essay Grading</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        <Text style={{ color: colors.textFaint, fontSize: 11, fontWeight: "600", letterSpacing: 1.5, marginBottom: 8 }}>SUBJECT</Text>
        <TextInput value={subject} onChangeText={setSubject} style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 14, color: colors.text, fontSize: 15, marginBottom: 16 }} />
        <Text style={{ color: colors.textFaint, fontSize: 11, fontWeight: "600", letterSpacing: 1.5, marginBottom: 8 }}>YOUR ESSAY</Text>
        <TextInput
          value={essay}
          onChangeText={setEssay}
          placeholder="Paste or type your essay here..."
          placeholderTextColor={colors.textFaint}
          multiline
          style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 16, color: colors.text, fontSize: 15, minHeight: 200, textAlignVertical: "top", marginBottom: 16 }}
        />
        {error ? <Text style={{ color: colors.red, fontSize: 14, marginBottom: 12, textAlign: "center" }}>{error}</Text> : null}
        <Pressable onPress={grade} disabled={loading} style={{ backgroundColor: colors.green, borderRadius: radius.md, padding: 18, alignItems: "center", marginBottom: 24 }}>
          {loading ? <ActivityIndicator color="#000" /> :
            <Text style={{ color: "#000", fontSize: 16, fontWeight: "800", letterSpacing: 1 }}>GRADE MY ESSAY</Text>}
        </Pressable>
        {result ? (
          <>
            <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 2, borderColor: colors.green, padding: 24, alignItems: "center", marginBottom: 16 }}>
              <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5 }}>SCORE</Text>
              <Text style={{ color: colors.green, fontSize: 64, fontWeight: "800" }}>{result.score}/100</Text>
            </View>
            <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: colors.accent, padding: 18, marginBottom: 12 }}>
              <Text style={{ color: colors.accentHi, fontSize: 11, fontWeight: "700", letterSpacing: 1.5, marginBottom: 8 }}>FEEDBACK</Text>
              <Text style={{ color: colors.text, fontSize: 15, lineHeight: 23 }}>{result.feedback}</Text>
            </View>
            {(result.strengths || []).length > 0 ? (
              <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: colors.green, padding: 18, marginBottom: 12 }}>
                <Text style={{ color: colors.green, fontSize: 11, fontWeight: "700", letterSpacing: 1.5, marginBottom: 8 }}>STRENGTHS</Text>
                {result.strengths.map((s: string, i: number) => (
                  <Text key={i} style={{ color: colors.text, fontSize: 14, lineHeight: 22, marginBottom: 4 }}>✓ {s}</Text>
                ))}
              </View>
            ) : null}
            {(result.improvements || []).length > 0 ? (
              <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: colors.yellow, padding: 18 }}>
                <Text style={{ color: colors.yellow, fontSize: 11, fontWeight: "700", letterSpacing: 1.5, marginBottom: 8 }}>IMPROVEMENTS</Text>
                {result.improvements.map((s: string, i: number) => (
                  <Text key={i} style={{ color: colors.text, fontSize: 14, lineHeight: 22, marginBottom: 4 }}>→ {s}</Text>
                ))}
              </View>
            ) : null}
          </>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}