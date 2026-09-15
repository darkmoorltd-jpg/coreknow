import { useState, useCallback } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, TextInput, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useLocalSearchParams, useFocusEffect } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../../lib/store";
import { school } from "../../../lib/school";
import { colors, radius } from "../../../constants/theme";

export default function ClassDetail() {
  const params = useLocalSearchParams();
  const user = useAuth((s) => s.user);
  const classId = Number(params.id);
  const [tab, setTab] = useState<'assignments'|'members'>('assignments');
  const [assignments, setAssignments] = useState<any[]>([]);
  const [members, setMembers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNew, setShowNew] = useState(false);
  const [title, setTitle] = useState("");
  const [subject, setSubject] = useState("Chemistry");
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    const [a, m] = await Promise.all([
      school.listAssignments(classId),
      school.members(classId),
    ]);
    if (a.ok) setAssignments(a.assignments || []);
    if (m.ok) setMembers(m.members || []);
    setLoading(false);
  }, [classId]);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  const doCreate = async () => {
    if (!title.trim()) return;
    setCreating(true);
    const d = await school.createAssignment({
      class_id: classId,
      teacher_id: user?.id,
      title: title.trim(),
      subject,
      max_score: 100,
    });
    setCreating(false);
    if (d.ok) {
      setTitle('');
      setShowNew(false);
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
        <Text style={{ color: colors.text, fontSize: 20, fontWeight: "700", marginLeft: 16, flex: 1 }}>Class</Text>
        <Pressable onPress={() => router.push("/school/analytics?class_id=" + classId)} style={{ padding: 8 }}>
          <Ionicons name="bar-chart" size={22} color={colors.accent} />
        </Pressable>
      </View>
      <View style={{ flexDirection: "row", gap: 8, paddingHorizontal: 20, marginBottom: 12 }}>
        {(['assignments','members'] as const).map((t) => (
          <Pressable key={t} onPress={() => setTab(t)} style={{ flex: 1, padding: 12, borderRadius: radius.md, backgroundColor: tab === t ? colors.accent : colors.card, alignItems: 'center' }}>
            <Text style={{ color: tab === t ? "#fff" : colors.text, fontWeight: "700", textTransform: "capitalize" }}>{t}</Text>
          </Pressable>
        ))}
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        {tab === 'assignments' ? (
          <>
            <Pressable onPress={() => setShowNew(!showNew)} style={{ backgroundColor: colors.green, borderRadius: radius.md, padding: 14, alignItems: "center", marginBottom: 16, flexDirection: "row", justifyContent: "center" }}>
              <Ionicons name="add" size={20} color="#000" />
              <Text style={{ color: "#000", fontWeight: "800", marginLeft: 6 }}>NEW ASSIGNMENT</Text>
            </Pressable>
            {showNew ? (
              <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 2, borderColor: colors.green, padding: 14, marginBottom: 16 }}>
                <TextInput value={title} onChangeText={setTitle} placeholder='Title' placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.bg2, borderRadius: radius.sm, padding: 12, color: colors.text, marginBottom: 8 }} />
                <TextInput value={subject} onChangeText={setSubject} placeholder='Subject' placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.bg2, borderRadius: radius.sm, padding: 12, color: colors.text, marginBottom: 12 }} />
                <Pressable onPress={doCreate} disabled={creating} style={{ backgroundColor: colors.green, borderRadius: radius.md, padding: 12, alignItems: "center" }}>
                  {creating ? <ActivityIndicator color="#000" /> : <Text style={{ color: "#000", fontWeight: "800" }}>CREATE</Text>}
                </Pressable>
              </View>
            ) : null}
            {loading ? <ActivityIndicator color={colors.accent} /> : null}
            {!loading && assignments.length === 0 ? (
              <Text style={{ color: colors.textDim, textAlign: "center", marginTop: 40 }}>No assignments yet</Text>
            ) : null}
            {assignments.map((a) => (
              <Pressable key={a.id} onPress={() => router.push("/school/assignment/" + a.id)} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 14, marginBottom: 10 }}>
                <Text style={{ color: colors.accentHi, fontSize: 11, letterSpacing: 1 }}>{a.subject} · MAX {a.max_score}</Text>
                <Text style={{ color: colors.text, fontSize: 15, fontWeight: "700", marginTop: 4 }}>{a.title}</Text>
              </Pressable>
            ))}
          </>
        ) : (
          <>
            <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 12 }}>{members.length} MEMBERS</Text>
            {members.map((m, i) => (
              <View key={m.id} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 14, marginBottom: 8, flexDirection: "row", alignItems: "center" }}>
                <Text style={{ color: colors.textFaint, width: 28, fontWeight: "800" }}>#{i + 1}</Text>
                <Text style={{ color: colors.text, flex: 1, fontWeight: "600" }}>{m.full_name || m.user_id.slice(0, 12)}</Text>
                <Pressable onPress={() => router.push("/school/report/" + classId + "/" + m.user_id)} style={{ padding: 6 }}>
                  <Ionicons name="document-text" size={20} color={colors.accent} />
                </Pressable>
              </View>
            ))}
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
