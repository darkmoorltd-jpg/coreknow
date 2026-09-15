import { useState, useEffect } from "react";
import { View, Text, TextInput, Pressable, ScrollView, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import Constants from "expo-constants";
import { useAuth } from "../lib/store";
import { day3 } from "../lib/day3";
import { colors, radius } from "../constants/theme";

const BASE =
  (Constants.expoConfig?.extra?.apiUrl as string) ||
  "https://coreknow.onrender.com";

export default function Parent() {
  const user = useAuth((s) => s.user);
  const [childEmail, setChildEmail] = useState("");
  const [children, setChildren] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [linking, setLinking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user?.id) { setLoading(false); return; }
    fetch(BASE + '/api/parent/dashboard/' + user.id)
      .then((r) => r.json())
      .then((d) => {
        setChildren(d.children || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [user]);

  const link = async () => {
    if (!childEmail.trim()) { setError('Enter child\'s email'); return; }
    setLinking(true); setError(null);
    try {
      const r = await fetch(BASE + '/api/parent/link', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ parent_id: user?.id, child_email: childEmail.trim() }),
      });
      const d = await r.json();
      if (!d.ok) { setError(d.error); setLinking(false); return; }
      setChildEmail('');
      const reload = await fetch(BASE + '/api/parent/dashboard/' + user?.id);
      const rd = await reload.json();
      setChildren(rd.children || []);
    } catch (e: any) {
      setError(e.message);
    }
    setLinking(false);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Parent Dashboard</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>

        <Text style={{ color: colors.text, fontSize: 18, fontWeight: "700", marginBottom: 12 }}>Link a child</Text>
        <TextInput
          value={childEmail}
          onChangeText={setChildEmail}
          placeholder="child@example.com"
          placeholderTextColor={colors.textFaint}
          autoCapitalize="none"
          keyboardType="email-address"
          style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 16, color: colors.text, fontSize: 15, marginBottom: 12 }}
        />
        {error && <Text style={{ color: colors.red, fontSize: 14, marginBottom: 8 }}>{error}</Text>}
        <Pressable onPress={link} disabled={linking} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 16, alignItems: "center", marginBottom: 32 }}>
          {linking ? <ActivityIndicator color="#fff" /> :
            <Text style={{ color: "#fff", fontWeight: "700" }}>LINK CHILD</Text>}
        </Pressable>

        <Text style={{ color: colors.textFaint, fontSize: 11, fontWeight: "600", letterSpacing: 1.5, marginBottom: 12 }}>LINKED CHILDREN</Text>
        {loading && <ActivityIndicator color={colors.accent} />}
        {!loading && children.length === 0 && (
          <View style={{ alignItems: "center", paddingVertical: 40 }}>
            <Ionicons name="people-outline" size={56} color={colors.textFaint} />
            <Text style={{ color: colors.textDim, fontSize: 15, marginTop: 12 }}>No children linked yet</Text>
          </View>
        )}
        {children.map((c) => (
          <View key={c.child_id} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 18, marginBottom: 12 }}>
            <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1 }}>STUDENT</Text>
            <Text style={{ color: colors.text, fontSize: 15, fontWeight: "600", marginTop: 4 }}>{c.child_id.slice(0, 12)}...</Text>
            <View style={{ flexDirection: "row", marginTop: 14, gap: 20 }}>
              <View style={{ flex: 1 }}>
                <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1 }}>STREAK</Text>
                <Text style={{ color: colors.yellow, fontSize: 24, fontWeight: "800", marginTop: 2 }}>
                  {c.streak?.current_streak || 0}🔥
                </Text>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1 }}>BADGES</Text>
                <Text style={{ color: colors.green, fontSize: 24, fontWeight: "800", marginTop: 2 }}>{c.badge_count || 0}</Text>
              </View>
            </View>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}