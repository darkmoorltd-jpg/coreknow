import { useState } from "react";
import { View, Text, Pressable, ScrollView, StatusBar } from "react-native";
import { router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius, font } from "../constants/theme";

// Hardcoded practice questions — replace with API call to /api/practice later
const QUESTIONS = [
  { q: "What is the chemical formula for water?", options: ["H2O", "CO2", "NaCl", "O2"], correct: 0 },
  { q: "Which gas makes up ~78% of air?", options: ["Oxygen", "Nitrogen", "Argon", "CO2"], correct: 1 },
  { q: "What is the atomic number of carbon?", options: ["4", "6", "8", "12"], correct: 1 },
  { q: "Which is a noble gas?", options: ["Hydrogen", "Oxygen", "Helium", "Nitrogen"], correct: 2 },
  { q: "Which is NOT a state of matter?", options: ["Solid", "Liquid", "Gas", "Energy"], correct: 3 },
];

export default function Practice() {
  const [idx, setIdx] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [finished, setFinished] = useState(false);

  const q = QUESTIONS[idx];

  const next = () => {
    const isCorrect = selected === q.correct;
    const newScore = score + (isCorrect ? 1 : 0);
    setScore(newScore);
    if (idx + 1 < QUESTIONS.length) {
      setIdx(idx + 1);
      setSelected(null);
    } else {
      setFinished(true);
    }
  };

  if (finished) {
    const pct = Math.round((score / QUESTIONS.length) * 100);
    return (
      <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center", padding: 24 }}>
        <StatusBar barStyle="light-content" />
        <View style={{ alignItems: "center" }}>
          <View style={{ width: 120, height: 120, borderRadius: 60, backgroundColor: pct >= 70 ? colors.green : colors.yellow, justifyContent: "center", alignItems: "center" }}>
            <Text style={{ fontSize: 56, fontWeight: "800", color: "#000" }}>{pct}%</Text>
          </View>
          <Text style={[font.h1, { color: colors.text, marginTop: 28 }]}>Practice Done</Text>
          <Text style={{ color: colors.textDim, fontSize: 16, marginTop: 8 }}>{score} of {QUESTIONS.length} correct</Text>
          <Text style={{ color: colors.textDim, fontSize: 15, marginTop: 20, textAlign: "center" }}>
            {pct >= 80 ? 'Excellent work! 🎉' : pct >= 60 ? 'Good effort!' : 'Keep practising!'}
          </Text>
          <Pressable onPress={() => { setIdx(0); setScore(0); setSelected(null); setFinished(false); }} style={{ marginTop: 40, backgroundColor: colors.accent, paddingHorizontal: 40, paddingVertical: 16, borderRadius: 999 }}>
            <Text style={{ color: "#fff", fontSize: 16, fontWeight: "700" }}>Try Again</Text>
          </Pressable>
          <Pressable onPress={() => router.back()} style={{ marginTop: 12, padding: 12 }}>
            <Text style={{ color: colors.textDim, fontSize: 15 }}>Back to Home</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />

      {/* Header */}
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20, paddingBottom: 12 }}>
        <Pressable onPress={() => router.back()}>
          <Text style={{ color: colors.text, fontSize: 32 }}>‹</Text>
        </Pressable>
        <Text style={[font.h3, { color: colors.text, marginLeft: 16 }]}>Practice</Text>
        <View style={{ flex: 1 }} />
        <Text style={{ color: colors.cyan, fontSize: 15, fontWeight: "700" }}>Q {idx + 1}/{QUESTIONS.length}</Text>
      </View>

      {/* Progress */}
      <View style={{ marginHorizontal: 20, height: 6, backgroundColor: colors.stroke, borderRadius: 3, marginBottom: 24, overflow: "hidden" }}>
        <View style={{ width: ((idx + 1) / QUESTIONS.length * 100) + "%", height: "100%", backgroundColor: colors.cyan }} />
      </View>

      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 140 }}>
        {/* Question */}
        <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.stroke, padding: 24, marginBottom: 20 }}>
          <Text style={[font.tiny, { color: colors.cyan }]}>PRACTICE</Text>
          <Text style={{ color: colors.text, fontSize: 22, fontWeight: "600", lineHeight: 32, marginTop: 12 }}>{q.q}</Text>
        </View>

        {/* Options */}
        {q.options.map((opt, i) => {
          const isSel = selected === i;
          return (
            <Pressable
              key={i}
              onPress={() => setSelected(i)}
              style={{
                backgroundColor: isSel ? colors.cyan : colors.card,
                borderRadius: radius.md,
                borderWidth: 2,
                borderColor: isSel ? colors.cyan : colors.stroke,
                padding: 20,
                marginBottom: 12,
                flexDirection: "row", alignItems: "center",
              }}
            >
              <View style={{
                width: 44, height: 44, borderRadius: 22,
                backgroundColor: isSel ? 'rgba(0,0,0,0.2)' : colors.cardHi,
                justifyContent: 'center', alignItems: 'center',
              }}>
                <Text style={{ color: isSel ? "#000" : colors.text, fontSize: 18, fontWeight: "800" }}>{String.fromCharCode(65 + i)}</Text>
              </View>
              <Text style={{ flex: 1, marginLeft: 16, color: isSel ? "#000" : colors.text, fontSize: 17, fontWeight: "500" }}>{opt}</Text>
            </Pressable>
          );
        })}
      </ScrollView>

      {/* Next */}
      <View style={{ position: "absolute", bottom: 30, left: 20, right: 20 }}>
        <Pressable onPress={next} disabled={selected === null} style={{ backgroundColor: selected !== null ? colors.cyan : colors.card, borderRadius: radius.md, padding: 20, alignItems: "center", borderWidth: 2, borderColor: selected !== null ? colors.cyan : colors.stroke }}>
          <Text style={{ color: selected !== null ? "#000" : colors.textFaint, fontSize: 16, fontWeight: "800", letterSpacing: 1 }}>
            {idx + 1 === QUESTIONS.length ? 'FINISH' : 'NEXT'}
          </Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}