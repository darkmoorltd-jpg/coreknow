import { useState } from "react";
import { View, Text, TextInput, Pressable, ScrollView, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { day6 } from "../lib/day6";
import { speak, stopSpeaking } from "../lib/audio";
import { colors, radius } from "../constants/theme";

export default function ELI5() {
  const [concept, setConcept] = useState("");
  const [explanation, setExplanation] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const explain = async () => {
    if (!concept.trim()) { setError('Type a concept'); return; }
    setLoading(true); setError(null); setExplanation('');
    const d = await day6.eli5(concept.trim());
    setLoading(false);
    if (!d.ok) { setError(d.error); return; }
    setExplanation(d.explanation);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => { stopSpeaking(); router.back(); }}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Explain Simply</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        <View style={{ alignItems: "center", marginBottom: 24 }}>
          <View style={{ width: 80, height: 80, borderRadius: 40, backgroundColor: colors.cyan, justifyContent: "center", alignItems: "center" }}>
            <Text style={{ fontSize: 40 }}>🧒</Text>
          </View>
          <Text style={{ color: colors.text, fontSize: 18, fontWeight: "700", marginTop: 16, textAlign: "center" }}>
            Explain like I am 10
          </Text>
        </View>
        <TextInput
          value={concept}
          onChangeText={setConcept}
          placeholder="e.g. Photosynthesis, Ohms law, Redox"
          placeholderTextColor={colors.textFaint}
          style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 16, color: colors.text, fontSize: 16, marginBottom: 16 }}
        />
        {error ? <Text style={{ color: colors.red, fontSize: 14, marginBottom: 12, textAlign: "center" }}>{error}</Text> : null}
        <Pressable onPress={explain} disabled={loading} style={{ backgroundColor: colors.cyan, borderRadius: radius.md, padding: 18, alignItems: "center", marginBottom: 24 }}>
          {loading ? <ActivityIndicator color="#000" /> :
            <Text style={{ color: "#000", fontSize: 16, fontWeight: "800", letterSpacing: 1 }}>EXPLAIN SIMPLY</Text>}
        </Pressable>
        {explanation ? (
          <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderLeftWidth: 4, borderLeftColor: colors.cyan, padding: 20 }}>
            <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 12 }}>
              <Text style={{ color: colors.cyan, fontSize: 12, fontWeight: "700", letterSpacing: 1 }}>SIMPLE EXPLANATION</Text>
              <Pressable onPress={() => speak(explanation)}>
                <Ionicons name="volume-high" size={20} color={colors.cyan} />
              </Pressable>
            </View>
            <Text style={{ color: colors.text, fontSize: 16, lineHeight: 26 }}>{explanation}</Text>
          </View>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}