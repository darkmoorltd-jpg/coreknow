import { View, Text, ScrollView, Pressable, ActivityIndicator } from "react-native";
import { useLocalSearchParams, Stack, router } from "expo-router";
import { useQuery } from "@tanstack/react-query";
import { Video, ResizeMode } from "expo-av";
import { SafeAreaView } from "react-native-safe-area-context";
import { api } from "../../lib/api";
import { colors, spacing, radius, font } from "../../constants/theme";
import { useAuth } from "../../lib/store";
import { api } from "../../lib/day1";
import { speak, stopSpeaking } from "../../lib/audio";
import LessonNotes from "../../components/LessonNotes";
import { useState } from "react";

export default function LessonScreen() {
  const user = useAuth((s) => s.user);
  const params = useLocalSearchParams();
  const id = Number(params.id);
  const [mode, setMode] = useState<"read" | "watch">("read");
  const q = useQuery({ queryKey: ["lesson", id], queryFn: () => api.getLesson(id) });

  if (q.isLoading || !q.data) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}><ActivityIndicator size="large" color={colors.accent} /></View>;
  }

  const d = q.data;
  const text = (d.lesson && d.lesson.lesson_text) || "";
  const videoUrls: string[] = [];
  const lines = text.split('\n');
  for (const line of lines) {
    if (line.indexOf("Watch Video") >= 0 && line.indexOf("http") >= 0) {
      const m = line.match(/\(([^)]+)\)/);
      if (m) videoUrls.push(m[1]);
    }
  }
  const bodyText = text.split("## VIDEO SIMULATIONS")[0].trim();

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <Stack.Screen options={{ headerShown: false }} />

      {/* Header */}
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20, paddingBottom: 12 }}>
        <Pressable onPress={() => router.back()}>
          <Text style={{ color: colors.text, fontSize: 32 }}>‹</Text>
        </Pressable>
        <Text style={[font.h3, { color: colors.text, marginLeft: 16, flex: 1 }]} numberOfLines={1}>{d.syllabus.topic_title}</Text>
        <Text style={{ color: colors.yellow, fontSize: 24 }}>★</Text>
      </View>

      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        <View style={{ backgroundColor: colors.card, borderRadius: 999, borderWidth: 1, borderColor: colors.stroke, paddingHorizontal: 16, paddingVertical: 8, alignSelf: "flex-start", marginBottom: 20 }}>
          <Text style={{ color: colors.textDim, fontSize: 12, fontWeight: "600" }}>TOPIC {d.syllabus.topic_number}</Text>
        </View>

        {/* Read / Watch toggle */}
        {videoUrls.length > 0 && (
          <View style={{ flexDirection: "row", backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 6, marginBottom: 24 }}>
            <Pressable
              onPress={() => setMode("read")}
              style={{
                flex: 1, paddingVertical: 14, borderRadius: radius.sm,
                backgroundColor: mode === "read" ? colors.accent : "transparent",
                alignItems: "center",
              }}
            >
              <Text style={{ color: mode === "read" ? "#fff" : colors.textDim, fontWeight: "700" }}>Read</Text>
            </Pressable>
            <Pressable
              onPress={() => setMode("watch")}
              style={{
                flex: 1, paddingVertical: 14, borderRadius: radius.sm,
                backgroundColor: mode === "watch" ? colors.accent : "transparent",
                alignItems: "center",
              }}
            >
              <Text style={{ color: mode === "watch" ? "#fff" : colors.textDim, fontWeight: "700" }}>Watch</Text>
            </Pressable>
          </View>
        )}

        {mode === "watch" ? (
          videoUrls.map((url, i) => (
            <Video key={i} source={{ uri: url }} useNativeControls resizeMode={ResizeMode.CONTAIN} style={{ width: "100%", aspectRatio: 9/16, borderRadius: radius.md, marginBottom: 20, backgroundColor: "#000" }} />
          ))
        ) : (
          <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.stroke, padding: 24 }}>
            <Text style={{ color: colors.text, fontSize: 15, lineHeight: 26 }}>{bodyText}</Text>
          </View>
        )}

        <LessonNotes lessonId={id} />
        <View style={{ height: 40 }} />
      </ScrollView>
    </SafeAreaView>
  );
}