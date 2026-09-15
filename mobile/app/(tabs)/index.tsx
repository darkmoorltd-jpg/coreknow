import { ScrollView, View, Text, Pressable, StatusBar } from "react-native";
import { router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { colors, spacing, radius, font } from "../../constants/theme";

const EXAMS = [
  { id: "JAMB", letter: "J", color: colors.accent, topics: 18 },
  { id: "WAEC", letter: "W", color: colors.green,  topics: 18 },
  { id: "NECO", letter: "N", color: colors.yellow, topics: 18 },
  { id: "GCE",  letter: "G", color: colors.violet, topics: 18 },
];

export default function HomeScreen() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 100 }} showsVerticalScrollIndicator={false}>

        {/* Greeting */}
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 28 }}>
          <View>
            <Text style={{ color: colors.textDim, fontSize: 14 }}>Good evening,</Text>
            <Text style={[font.h1, { color: colors.text, marginTop: 2 }]}>Ade</Text>
          </View>
          <View style={{ width: 52, height: 52, borderRadius: 26, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center" }}>
            <Text style={{ color: "#fff", fontSize: 22, fontWeight: "700" }}>A</Text>
          </View>
        </View>

        {/* Continue learning hero */}
        <Pressable style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 2, borderColor: colors.strokeHi, padding: 24, marginBottom: 24 }}>
          <View style={{ position: "absolute", left: 0, top: 20, bottom: 20, width: 4, backgroundColor: colors.accent, borderTopRightRadius: 4, borderBottomRightRadius: 4 }} />
          <Text style={[font.tiny, { color: colors.accentHi }]}>CONTINUE LEARNING</Text>
          <Text style={[font.h2, { color: colors.text, marginTop: 8 }]}>Chemistry  ·  Lesson 6</Text>
          <Text style={{ color: colors.textDim, fontSize: 15, marginTop: 4 }}>Solubility</Text>
          <View style={{ height: 6, backgroundColor: colors.stroke, borderRadius: 3, marginTop: 22, overflow: "hidden" }}>
            <View style={{ width: "28%", height: "100%", backgroundColor: colors.accent }} />
          </View>
          <View style={{ flexDirection: "row", justifyContent: "space-between", marginTop: 8 }}>
            <Text style={{ color: colors.textFaint, fontSize: 12 }}>5 of 18 topics</Text>
            <Text style={{ color: colors.accent, fontSize: 12, fontWeight: "700" }}>28%</Text>
          </View>
        </Pressable>

        {/* Stats row */}
        <View style={{ flexDirection: "row", gap: 12, marginBottom: 28 }}>
          {[
            { n: "5", label: "Topics", color: colors.green },
            { n: "0", label: "Streak", color: colors.yellow },
            { n: "—", label: "Avg", color: colors.cyan },
          ].map((s, i) => (
            <View key={i} style={{ flex: 1, backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 16 }}>
              <View style={{ width: 10, height: 10, borderRadius: 5, backgroundColor: s.color, marginBottom: 12 }} />
              <Text style={{ color: colors.text, fontSize: 28, fontWeight: "800" }}>{s.n}</Text>
              <Text style={{ color: colors.textFaint, fontSize: 11, marginTop: 2 }}>{s.label}</Text>
            </View>
          ))}
        </View>

        {/* Exams section */}
        <Text style={[font.tiny, { color: colors.textFaint, marginBottom: 14 }]}>EXAMS</Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 12 }}>
          {EXAMS.map((exam) => (
            <Pressable
              key={exam.id}
              onPress={() => router.push("/subject/" + exam.id + "?exam=" + exam.id)}
              style={{ width: "48%", backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 2, borderColor: colors.stroke, padding: 18, minHeight: 150 }}
            >
              <View style={{ position: "absolute", left: 0, top: 16, bottom: 16, width: 3, backgroundColor: exam.color, borderTopRightRadius: 3, borderBottomRightRadius: 3 }} />
              <View style={{ width: 48, height: 48, borderRadius: 24, backgroundColor: exam.color, justifyContent: "center", alignItems: "center" }}>
                <Text style={{ color: "#fff", fontSize: 22, fontWeight: "800" }}>{exam.letter}</Text>
              </View>
              <Text style={[font.h3, { color: colors.text, marginTop: 14 }]}>{exam.id}</Text>
              <Text style={{ color: colors.textFaint, fontSize: 12, marginTop: 2 }}>{exam.topics} topics</Text>
            </Pressable>
          ))}
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}