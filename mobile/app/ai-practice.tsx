import { useState } from "react";
import { View, Text, Pressable, ScrollView, ActivityIndicator, TextInput, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../lib/store";
import { day2 } from "../lib/day2";
import { colors, radius } from "../constants/theme";

type MCQ = {
  id: number;
  question: string;
  options: string[];
  correct_index: number;
  explanation: string;
};

export default function AIPractice() {
  const user = useAuth((s) => s.user);
  const [topic, setTopic] = useState("");
  const [questions, setQuestions] = useState<MCQ[]>([]);
  const [idx, setIdx] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [score, setScore] = useState(0);
  const [loading, setLoading] = useState(false);
  const [finished, setFinished] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generate = async () => {
    if (!topic.trim()) { setError('Enter a topic'); return; }
    setLoading(true); setError(null);
    setQuestions([]); setIdx(0); setScore(0); setSelected(null); setFinished(false);
    try {
      const d = await day2.generateQuestions(
        'Chemistry', 0, topic.trim(), 10, user?.id || ''
      );
      if (!d.ok) { setError(d.error || 'Failed'); setLoading(false); return; }
      setQuestions(d.questions || []);
      setLoading(false);
    } catch (e: any) {
      setError(e.message);
      setLoading(false);
    }
  };

  const next = () => {
    const correct = selected === questions[idx].correct_index;
    const newScore = score + (correct ? 1 : 0);
    setScore(newScore);
    if (idx + 1 < questions.length) {
      setIdx(idx + 1);
      setSelected(null);
    } else {
      setFinished(true);
    }
  };

  if (questions.length === 0) {
    return (
      <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
        <StatusBar barStyle="light-content" />
        <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
          <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
          <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>AI Practice</Text>
        </View>
        <ScrollView contentContainerStyle={{ padding: 20 }}>
          <View style={{ alignItems: "center", marginBottom: 32 }}>
            <View style={{ width: 96, height: 96, borderRadius: 48, backgroundColor: colors.violet, justifyContent: "center", alignItems: "center" }}>
              <Ionicons name="sparkles" size={44} color="#fff" />
            </View>
            <Text style={{ color: colors.text, fontSize: 24, fontWeight: "800", marginTop: 20 }}>AI Question Generator</Text>
            <Text style={{ color: colors.textDim, fontSize: 15, marginTop: 8, textAlign: "center", lineHeight: 22 }}>
              Type any topic. Get 10 fresh questions instantly.
            </Text>
          </View>
          <Text style={{ color: colors.textFaint, fontSize: 11, fontWeight: "600", letterSpacing: 1.5, marginBottom: 8 }}>TOPIC</Text>
          <TextInput
            value={topic}
            onChangeText={setTopic}
            placeholder="e.g. Solubility"
            placeholderTextColor={colors.textFaint}
            style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 16, color: colors.text, fontSize: 16, marginBottom: 20 }}
          />
          {error && <Text style={{ color: colors.red, fontSize: 14, marginBottom: 12, textAlign: "center" }}>{error}</Text>}
          <Pressable onPress={generate} disabled={loading} style={{ backgroundColor: colors.violet, borderRadius: radius.md, padding: 20, alignItems: "center" }}>
            {loading ? <ActivityIndicator color="#fff" /> :
              <Text style={{ color: "#fff", fontSize: 16, fontWeight: "800", letterSpacing: 1 }}>GENERATE 10 QUESTIONS</Text>}
          </Pressable>
        </ScrollView>
      </SafeAreaView>
    );
  }

  if (finished) {
    const pct = Math.round((score / questions.length) * 100);
    return (
      <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center", padding: 24 }}>
        <StatusBar barStyle="light-content" />
        <View style={{ alignItems: "center" }}>
          <View style={{ width: 120, height: 120, borderRadius: 60, backgroundColor: pct >= 70 ? colors.green : colors.yellow, justifyContent: "center", alignItems: "center" }}>
            <Text style={{ fontSize: 48, fontWeight: "800", color: "#000" }}>{pct}%</Text>
          </View>
          <Text style={{ color: colors.text, fontSize: 24, fontWeight: "800", marginTop: 20 }}>Session Complete</Text>
          <Text style={{ color: colors.textDim, fontSize: 16, marginTop: 8 }}>{score} of {questions.length} correct</Text>
          <Pressable onPress={() => { setQuestions([]); setIdx(0); setScore(0); setSelected(null); setFinished(false); }} style={{ marginTop: 30, backgroundColor: colors.violet, paddingHorizontal: 40, paddingVertical: 16, borderRadius: 999 }}>
            <Text style={{ color: "#fff", fontSize: 16, fontWeight: "700" }}>New Session</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }

  const q = questions[idx];
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 20, fontWeight: "700", marginLeft: 16, flex: 1 }}>AI Practice</Text>
        <Text style={{ color: colors.violet, fontWeight: "700" }}>Q {idx + 1}/{questions.length}</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 140 }}>
        <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.stroke, padding: 24, marginBottom: 20 }}>
          <Text style={{ color: colors.violet, fontSize: 11, fontWeight: "700", letterSpacing: 1.5, marginBottom: 10 }}>AI-GENERATED</Text>
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
          else if (isSel) { bg = colors.violet; border = colors.violet; }
          return (
            <Pressable key={i} onPress={() => selected === null && setSelected(i)} style={{ backgroundColor: bg, borderRadius: radius.md, borderWidth: 2, borderColor: border, padding: 18, marginBottom: 12 }}>
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
        <Pressable onPress={next} disabled={selected === null} style={{ backgroundColor: selected !== null ? colors.violet : colors.card, borderRadius: radius.md, padding: 20, alignItems: "center", borderWidth: 2, borderColor: selected !== null ? colors.violet : colors.stroke }}>
          <Text style={{ color: selected !== null ? "#fff" : colors.textFaint, fontSize: 16, fontWeight: "800" }}>
            {idx + 1 === questions.length ? 'FINISH' : 'NEXT'}
          </Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}