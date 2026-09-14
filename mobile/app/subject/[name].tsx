import { View, Text, Pressable, FlatList, ActivityIndicator } from "react-native";
import { router, useLocalSearchParams, Stack } from "expo-router";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../lib/api";
import { colors, spacing, radius } from "../../constants/theme";

export default function SubjectScreen() {
  const params = useLocalSearchParams();
  const name = params.name;
  const exam = params.exam || 'JAMB';
  const q = useQuery({ queryKey: ["topics", exam, name], queryFn: () => api.getTopics(name, exam) });

  if (q.isLoading) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}><ActivityIndicator size="large" color={colors.accent} /></View>;
  }

  return (
    <>
      <Stack.Screen options={{ title: name }} />
      <FlatList
        style={{ backgroundColor: colors.bg }}
        data={q.data || []}
        keyExtractor={(t) => String(t.id)}
        contentContainerStyle={{ padding: spacing.md }}
        renderItem={({ item }) => (
          <Pressable onPress={() => router.push("/lesson/" + item.id)} style={{ backgroundColor: colors.card, borderRadius: radius.md, padding: spacing.md, marginBottom: 10, borderLeftWidth: 4, borderLeftColor: colors.accent }}>
            <Text style={{ color: colors.textDim, fontSize: 12 }}>TOPIC {item.topic_number}</Text>
            <Text style={{ color: colors.text, fontSize: 16, fontWeight: "600", marginTop: 4 }}>{item.topic_title}</Text>
          </Pressable>
        )}
      />
    </>
  );
}