import { View, Text, Pressable, ScrollView, ActivityIndicator } from "react-native";
import { router, useLocalSearchParams, Stack } from "expo-router";
import { useQuery } from "@tanstack/react-query";
import { SafeAreaView } from "react-native-safe-area-context";
import { api } from "../../lib/api";
import { colors, spacing, radius, font } from "../../constants/theme";

export default function SubjectDetail() {
  const params = useLocalSearchParams();
  const name = params.name;
  const exam = params.exam || 'JAMB';
  const q = useQuery({ queryKey: ["topics", exam, name], queryFn: () => api.getTopics(name, exam) });

  if (q.isLoading) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}><ActivityIndicator size="large" color={colors.accent} /></View>;
  }

  const topics = q.data || [];
  const done = Math.min(5, topics.length);
  const pct = topics.length > 0 ? done / topics.length : 0;

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <Stack.Screen options={{ headerShown: false }} />
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 100 }}>

        {/* Back */}
        <Pressable onPress={() => router.back()} style={{ marginBottom: 20 }}>
          <Text style={{ color: colors.text, fontSize: 32 }}>‹</Text>
        </Pressable>

        {/* Hero card */}
        <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 2, borderColor: colors.strokeHi, padding: 24, marginBottom: 28, flexDirection: "row", alignItems: "center" }}>
          <View style={{ width: 72, height: 72, borderRadius: 36, backgroundColor: colors.green, justifyContent: "center", alignItems: "center" }}>
            <Text style={{ color: "#fff", fontSize: 32, fontWeight: "800" }}>{String(name)[0]}</Text>
          </View>
          <View style={{ flex: 1, marginLeft: 16 }}>
            <Text style={[font.h2, { color: colors.text }]}>{name}</Text>
            <Text style={{ color: colors.textDim, fontSize: 13, marginTop: 4 }}>{exam}  ·  SS1-SS3</Text>
          </View>
        </View>

        {/* Progress */}
        <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 8 }}>
          <Text style={{ color: colors.textDim, fontSize: 14 }}>{done} of {topics.length} topics complete</Text>
          <Text style={{ color: colors.green, fontSize: 14, fontWeight: "700" }}>{Math.round(pct * 100)}%</Text>
        </View>
        <View style={{ height: 8, backgroundColor: colors.stroke, borderRadius: 4, marginBottom: 28, overflow: "hidden" }}>
          <View style={{ width: (pct * 100) + "%", height: "100%", backgroundColor: colors.green }} />
        </View>

        <Text style={[font.tiny, { color: colors.textFaint, marginBottom: 14 }]}>TOPICS</Text>

        {topics.map((t, i) => {
          const isDone = i < 5;
          const isProgress = i === 5;
          const circleBg = isDone ? colors.green : 'transparent';
          const circleBorder = isDone ? colors.green : isProgress ? colors.accent : colors.textFaint;
          return (
            <Pressable
              key={t.id}
              onPress={() => router.push("/lesson/" + t.id)}
              style={{
                backgroundColor: colors.card, borderRadius: radius.md,
                borderWidth: 1, borderColor: colors.stroke,
                padding: 16, marginBottom: 10,
                flexDirection: "row", alignItems: "center",
              }}
            >
              <View style={{
                width: 40, height: 40, borderRadius: 20,
                backgroundColor: circleBg,
                borderWidth: isDone ? 0 : 2,
                borderColor: circleBorder,
                justifyContent: "center", alignItems: "center",
              }}>
                {isDone ? <Text style={{ color: "#000", fontWeight: "900", fontSize: 18 }}>✓</Text> :
                 isProgress ? <View style={{ width: 12, height: 12, borderRadius: 6, backgroundColor: colors.accent }} /> : null}
              </View>
              <View style={{ flex: 1, marginLeft: 16 }}>
                <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5 }}>TOPIC {t.topic_number}</Text>
                <Text style={[font.bodyBold, { color: colors.text, marginTop: 4 }]} numberOfLines={2}>{t.topic_title}</Text>
              </View>
              <Text style={{ color: colors.textFaint, fontSize: 22 }}>›</Text>
            </Pressable>
          );
        })}
      </ScrollView>
    </SafeAreaView>
  );
}