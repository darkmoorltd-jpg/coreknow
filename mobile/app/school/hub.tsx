import { useState, useCallback } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, TextInput, Alert, RefreshControl } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useFocusEffect } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../lib/store";
import { school } from "../../lib/school";
import { colors, radius } from "../../constants/theme";

export default function SchoolHub() {
  const user = useAuth((s) => s.user);
  const [classes, setClasses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [joinCode, setJoinCode] = useState("");
  const [joining, setJoining] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newLevel, setNewLevel] = useState("SS2");
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    const d = await school.listClasses(0, user?.id || '');
    if (d.ok) setClasses(d.classes || []);
    setLoading(false);
  }, [user]);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const doJoin = async () => {
    if (!joinCode.trim()) return;
    setJoining(true);
    const d = await school.joinClass(joinCode.trim().toUpperCase(), user?.id || '', '');
    setJoining(false);
    if (d.ok) {
      Alert.alert('Joined', 'You are now in ' + d.class.name);
      setJoinCode('');
      load();
    } else {
      Alert.alert('Error', d.error || 'Could not join');
    }
  };

  const doCreate = async () => {
    if (!newName.trim()) return;
    setCreating(true);
    const d = await school.createClass({
      school_license_id: 0,
      admin_id: user?.id,
      name: newName.trim(),
      level: newLevel,
      teacher_id: user?.id,
    });
    setCreating(false);
    if (d.ok) {
      Alert.alert('Created', 'Join code: ' + d.class.join_code);
      setNewName('');
      setShowCreate(false);
      load();
    } else {
      Alert.alert('Error', d.error || 'Failed');
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16, flex: 1 }}>School</Text>
        <Pressable onPress={() => setShowCreate(!showCreate)}><Ionicons name="add-circle" size={26} color={colors.accent} /></Pressable>
      </View>
      <ScrollView
        contentContainerStyle={{ padding: 20, paddingBottom: 60 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />}
      >
        {showCreate ? (
          <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 2, borderColor: colors.accent, padding: 16, marginBottom: 20 }}>
            <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 8 }}>NEW CLASS</Text>
            <TextInput value={newName} onChangeText={setNewName} placeholder='Class name (e.g. SS2A Chemistry)' placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.bg2, borderRadius: radius.sm, padding: 12, color: colors.text, marginBottom: 10 }} />
            <TextInput value={newLevel} onChangeText={setNewLevel} placeholder='Level (SS1, SS2, SS3)' placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.bg2, borderRadius: radius.sm, padding: 12, color: colors.text, marginBottom: 12 }} />
            <Pressable onPress={doCreate} disabled={creating} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 14, alignItems: "center" }}>
              {creating ? <ActivityIndicator color="#fff" /> : <Text style={{ color: "#fff", fontWeight: "800" }}>CREATE CLASS</Text>}
            </Pressable>
          </View>
        ) : null}

        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 8 }}>JOIN A CLASS</Text>
        <View style={{ flexDirection: "row", gap: 8, marginBottom: 24 }}>
          <TextInput value={joinCode} onChangeText={setJoinCode} placeholder='6-char code' placeholderTextColor={colors.textFaint} autoCapitalize='characters' style={{ flex: 1, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 14, color: colors.text, fontSize: 15 }} />
          <Pressable onPress={doJoin} disabled={joining} style={{ backgroundColor: colors.green, borderRadius: radius.md, paddingHorizontal: 20, justifyContent: "center" }}>
            {joining ? <ActivityIndicator color="#000" /> : <Text style={{ color: "#000", fontWeight: "800" }}>JOIN</Text>}
          </Pressable>
        </View>

        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 12 }}>MY CLASSES</Text>
        {loading && <ActivityIndicator color={colors.accent} />}
        {!loading && classes.length === 0 && (
          <View style={{ alignItems: "center", paddingVertical: 40 }}>
            <Ionicons name="school-outline" size={56} color={colors.textFaint} />
            <Text style={{ color: colors.textDim, marginTop: 16 }}>No classes yet</Text>
          </View>
        )}
        {classes.map((c) => (
          <Pressable key={c.id} onPress={() => router.push("/school/class/" + c.id)} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 16, marginBottom: 10 }}>
            <View style={{ flexDirection: "row", alignItems: "center" }}>
              <View style={{ width: 48, height: 48, borderRadius: 24, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center" }}>
                <Text style={{ color: "#fff", fontSize: 20, fontWeight: "800" }}>{c.name?.[0] || "C"}</Text>
              </View>
              <View style={{ flex: 1, marginLeft: 14 }}>
                <Text style={{ color: colors.text, fontSize: 16, fontWeight: "700" }}>{c.name}</Text>
                <Text style={{ color: colors.textFaint, fontSize: 12, marginTop: 4 }}>{c.level} · Code: {c.join_code}</Text>
              </View>
              <Text style={{ color: colors.textFaint, fontSize: 22 }}>›</Text>
            </View>
          </Pressable>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
