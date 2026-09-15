import { useState, useCallback } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar } from "react-native";
import { useFocusEffect } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../lib/store";
import { api } from "../lib/day1";
import { colors, radius } from "../constants/theme";

export default function Bookmarks() {
  const user = useAuth((s) => s.user);
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useFocusEffect(useCallback(() => {
    if (!user?.id) { setLoading(false); return; }
    api.getBookmarks(user.id).then((d) => {
      setItems(d.bookmarks || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [user]));

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Bookmarks</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        {loading && <ActivityIndicator color={colors.accent} />}
        {!loading && items.length === 0 && (
          <View style={{ alignItems: "center", paddingVertical: 60 }}>
            <Ionicons name="bookmark-outline" size={64} color={colors.textFaint} />
            <Text style={{ color: colors.textDim, fontSize: 16, marginTop: 16 }}>No bookmarks yet</Text>
          </View>
        )}
        {items.map((b) => (
          <Pressable key={b.lesson_id} onPress={() => router.push("/lesson/" + b.lesson_id)} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 18, marginBottom: 10, flexDirection: "row", alignItems: "center" }}>
            <Ionicons name="bookmark" size={22} color={colors.yellow} />
            <Text style={{ flex: 1, marginLeft: 14, color: colors.text, fontSize: 16, fontWeight: "600" }} numberOfLines={2}>{b.topic_title}</Text>
            <Text style={{ color: colors.textFaint, fontSize: 22 }}>›</Text>
          </Pressable>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}