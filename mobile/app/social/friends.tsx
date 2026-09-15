import { useState, useCallback } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, TextInput, Alert, RefreshControl } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useFocusEffect } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../lib/store";
import { social } from "../../lib/social";
import { colors, radius } from "../../constants/theme";

export default function Friends() {
  const user = useAuth((s) => s.user);
  const [friends, setFriends] = useState<any[]>([]);
  const [pending, setPending] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [email, setEmail] = useState("");
  const [inviting, setInviting] = useState(false);

  const load = useCallback(async () => {
    if (!user?.id) return;
    const d = await social.listFriends(user.id);
    if (d.ok) {
      setFriends(d.friends || []);
      setPending(d.pending || []);
    }
    setLoading(false);
  }, [user]);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const invite = async () => {
    if (!email.trim()) return;
    setInviting(true);
    const d = await social.requestFriend(user?.id || '', email.trim());
    setInviting(false);
    if (d.ok) {
      Alert.alert('Sent', 'Friend request sent');
      setEmail('');
    } else Alert.alert('Error', d.error || 'Failed');
  };

  const respond = async (fid: string, accept: boolean) => {
    await social.respondFriend(user?.id || '', fid, accept);
    load();
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Friends</Text>
      </View>
      <ScrollView
        contentContainerStyle={{ padding: 20, paddingBottom: 60 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />}
      >
        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 8 }}>ADD BY EMAIL</Text>
        <View style={{ flexDirection: "row", gap: 8, marginBottom: 24 }}>
          <TextInput value={email} onChangeText={setEmail} placeholder='friend@example.com' placeholderTextColor={colors.textFaint} autoCapitalize='none' keyboardType='email-address' style={{ flex: 1, backgroundColor: colors.card, borderRadius: radius.md, padding: 12, color: colors.text, borderWidth: 1, borderColor: colors.stroke }} />
          <Pressable onPress={invite} disabled={inviting} style={{ backgroundColor: colors.accent, borderRadius: radius.md, paddingHorizontal: 18, justifyContent: "center" }}>
            {inviting ? <ActivityIndicator color="#fff" /> : <Text style={{ color: "#fff", fontWeight: "800" }}>ADD</Text>}
          </Pressable>
        </View>

        {loading ? <ActivityIndicator color={colors.accent} /> : null}

        {pending.length > 0 ? (
          <>
            <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 8 }}>PENDING REQUESTS ({pending.length})</Text>
            {pending.map((p) => (
              <View key={p.id} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: colors.yellow, padding: 14, marginBottom: 10 }}>
                <Text style={{ color: colors.text, fontWeight: "600" }}>{p.user_id.slice(0, 12)}...</Text>
                <View style={{ flexDirection: "row", gap: 8, marginTop: 10 }}>
                  <Pressable onPress={() => respond(p.user_id, true)} style={{ flex: 1, backgroundColor: colors.green, borderRadius: radius.sm, padding: 10, alignItems: "center" }}>
                    <Text style={{ color: "#000", fontWeight: "800" }}>ACCEPT</Text>
                  </Pressable>
                  <Pressable onPress={() => respond(p.user_id, false)} style={{ flex: 1, backgroundColor: colors.card, borderRadius: radius.sm, padding: 10, alignItems: "center", borderWidth: 1, borderColor: colors.red }}>
                    <Text style={{ color: colors.red, fontWeight: "800" }}>DECLINE</Text>
                  </Pressable>
                </View>
              </View>
            ))}
          </>
        ) : null}

        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginTop: 12, marginBottom: 8 }}>MY FRIENDS ({friends.length})</Text>
        {friends.length === 0 ? <Text style={{ color: colors.textDim }}>No friends yet</Text> : null}
        {friends.map((f) => (
          <View key={f.id} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 14, marginBottom: 8, flexDirection: "row", alignItems: "center" }}>
            <Ionicons name="person-circle" size={36} color={colors.accent} />
            <Text style={{ color: colors.text, fontWeight: "600", flex: 1, marginLeft: 12 }}>{(f.user_id === user?.id ? f.friend_id : f.user_id).slice(0, 12)}...</Text>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
