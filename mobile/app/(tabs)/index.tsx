import { ScrollView, View, Text, Pressable } from "react-native";
import { router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { colors, spacing, radius } from "../../constants/theme";

const exams = ["JAMB", "WAEC", "NECO", "GCE"];

export default function HomeScreen() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView contentContainerStyle={{ padding: spacing.lg }}>
        <Text style={{ color: colors.text, fontSize: 32, fontWeight: '800' }}>CoreKnow</Text>
        <Text style={{ color: colors.textDim, fontSize: 15, marginTop: 6, marginBottom: 32 }}>Your AI tutor for every subject</Text>
        <Pressable onPress={() => router.push("/chat")} style={{ backgroundColor: colors.accent, borderRadius: radius.lg, padding: spacing.lg, marginBottom: spacing.lg }}>
          <Text style={{ color: "#fff", fontSize: 18, fontWeight: "700" }}>Ask CoreKnow</Text>
          <Text style={{ color: "#dbe4ff", fontSize: 13, marginTop: 4 }}>Type or upload any question</Text>
        </Pressable>
        <Text style={{ color: colors.text, fontSize: 18, fontWeight: '700', marginBottom: spacing.md }}>Choose your exam</Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 12 }}>
          {exams.map((e) => (
            <Pressable key={e} onPress={() => router.push("/subject/" + e + "?exam=" + e)} style={{ width: "47%", backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: colors.accent, padding: spacing.md, minHeight: 90 }}>
              <Text style={{ color: colors.text, fontSize: 17, fontWeight: "700" }}>{e}</Text>
            </Pressable>
          ))}
        </View>
        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}