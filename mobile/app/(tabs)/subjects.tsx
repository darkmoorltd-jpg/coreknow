import { View, Text, Pressable, FlatList, ActivityIndicator } from "react-native";
import { router } from "expo-router";
import { useQuery } from "@tanstack/react-query";
import { SafeAreaView } from "react-native-safe-area-context";
import { api } from "../../lib/api";
import { colors, spacing, radius } from "../../constants/theme";

export default function SubjectsScreen() {
  const q = useQuery({ queryKey: ["subjects"], queryFn: () => api.getSubjects("JAMB") });

  if (q.isLoading) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}><ActivityIndicator size="large" color={colors.accent} /></View>;
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <FlatList
        data={q.data || []}
        keyExtractor={(i) => i}
        contentContainerStyle={{ padding: spacing.md }}
        ListHeaderComponent={<Text style={{ color: colors.text, fontSize: 24, fontWeight: '700', marginBottom: spacing.md }}>JAMB Subjects</Text>}
        renderItem={({ item }) => (
          <Pressable onPress={() => router.push("/subject/" + item + "?exam=JAMB")} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: colors.accent, padding: spacing.md, marginBottom: 12 }}>
            <Text style={{ color: colors.text, fontSize: 17, fontWeight: "600" }}>{item}</Text>
          </Pressable>
        )}
      />
    </SafeAreaView>
  );
}