import { useState, useEffect } from "react";
import { View, Text, Pressable, ScrollView, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import Constants from "expo-constants";
import { colors, radius } from "../constants/theme";

const BASE =
  (Constants.expoConfig?.extra?.apiUrl as string) ||
  "https://coreknow.onrender.com";

type MCQ = {
  id: number;
  question: string;
  options: string[];
  correct_index: number;
  explanation: string;
};

export default function Practice() {
  const [questions, setQuestions] = useState<MCQ[]>([]);
  const [idx, setIdx] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(true);
  const [finished, setFinished] = useState(false);

  useEffect(() => {
    fetch(BASE + '/api/mcqs?subject=Chemistry&limit=10')
      .then((r) => r.json())
      .then((d) => {
        setQuestions(d.mcqs || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}><ActivityIndicator color={colors.accent} size="large" /></View>;
  }

  if (questions.length === 0) {
    return (
      <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center", padding: 24 }}>
        <Text style={{ color: colors.text, fontSize: 20, textAlign: "center" }}>No questions yet</Text>
      </SafeAreaView>
    );
  }

  const q = questions[idx];

  const next = () => {
    const correct = selected === q.correct_index;
    const newScore = score + (correct ? 1 : 0);
    setScore(newScore);
    if (idx + 1 < questions.length) {
      setIdx(idx + 1);
      setSelected(null);
    } else {
      setFinished(true);
    }
  };

  if (finished) {
    const pct = Math.round((score / questions.length) * 100);
    return (
      <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center", padding: 24 }}>
        <StatusBar barStyle="light-content" />
        <View style={{ alignItems: "center" }}>
          <View style={{ width: 120, height: 120, borderRadius: 60, backgroundColor: pct >= 70 ? colors.green : colors.yellow, justifyContent: "center", alignItems: "center" }}>
            <Text style={{ fontSize: 48, fontWeight: "800", color: "#000" }}>{pct}%</Text>
          </View>
          <Text style={{ color: colors.text, fontSize: 24, fontWeight: "800", marginTop: 20 }}>Practice Done</Text>
          <Text style={{ color: colors.textDim, fontSize: 16, marginTop: 8 }}>{score} of {questions.length} correct</Text>
          <Pressable onPress={() => { setIdx(0); setScore(0); setSelected(null); setFinished(false); }} style={{ marginTop: 30, backgroundColor: colors.accent, paddingHorizontal: 40, paddingVertical: 16, borderRadius: 999 }}>
            <Text style={{ color: "#fff", fontSize: 16, fontWeight: "700" }}>Try Again</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 20, fontWeight: "700", marginLeft: 16, flex: 1 }}>Practice</Text>
        <Text style={{ color: colors.cyan, fontWeight: "700" }}>Q {idx + 1}/{questions.length}</Text>
      </View>
      <View style={{ marginHorizontal: 20, height: 6, backgroundColor: colors.stroke, borderRadius: 3, marginBottom: 20, overflow: "hidden" }}>
        <View style={{ width: ((idx + 1) / questions.length * 100) + "%", height: "100%", backgroundColor: colors.cyan }} />
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 140 }}>
        <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.stroke, padding: 24, marginBottom: 20 }}>
          <Text style={{ color: colors.text, fontSize: 20, fontWeight: "600", lineHeight: 28 }}>{q.question}</Text>
        </View>
        {q.options.map((opt, i) => {
          const isSel = selected === i;
          const isCorrect = i === q.correct_index;
          const showResult = selected !== null;
          let bg = colors.card;
          let border = colors.stroke;
          if (showResult && isCorrect) { bg = colors.green; border = colors.green; }
          else if (isSel && showResult && !isCorrect) { bg = colors.red; border = colors.red; }
          else if (isSel) { bg = colors.cyan; border = colors.cyan; }
          return (
            <Pressable
              key={i}
              onPress={() => selected === null && setSelected(i)}
              style={{ backgroundColor: bg, borderRadius: radius.md, borderWidth: 2, borderColor: border, padding: 18, marginBottom: 12 }}
            >
              <Text style={{ color: showResult && (isCorrect || isSel) ? "#fff" : colors.text, fontSize: 17, fontWeight: "600" }}>{opt}</Text>
            </Pressable>
          );
        })}
        {selected !== null && q.explanation && (
          <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: colors.green, padding: 18, marginTop: 12 }}>
            <Text style={{ color: colors.green, fontSize: 12, fontWeight: "700", letterSpacing: 1, marginBottom: 6 }}>EXPLANATION</Text>
            <Text style={{ color: colors.text, fontSize: 15, lineHeight: 22 }}>{q.explanation}</Text>
          </View>
        )}
      </ScrollView>
      <View style={{ position: "absolute", bottom: 30, left: 20, right: 20 }}>
        <Pressable onPress={next} disabled={selected === null} style={{ backgroundColor: selected !== null ? colors.cyan : colors.card, borderRadius: radius.md, padding: 20, alignItems: "center", borderWidth: 2, borderColor: selected !== null ? colors.cyan : colors.stroke }}>
          <Text style={{ color: selected !== null ? "#000" : colors.textFaint, fontSize: 16, fontWeight: "800" }}>
            {idx + 1 === questions.length ? 'FINISH' : 'NEXT'}
          </Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}