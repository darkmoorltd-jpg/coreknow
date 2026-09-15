import { useState } from "react";
import { View, Text, ScrollView, Pressable, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius, font } from "../../constants/theme";

const QUESTIONS = [
  {
    q: "What is the chemical formula for water?",
    options: [
      { letter: "A", text: "H2O", correct: true },
      { letter: "B", text: "CO2", correct: false },
      { letter: "C", text: "NaCl", correct: false },
      { letter: "D", text: "O2", correct: false },
    ],
  },
  {
    q: "Which gas makes up ~78% of air?",
    options: [
      { letter: "A", text: "Oxygen", correct: false },
      { letter: "B", text: "Nitrogen", correct: true },
      { letter: "C", text: "Argon", correct: false },
      { letter: "D", text: "CO2", correct: false },
    ],
  },
];

export default function ExamMode() {
  const [idx, setIdx] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [score, setScore] = useState(0);
  const [finished, setFinished] = useState(false);

  const question = QUESTIONS[idx];

  const next = () => {
    const correct = question.options.find((o) => o.letter === selected)?.correct;
    const newScore = score + (correct ? 1 : 0);
    setScore(newScore);
    if (idx + 1 < QUESTIONS.length) {
      setIdx(idx + 1);
      setSelected(null);
    } else {
      setFinished(true);
    }
  };

  if (finished) {
    return (
      <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center", padding: 24 }}>
        <StatusBar barStyle="light-content" />
        <View style={{ alignItems: "center" }}>
          <View style={{ width: 120, height: 120, borderRadius: 60, backgroundColor: colors.green, justifyContent: "center", alignItems: "center" }}>
            <Text style={{ fontSize: 60 }}>🎉</Text>
          </View>
          <Text style={[font.hero, { color: colors.text, marginTop: 24 }]}>Exam Done</Text>
          <Text style={{ color: colors.textDim, fontSize: 16, marginTop: 8 }}>You scored</Text>
          <Text style={{ color: colors.green, fontSize: 72, fontWeight: "800", marginTop: 8 }}>{score}/{QUESTIONS.length}</Text>
          <Text style={{ color: colors.textDim, fontSize: 15, marginTop: 8 }}>
            {score === QUESTIONS.length ? 'Perfect score!' : score >= QUESTIONS.length / 2 ? 'Good job!' : 'Keep practising!'}
          </Text>
          <Pressable onPress={() => { setIdx(0); setScore(0); setSelected(null); setFinished(false); }} style={{ marginTop: 40, backgroundColor: colors.accent, paddingHorizontal: 40, paddingVertical: 16, borderRadius: 999 }}>
            <Text style={{ color: "#fff", fontSize: 16, fontWeight: "700" }}>Try Again</Text>
          </Pressable>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 140 }}>

        {/* Timer card */}
        <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 2, borderColor: colors.strokeHi, padding: 20, marginBottom: 20, flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
          <View style={{ position: "absolute", left: 0, top: 20, bottom: 20, width: 4, backgroundColor: colors.red, borderTopRightRadius: 4, borderBottomRightRadius: 4 }} />
          <View>
            <Text style={[font.tiny, { color: colors.textDim }]}>TIME REMAINING</Text>
            <Text style={{ color: colors.red, fontSize: 32, fontWeight: "800", marginTop: 4 }}>28:41</Text>
          </View>
          <View>
            <Text style={[font.tiny, { color: colors.textDim, textAlign: "right" }]}>QUESTION</Text>
            <Text style={{ color: colors.text, fontSize: 32, fontWeight: "800", marginTop: 4 }}>{idx + 1}/{QUESTIONS.length}</Text>
          </View>
        </View>

        {/* Progress */}
        <View style={{ height: 8, backgroundColor: colors.stroke, borderRadius: 4, marginBottom: 24, overflow: "hidden" }}>
          <View style={{ width: ((idx + 1) / QUESTIONS.length * 100) + "%", height: "100%", backgroundColor: colors.accent }} />
        </View>

        {/* Question */}
        <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.stroke, padding: 24, marginBottom: 24 }}>
          <Text style={[font.tiny, { color: colors.accentHi }]}>CHEMISTRY</Text>
          <Text style={{ color: colors.textFaint, fontSize: 13, marginTop: 4, marginBottom: 16 }}>Multiple Choice</Text>
          <Text style={{ color: colors.text, fontSize: 22, fontWeight: "600", lineHeight: 32 }}>{question.q}</Text>
        </View>

        {/* Options */}
        {question.options.map((opt) => {
          const isSel = selected === opt.letter;
          return (
            <Pressable
              key={opt.letter}
              onPress={() => setSelected(opt.letter)}
              style={{
                backgroundColor: isSel ? colors.accent : colors.card,
                borderRadius: radius.md,
                borderWidth: 2,
                borderColor: isSel ? colors.accentHi : colors.stroke,
                padding: 20,
                marginBottom: 12,
                flexDirection: "row", alignItems: "center",
              }}
            >
              <View style={{
                width: 44, height: 44, borderRadius: 22,
                backgroundColor: isSel ? 'rgba(255,255,255,0.25)' : colors.cardHi,
                justifyContent: 'center', alignItems: 'center',
              }}>
                <Text style={{ color: isSel ? "#fff" : colors.text, fontSize: 18, fontWeight: "800" }}>{opt.letter}</Text>
              </View>
              <Text style={{ flex: 1, marginLeft: 16, color: isSel ? "#fff" : colors.text, fontSize: 17, fontWeight: "500" }}>{opt.text}</Text>
            </Pressable>
          );
        })}
      </ScrollView>

      {/* Next button */}
      <View style={{ position: "absolute", bottom: 30, left: 20, right: 20 }}>
        <Pressable onPress={next} disabled={!selected} style={{ backgroundColor: selected ? colors.accent : colors.card, borderRadius: radius.md, padding: 20, alignItems: "center", borderWidth: 2, borderColor: selected ? colors.accentHi : colors.stroke }}>
          <Text style={{ color: selected ? "#fff" : colors.textFaint, fontSize: 16, fontWeight: "800", letterSpacing: 1 }}>
            {idx + 1 === QUESTIONS.length ? 'FINISH EXAM' : 'NEXT QUESTION'}
          </Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}