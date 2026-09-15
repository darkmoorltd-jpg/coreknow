import { useState, useRef, useEffect } from "react";
import { View, Text, TextInput, Pressable, ScrollView, KeyboardAvoidingView, Platform, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { api } from "../../lib/api";
import { colors, spacing, radius, font } from "../../constants/theme";

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
    setTimeout(() => ref.current?.scrollToEnd({ animated: true }), 120);
  }, [messages, loading]);

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />

      {/* Header */}
      <View style={{ flexDirection: "row", alignItems: "center", paddingHorizontal: 20, paddingVertical: 14, borderBottomWidth: 1, borderBottomColor: colors.stroke }}>
        <View style={{ width: 44, height: 44, borderRadius: 22, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center" }}>
          <Text style={{ color: "#fff", fontSize: 20, fontWeight: "800" }}>C</Text>
        </View>
        <View style={{ marginLeft: 12, flex: 1 }}>
          <Text style={[font.h3, { color: colors.text }]}>CoreKnow</Text>
          <View style={{ flexDirection: "row", alignItems: "center", marginTop: 2 }}>
            <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: colors.green }} />
            <Text style={{ color: colors.green, fontSize: 12, marginLeft: 6, fontWeight: "600" }}>Online</Text>
          </View>
        </View>
        <Text style={{ color: colors.textDim, fontSize: 22 }}>⋯</Text>
      </View>

      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
        <ScrollView ref={ref} contentContainerStyle={{ padding: 20, paddingBottom: 140 }}>
          {messages.length === 0 && (
            <View style={{ alignItems: "center", paddingVertical: 80 }}>
              <View style={{ width: 100, height: 100, borderRadius: 50, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center" }}>
                <Text style={{ fontSize: 56, color: "#fff", fontWeight: "800" }}>C</Text>
              </View>
              <Text style={[font.h2, { color: colors.text, marginTop: 24 }]}>Ask me anything</Text>
              <Text style={{ color: colors.textDim, fontSize: 15, marginTop: 8, textAlign: "center", paddingHorizontal: 40 }}>
                Type or upload a question. I'll explain step by step.
              </Text>
            </View>
          )}

          {messages.map((m, i) => (
            <View key={i} style={{ marginVertical: 8 }}>
              {m.role === 'user' ? (
                <View style={{ alignSelf: "flex-end", maxWidth: "85%", backgroundColor: colors.accent, paddingHorizontal: 18, paddingVertical: 14, borderRadius: 22, borderBottomRightRadius: 6 }}>
                  <Text style={{ color: "#fff", fontSize: 15, lineHeight: 22 }}>{m.content}</Text>
                </View>
              ) : (
                <View style={{ flexDirection: "row", maxWidth: "90%" }}>
                  <View style={{ width: 32, height: 32, borderRadius: 16, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center", marginRight: 10 }}>
                    <Text style={{ color: "#fff", fontSize: 14, fontWeight: "800" }}>C</Text>
                  </View>
                  <View style={{ flex: 1, paddingTop: 4 }}>
                    <Text style={{ color: colors.accentHi, fontSize: 12, fontWeight: "700", marginBottom: 4 }}>CoreKnow</Text>
                    <Text style={{ color: colors.text, fontSize: 15, lineHeight: 24 }}>{m.content}</Text>
                  </View>
                </View>
              )}
            </View>
          ))}

          {loading && (
            <View style={{ flexDirection: "row", alignItems: "center", gap: 8, paddingVertical: 12 }}>
              <ActivityIndicator color={colors.accent} size="small" />
              <Text style={{ color: colors.textDim, fontSize: 14 }}>CoreKnow is thinking...</Text>
            </View>
          )}
        </ScrollView>

        {/* Input bar */}
        <View style={{ flexDirection: "row", alignItems: "flex-end", paddingHorizontal: 16, paddingVertical: 12, gap: 10, borderTopWidth: 1, borderTopColor: colors.stroke, backgroundColor: colors.bg }}>
          <View style={{ flex: 1, backgroundColor: colors.card, borderRadius: 24, borderWidth: 1, borderColor: colors.strokeHi, flexDirection: "row", alignItems: "flex-end", paddingHorizontal: 16, paddingVertical: 4 }}>
            <TextInput
              value={input}
              onChangeText={setInput}
              placeholder="Ask CoreKnow..."
              placeholderTextColor={colors.textFaint}
              multiline
              style={{ flex: 1, color: colors.text, fontSize: 15, maxHeight: 100, paddingVertical: 10 }}
            />
          </View>
          <Pressable onPress={send} disabled={!input.trim() || loading} style={{ width: 52, height: 52, borderRadius: 26, backgroundColor: input.trim() ? colors.accent : colors.card, justifyContent: "center", alignItems: "center", borderWidth: 1, borderColor: input.trim() ? colors.accent : colors.stroke }}>
            <Ionicons name="send" size={20} color={input.trim() ? "#fff" : colors.textFaint} />
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}