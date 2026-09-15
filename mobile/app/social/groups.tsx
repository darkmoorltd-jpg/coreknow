import { useState, useCallback } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, TextInput, Alert, RefreshControl } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useFocusEffect } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../lib/store";
import { social } from "../../lib/social";
import { colors, radius } from "../../constants/theme";

export default function GroupsList() {
  const user = useAuth((s) => s.user);
  const [mine, setMine] = useState<any[]>([]);
  const [discover, setDiscover] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [newName, setNewName] = useState("");
  const [newSubject, setNewSubject] = useState("Chemistry");
  const [joinCode, setJoinCode] = useState("");

  const load = useCallback(async () => {
    const d = await social.listGroups(user?.id || '');
    if (d.ok) {
      setMine(d.mine || []);
      setDiscover(d.discover || []);
    }
    setLoading(false);
  }, [user]);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const create = async () => {
    if (!newName.trim()) return;
    const d = await social.createGroup({
      user_id: user?.id,
      name: newName.trim(),
      subject: newSubject,
      is_public: true,
    });
    if (d.ok) {
      Alert.alert('Group created', 'Join code: ' + d.group.join_code);
      setNewName('');
      setShowNew(false);
      load();
    } else Alert.alert('Error', d.error || 'Failed');
  };

  const joinByCode = async () => {
    if (!joinCode.trim()) return;
    const d = await social.joinGroup(user?.id || '', '', 0, joinCode.trim().toUpperCase());
    if (d.ok) {
      setJoinCode('');
      load();
    } else Alert.alert('Error', d.error || 'Failed');
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16, flex: 1 }}>Study Groups</Text>
        <Pressable onPress={() => setShowNew(!showNew)}><Ionicons name="add-circle" size={26} color={colors.accent} /></Pressable>
      </View>
      <ScrollView
        contentContainerStyle={{ padding: 20, paddingBottom: 60 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />}
      >
        {showNew ? (
          <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 2, borderColor: colors.accent, padding: 16, marginBottom: 20 }}>
            <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 8 }}>NEW GROUP</Text>
            <TextInput value={newName} onChangeText={setNewName} placeholder='Group name' placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.bg2, borderRadius: radius.sm, padding: 12, color: colors.text, marginBottom: 8 }} />
            <TextInput value={newSubject} onChangeText={setNewSubject} placeholder='Subject' placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.bg2, borderRadius: radius.sm, padding: 12, color: colors.text, marginBottom: 12 }} />
            <Pressable onPress={create} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 14, alignItems: "center" }}>
              <Text style={{ color: "#fff", fontWeight: "800" }}>CREATE</Text>
            </Pressable>
          </View>
        ) : null}

        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 8 }}>JOIN BY CODE</Text>
        <View style={{ flexDirection: "row", gap: 8, marginBottom: 24 }}>
          <TextInput value={joinCode} onChangeText={setJoinCode} placeholder='6-char code' placeholderTextColor={colors.textFaint} autoCapitalize='characters' style={{ flex: 1, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 14, color: colors.text }} />
          <Pressable onPress={joinByCode} style={{ backgroundColor: colors.green, borderRadius: radius.md, paddingHorizontal: 20, justifyContent: "center" }}>
            <Text style={{ color: "#000", fontWeight: "800" }}>JOIN</Text>
          </Pressable>
        </View>

        {loading ? <ActivityIndicator color={colors.accent} /> : null}

        {mine.length > 0 ? <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 8 }}>MY GROUPS</Text> : null}
        {mine.map((g) => (
          <Pressable key={g.id} onPress={() => router.push("/social/group/" + g.id)} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: colors.green, padding: 14, marginBottom: 10 }}>
            <Text style={{ color: colors.text, fontSize: 15, fontWeight: "700" }}>{g.name}</Text>
            <Text style={{ color: colors.textFaint, fontSize: 12, marginTop: 4 }}>{g.subject} · Code: {g.join_code}</Text>
          </Pressable>
        ))}

        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginTop: 12, marginBottom: 8 }}>DISCOVER</Text>
        {discover.map((g) => (
          <Pressable key={g.id} onPress={() => router.push("/social/group/" + g.id)} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: colors.accent, padding: 14, marginBottom: 10 }}>
            <Text style={{ color: colors.text, fontSize: 15, fontWeight: "700" }}>{g.name}</Text>
            <Text style={{ color: colors.textFaint, fontSize: 12, marginTop: 4 }}>{g.subject}</Text>
          </Pressable>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
