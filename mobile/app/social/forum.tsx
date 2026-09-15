import { useState, useCallback } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, TextInput, Alert, RefreshControl } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useFocusEffect } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../lib/store";
import { social } from "../../lib/social";
import { colors, radius } from "../../constants/theme";

export default function Forum() {
  const user = useAuth((s) => s.user);
  const [threads, setThreads] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [subject, setSubject] = useState("Chemistry");

  const load = useCallback(async () => {
    const d = await social.listThreads();
    if (d.ok) setThreads(d.threads || []);
    setLoading(false);
  }, []);

  useFocusEffect(useCallback(() => { load(); }, [load]));

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const post = async () => {
    if (!title.trim() || !body.trim()) return;
    const d = await social.createThread({
      user_id: user?.id,
      subject,
      title: title.trim(),
      body: body.trim(),
    });
    if (d.ok) {
      setTitle('');
      setBody('');
      setShowNew(false);
      load();
    } else Alert.alert('Error', d.error || 'Failed');
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16, flex: 1 }}>Ask a Peer</Text>
        <Pressable onPress={() => setShowNew(!showNew)}><Ionicons name="add-circle" size={26} color={colors.accent} /></Pressable>
      </View>
      <ScrollView
        contentContainerStyle={{ padding: 20, paddingBottom: 60 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />}
      >
        {showNew ? (
          <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 2, borderColor: colors.accent, padding: 16, marginBottom: 20 }}>
            <TextInput value={subject} onChangeText={setSubject} placeholder="Subject" placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.bg2, borderRadius: radius.sm, padding: 12, color: colors.text, marginBottom: 8 }} />
            <TextInput value={title} onChangeText={setTitle} placeholder="Question title" placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.bg2, borderRadius: radius.sm, padding: 12, color: colors.text, marginBottom: 8 }} />
            <TextInput value={body} onChangeText={setBody} multiline placeholder="Describe your question..." placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.bg2, borderRadius: radius.sm, padding: 12, color: colors.text, minHeight: 120, textAlignVertical: "top", marginBottom: 12 }} />
            <Pressable onPress={post} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 14, alignItems: "center" }}>
              <Text style={{ color: "#fff", fontWeight: "800" }}>POST</Text>
            </Pressable>
          </View>
        ) : null}

        {loading ? <ActivityIndicator color={colors.accent} /> : null}
        {threads.map((t) => (
          <Pressable key={t.id} onPress={() => router.push("/social/thread/" + t.id)} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 16, marginBottom: 10 }}>
            <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 6 }}>
              <Text style={{ color: colors.accentHi, fontSize: 11, letterSpacing: 1 }}>{t.subject}</Text>
              <Text style={{ color: colors.textFaint, fontSize: 11 }}>{t.reply_count || 0} replies · {t.upvotes || 0} votes</Text>
            </View>
            <Text style={{ color: colors.text, fontSize: 15, fontWeight: "700" }} numberOfLines={2}>{t.title}</Text>
            <Text style={{ color: colors.textDim, fontSize: 13, marginTop: 6 }} numberOfLines={2}>{t.body}</Text>
            <Text style={{ color: colors.textFaint, fontSize: 11, marginTop: 6 }}>By {t.author_name}</Text>
          </Pressable>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
