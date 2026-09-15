import { useState, useCallback } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, RefreshControl } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useFocusEffect } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../lib/store";
import { social } from "../../lib/social";
import { colors, radius } from "../../constants/theme";

export default function Challenges() {
  const user = useAuth((s) => s.user);
  const [challenges, setChallenges] = useState<any[]>([]);
  const [joined, setJoined] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    const d = await social.listChallenges(user?.id || '');
    if (d.ok) {
      setChallenges(d.challenges || []);
      setJoined(d.joined || []);
    }
    setLoading(false);
  }, [user]);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const join = async (id: number) => {
    await social.joinChallenge(id, user?.id || '');
    load();
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Challenges</Text>
      </View>
      <ScrollView
        contentContainerStyle={{ padding: 20, paddingBottom: 60 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />}
      >
        {loading ? <ActivityIndicator color={colors.accent} /> : null}
        {challenges.map((c) => {
          const isJoined = joined.includes(c.id);
          return (
            <View key={c.id} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 2, borderColor: isJoined ? colors.green : colors.stroke, padding: 18, marginBottom: 12 }}>
              <Text style={{ color: colors.accentHi, fontSize: 11, letterSpacing: 1.5 }}>{c.subject}</Text>
              <Text style={{ color: colors.text, fontSize: 18, fontWeight: "800", marginTop: 6 }}>{c.title}</Text>
              <Text style={{ color: colors.textDim, fontSize: 13, marginTop: 6 }}>{c.description}</Text>
              <Text style={{ color: colors.textFaint, fontSize: 12, marginTop: 8 }}>{c.target_count} topics · {c.duration_days} days</Text>
              {isJoined ? (
                <Pressable onPress={() => router.push("/social/challenge/" + c.id)} style={{ backgroundColor: colors.green, borderRadius: radius.md, padding: 12, alignItems: "center", marginTop: 12 }}>
                  <Text style={{ color: "#000", fontWeight: "800" }}>VIEW PROGRESS</Text>
                </Pressable>
              ) : (
                <Pressable onPress={() => join(c.id)} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 12, alignItems: "center", marginTop: 12 }}>
                  <Text style={{ color: "#fff", fontWeight: "800" }}>JOIN</Text>
                </Pressable>
              )}
            </View>
          );
        })}
      </ScrollView>
    </SafeAreaView>
  );
}
