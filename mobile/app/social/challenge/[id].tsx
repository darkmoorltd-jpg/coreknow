import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../../lib/store";
import { social } from "../../../lib/social";
import { colors, radius } from "../../../constants/theme";

export default function ChallengeDetail() {
  const params = useLocalSearchParams();
  const user = useAuth((s) => s.user);
  const challengeId = Number(params.id);
  const [leaders, setLeaders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    social.challengeLeaderboard(challengeId).then((d) => {
      if (d.ok) setLeaders(d.participants || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [challengeId]);

  const myRow = leaders.find((l) => l.user_id === user?.id);
  const myProgress = myRow?.progress || 0;

  const bump = async () => {
    if (!myRow) return;
    await social.updateProgress(challengeId, user?.id || '', myProgress + 1);
    const d = await social.challengeLeaderboard(challengeId);
    if (d.ok) setLeaders(d.participants || []);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 20, fontWeight: "700", marginLeft: 16 }}>Challenge</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 2, borderColor: colors.green, padding: 24, alignItems: "center", marginBottom: 24 }}>
          <Ionicons name="trophy" size={56} color={colors.yellow} />
          <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginTop: 12 }}>YOUR PROGRESS</Text>
          <Text style={{ color: colors.green, fontSize: 56, fontWeight: "800", marginTop: 4 }}>{myProgress}</Text>
        </View>
        <Pressable onPress={bump} style={{ backgroundColor: colors.green, borderRadius: radius.md, padding: 18, alignItems: "center", marginBottom: 24 }}>
          <Text style={{ color: "#000", fontWeight: "800", letterSpacing: 1 }}>+1 TOPIC COMPLETED</Text>
        </Pressable>
        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 12 }}>LEADERBOARD</Text>
        {loading ? <ActivityIndicator color={colors.accent} /> : null}
        {leaders.map((l, i) => (
          <View key={l.id} style={{ backgroundColor: l.user_id === user?.id ? colors.accent : colors.card, borderRadius: radius.md, padding: 14, marginBottom: 8, flexDirection: "row", alignItems: "center" }}>
            <Text style={{ color: l.user_id === user?.id ? "#fff" : colors.textFaint, width: 32, fontWeight: "800" }}>#{i + 1}</Text>
            <Text style={{ color: l.user_id === user?.id ? "#fff" : colors.text, flex: 1, fontWeight: "600" }}>
              {l.user_id === user?.id ? 'You' : 'Student ' + l.user_id.slice(0, 6)}
            </Text>
            <Text style={{ color: l.user_id === user?.id ? "#fff" : colors.green, fontSize: 20, fontWeight: "800" }}>{l.progress}</Text>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
