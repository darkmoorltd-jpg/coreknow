import { useState } from "react";
import { View, Text, ScrollView, ActivityIndicator, Pressable } from "react-native";
import { useLocalSearchParams, Stack } from "expo-router";
import { useQuery } from "@tanstack/react-query";
import { Video, ResizeMode } from "expo-av";
import { api } from "../../lib/api";
import { colors, spacing, radius } from "../../constants/theme";

export default function LessonScreen() {
  const params = useLocalSearchParams();
  const id = Number(params.id);
  const [mode, setMode] = useState("read");
  const query = useQuery({ queryKey: ["lesson", id], queryFn: () => api.getLesson(id) });

  if (query.isLoading || !query.data) {
    return (
      <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}>
        <ActivityIndicator size="large" color={colors.accent} />
      </View>
    );
  }

  const d = query.data;
  const text = (d.lesson && d.lesson.lesson_text) || "";
  const videoUrls = [];
  const arr = text.split("\n");
  for (let i = 0; i < arr.length; i++) {
    const line = arr[i];
    if (line.indexOf("Watch Video") >= 0 && line.indexOf("http") >= 0) {
      const m = line.match(/\(([^)]+)\)/);
      if (m) videoUrls.push(m[1]);
    }
  }
  const bodyText = text.split("## VIDEO SIMULATIONS")[0].trim();

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <Stack.Screen options={{ title: d.syllabus.topic_title }} />
      <ScrollView contentContainerStyle={{ padding: spacing.md }}>
        <Text style={{ color: colors.textDim, fontSize: 12 }}>TOPIC {d.syllabus.topic_number}</Text>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "800", marginTop: 6, marginBottom: 20 }}>{d.syllabus.topic_title}</Text>

        {videoUrls.length > 0 ? (
          <View style={{ flexDirection: "row", gap: 8, marginBottom: spacing.md }}>
            <Pressable onPress={() => setMode("read")} style={{ flex: 1, padding: 12, borderRadius: radius.md, backgroundColor: mode === "read" ? colors.accent : colors.card, alignItems: "center" }}>
              <Text style={{ color: mode === "read" ? "#fff" : colors.text, fontWeight: "600" }}>Read</Text>
            </Pressable>
            <Pressable onPress={() => setMode("watch")} style={{ flex: 1, padding: 12, borderRadius: radius.md, backgroundColor: mode === "watch" ? colors.accent : colors.card, alignItems: "center" }}>
              <Text style={{ color: mode === "watch" ? "#fff" : colors.text, fontWeight: "600" }}>Watch</Text>
            </Pressable>
          </View>
        ) : null}

        {mode === "watch" ? videoUrls.map((url, i) => (
          <Video key={i} source={{ uri: url }} useNativeControls resizeMode={ResizeMode.CONTAIN} style={{ width: "100%", aspectRatio: 9 / 16, marginBottom: spacing.md }} />
        )) : (
          <Text style={{ color: colors.text, fontSize: 15, lineHeight: 24 }}>{bodyText}</Text>
        )}
      </ScrollView>
    </View>
  );
}