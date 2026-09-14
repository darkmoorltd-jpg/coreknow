import { useState, useRef, useEffect } from "react";
import { View, Text, TextInput, Pressable, ScrollView, KeyboardAvoidingView, Platform, ActivityIndicator } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { api } from "../../lib/api";
import { colors, spacing, radius } from "../../constants/theme";

type Msg = { role: 'user' | 'assistant'; content: string };

export default function ChatScreen() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const ref = useRef<ScrollView>(null);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;
    const msgs: Msg[] = [...messages, { role: 'user', content: text }];
    setMessages(msgs);
    setInput("");
    setLoading(true);
    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const res = await api.chat(text, history);
      setMessages([...msgs, { role: 'assistant', content: res.reply }]);
    } catch (e) {
      setMessages([...msgs, { role: 'assistant', content: 'Connection failed. Try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setTimeout(() => ref.current?.scrollToEnd({ animated: true }), 100);
  }, [messages, loading]);

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : "height"}>
        <ScrollView ref={ref} contentContainerStyle={{ padding: spacing.md }}>
          {messages.length === 0 && (
            <View style={{ alignItems: "center", paddingVertical: 80 }}>
              <Text style={{ fontSize: 56 }}>🧠</Text>
              <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700", marginTop: 16 }}>Ask me anything</Text>
            </View>
          )}
          {messages.map((m, i) => (
            <View key={i} style={{ alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '85%', marginVertical: 6, backgroundColor: m.role === 'user' ? colors.card : 'transparent', padding: m.role === 'user' ? 14 : 0, borderRadius: 16 }}>
              <Text style={{ color: colors.text, fontSize: 15, lineHeight: 22 }}>{m.content}</Text>
            </View>
          ))}
          {loading && <ActivityIndicator color={colors.accent} />}
        </ScrollView>
        <View style={{ flexDirection: "row", alignItems: "flex-end", padding: spacing.md, gap: 8, borderTopWidth: 1, borderTopColor: colors.border }}>
          <TextInput
            value={input}
            onChangeText={setInput}
            placeholder="Ask CoreKnow..."
            placeholderTextColor={colors.textFaint}
            multiline
            style={{ flex: 1, backgroundColor: colors.card, color: colors.text, borderRadius: radius.md, padding: 12, maxHeight: 120, fontSize: 15 }}
          />
          <Pressable onPress={send} style={{ width: 48, height: 48, borderRadius: 24, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center" }}>
            <Ionicons name="send" size={20} color="#fff" />
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}