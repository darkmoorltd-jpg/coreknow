import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../../lib/store";
import { social } from "../../../lib/social";
import { colors, radius } from "../../../constants/theme";

export default function GroupDetail() {
  const params = useLocalSearchParams();
  const user = useAuth((s) => s.user);
  const groupId = Number(params.id);
  const [group, setGroup] = useState<any>(null);
  const [members, setMembers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(false);

  const load = async () => {
    const d = await social.groupDetail(groupId);
    if (d.ok) {
      setGroup(d.group);
      setMembers(d.members || []);
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, [groupId]);

  const isMember = members.some((m) => m.user_id === user?.id);

  const join = async () => {
    setJoining(true);
    await social.joinGroup(user?.id || '', '', groupId, '');
    setJoining(false);
    load();
  };

  if (loading) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}><ActivityIndicator color={colors.accent} /></View>;
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 20, fontWeight: "700", marginLeft: 16, flex: 1 }} numberOfLines={1}>{group?.name}</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: colors.accent, padding: 16, marginBottom: 20 }}>
          <Text style={{ color: colors.accentHi, fontSize: 11, letterSpacing: 1.5 }}>{group?.subject}</Text>
          <Text style={{ color: colors.text, fontSize: 20, fontWeight: "800", marginTop: 6 }}>{group?.name}</Text>
          <Text style={{ color: colors.textDim, fontSize: 13, marginTop: 8 }}>{members.length} members · Code: {group?.join_code}</Text>
        </View>
        {!isMember ? (
          <Pressable onPress={join} disabled={joining} style={{ backgroundColor: colors.green, borderRadius: radius.md, padding: 16, alignItems: "center", marginBottom: 20 }}>
            {joining ? <ActivityIndicator color="#000" /> : <Text style={{ color: "#000", fontWeight: "800", letterSpacing: 1 }}>JOIN GROUP</Text>}
          </Pressable>
        ) : null}
        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 12 }}>MEMBERS</Text>
        {members.map((m, i) => (
          <View key={m.id} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 12, marginBottom: 8, flexDirection: "row", alignItems: "center" }}>
            <Text style={{ color: colors.textFaint, width: 28, fontWeight: "800" }}>#{i + 1}</Text>
            <Text style={{ color: colors.text, flex: 1, fontWeight: "600" }}>{m.full_name || m.user_id.slice(0, 12)}</Text>
            {m.role === 'admin' ? <Text style={{ color: colors.yellow, fontSize: 11, fontWeight: '800' }}>ADMIN</Text> : null}
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
