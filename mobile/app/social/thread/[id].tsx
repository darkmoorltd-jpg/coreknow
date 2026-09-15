import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, TextInput, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../../lib/store";
import { social } from "../../../lib/social";
import { colors, radius } from "../../../constants/theme";

export default function ThreadDetail() {
  const params = useLocalSearchParams();
  const user = useAuth((s) => s.user);
  const threadId = Number(params.id);
  const [thread, setThread] = useState<any>(null);
  const [replies, setReplies] = useState<any[]>([]);
  const [reply, setReply] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);

  const load = async () => {
    const d = await social.threadDetail(threadId);
    if (d.ok) {
      setThread(d.thread);
      setReplies(d.replies || []);
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, [threadId]);

  const send = async () => {
    if (!reply.trim()) return;
    setSending(true);
    await social.createReply(threadId, user?.id || '', '', reply.trim());
    setReply('');
    setSending(false);
    load();
  };

  const vote = async () => {
    await social.vote('thread', threadId, user?.id || '');
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
        <Text style={{ color: colors.text, fontSize: 20, fontWeight: "700", marginLeft: 16, flex: 1 }} numberOfLines={1}>Thread</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 100 }}>
        <View style={{ backgroundColor: colors.card, borderRadius: radius.md, padding: 18, marginBottom: 20 }}>
          <Text style={{ color: colors.accentHi, fontSize: 11, letterSpacing: 1.5 }}>{thread?.subject}</Text>
          <Text style={{ color: colors.text, fontSize: 18, fontWeight: "800", marginTop: 6 }}>{thread?.title}</Text>
          <Text style={{ color: colors.text, fontSize: 15, lineHeight: 22, marginTop: 10 }}>{thread?.body}</Text>
          <View style={{ flexDirection: "row", alignItems: "center", marginTop: 12, gap: 12 }}>
            <Pressable onPress={vote} style={{ flexDirection: "row", alignItems: "center" }}>
              <Ionicons name="arrow-up" size={18} color={colors.accent} />
              <Text style={{ color: colors.accent, fontWeight: "700", marginLeft: 4 }}>{thread?.upvotes || 0}</Text>
            </Pressable>
            <Text style={{ color: colors.textFaint, fontSize: 12 }}>By {thread?.author_name}</Text>
          </View>
        </View>
        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 12 }}>{replies.length} REPLIES</Text>
        {replies.map((r) => (
          <View key={r.id} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 3, borderLeftColor: colors.accent, padding: 14, marginBottom: 10 }}>
            <Text style={{ color: colors.text, fontSize: 14, lineHeight: 21 }}>{r.body}</Text>
            <Text style={{ color: colors.textFaint, fontSize: 11, marginTop: 6 }}>By {r.author_name}</Text>
          </View>
        ))}
      </ScrollView>
      <View style={{ position: "absolute", bottom: 0, left: 0, right: 0, padding: 16, backgroundColor: colors.bg, borderTopWidth: 1, borderTopColor: colors.stroke, flexDirection: "row", gap: 8 }}>
        <TextInput value={reply} onChangeText={setReply} placeholder='Write a reply...' placeholderTextColor={colors.textFaint} style={{ flex: 1, backgroundColor: colors.card, borderRadius: radius.md, padding: 12, color: colors.text, borderWidth: 1, borderColor: colors.stroke }} />
        <Pressable onPress={send} disabled={sending} style={{ backgroundColor: colors.accent, borderRadius: radius.md, paddingHorizontal: 20, justifyContent: "center" }}>
          {sending ? <ActivityIndicator color="#fff" /> : <Ionicons name="send" size={18} color="#fff" />}
        </Pressable>
      </View>
    </SafeAreaView>
  );
}
