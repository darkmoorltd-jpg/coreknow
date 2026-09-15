import { View, Text, Pressable, ScrollView, ActivityIndicator } from "react-native";
import { router } from "expo-router";
import { useQuery } from "@tanstack/react-query";
import { SafeAreaView } from "react-native-safe-area-context";
import { api } from "../../lib/api";
import { colors, spacing, radius, font } from "../../constants/theme";

const COLORS = [colors.green, colors.accent, colors.violet, colors.cyan, colors.yellow, colors.pink];

export default function SubjectsScreen() {
  const q = useQuery({ queryKey: ["subjects"], queryFn: () => api.getSubjects("JAMB") });

  if (q.isLoading) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}><ActivityIndicator size="large" color={colors.accent} /></View>;
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 100 }}>
        <Text style={[font.hero, { color: colors.text, marginBottom: 24 }]}>Subjects</Text>

        <View style={{ flexDirection: "row", gap: 8, marginBottom: 24 }}>
          {["All", "JAMB", "WAEC", "SS1", "SS2"].map((c, i) => (
            <View key={c} style={{
              paddingHorizontal: 16, paddingVertical: 10, borderRadius: 999,
              backgroundColor: i === 0 ? colors.accent : colors.card,
              borderWidth: 1,
              borderColor: i === 0 ? colors.accent : colors.stroke,
            }}>
              <Text style={{ color: i === 0 ? "#fff" : colors.textDim, fontSize: 14, fontWeight: "600" }}>{c}</Text>
            </View>
          ))}
        </View>

        {(q.data || []).map((subject, i) => (
          <Pressable
            key={subject}
            onPress={() => router.push("/subject/" + subject + "?exam=JAMB")}
            style={{
              backgroundColor: colors.card, borderRadius: radius.md,
              borderWidth: 1, borderColor: colors.stroke,
              padding: 20, marginBottom: 12,
              flexDirection: "row", alignItems: "center",
            }}
          >
            <View style={{ position: "absolute", left: 0, top: 20, bottom: 20, width: 4, backgroundColor: COLORS[i % COLORS.length], borderTopRightRadius: 4, borderBottomRightRadius: 4 }} />
            <View style={{ width: 52, height: 52, borderRadius: 26, backgroundColor: COLORS[i % COLORS.length], justifyContent: "center", alignItems: "center" }}>
              <Text style={{ color: "#fff", fontSize: 22, fontWeight: "800" }}>{subject[0]}</Text>
            </View>
            <View style={{ flex: 1, marginLeft: 16 }}>
              <Text style={[font.h3, { color: colors.text }]}>{subject}</Text>
              <Text style={{ color: colors.textDim, fontSize: 13, marginTop: 2 }}>0 topics started</Text>
            </View>
            <Text style={{ color: colors.accent, fontSize: 13, fontWeight: "700", marginRight: 8 }}>START</Text>
            <Text style={{ color: colors.textFaint, fontSize: 22 }}>›</Text>
          </Pressable>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}