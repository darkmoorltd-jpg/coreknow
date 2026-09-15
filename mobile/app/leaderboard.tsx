import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../lib/store";
import { day4 } from "../lib/day4";
import { colors, radius } from "../constants/theme";

export default function Leaderboard() {
  const user = useAuth((s) => s.user);
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    day4.getLeaderboard().then((d) => {
      setRows(d.leaderboard || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const medal = (i: number) => {
    if (i === 0) return '🥇';
    if (i === 1) return '🥈';
    if (i === 2) return '🥉';
    return '';
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Leaderboard</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        <Text style={{ color: colors.textDim, fontSize: 14, marginBottom: 20 }}>This week · Top learners</Text>
        {loading && <ActivityIndicator color={colors.accent} />}
        {!loading && rows.length === 0 && (
          <View style={{ alignItems: "center", paddingVertical: 60 }}>
            <Ionicons name="trophy-outline" size={64} color={colors.textFaint} />
            <Text style={{ color: colors.textDim, fontSize: 16, marginTop: 16 }}>No activity this week</Text>
            <Text style={{ color: colors.textFaint, fontSize: 13, marginTop: 6 }}>Study to appear on the board</Text>
          </View>
        )}
        {rows.map((r, i) => {
          const isMe = r.user_id === user?.id;
          return (
            <View
              key={r.user_id}
              style={{
                backgroundColor: isMe ? colors.accent : colors.card,
                borderRadius: radius.md,
                borderWidth: isMe ? 2 : 1,
                borderColor: isMe ? colors.accent : colors.stroke,
                padding: 16,
                marginBottom: 10,
                flexDirection: 'row',
                alignItems: 'center',
              }}
            >
              <Text style={{ fontSize: 24, width: 40 }}>{medal(i)}</Text>
              <Text style={{ color: isMe ? '#fff' : colors.textFaint, fontSize: 16, fontWeight: '800', width: 40 }}>
                {i + 1}
              </Text>
              <View style={{ flex: 1 }}>
                <Text style={{ color: isMe ? '#fff' : colors.text, fontSize: 16, fontWeight: '600' }}>
                  {isMe ? 'You' : 'Student ' + r.user_id.slice(0, 6)}
                </Text>
                <Text style={{ color: isMe ? '#dbe4ff' : colors.textDim, fontSize: 12, marginTop: 2 }}>
                  {r.lessons_done || 0} lessons · {r.quizzes_done || 0} quizzes
                </Text>
              </View>
              <View style={{ alignItems: 'flex-end' }}>
                <Text style={{ color: isMe ? '#fff' : colors.yellow, fontSize: 22, fontWeight: '800' }}>{r.score}</Text>
                <Text style={{ color: isMe ? '#dbe4ff' : colors.textFaint, fontSize: 10, letterSpacing: 1 }}>POINTS</Text>
              </View>
            </View>
          );
        })}
      </ScrollView>
    </SafeAreaView>
  );
}