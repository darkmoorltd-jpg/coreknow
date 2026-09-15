import { useState } from "react";
import { View, Text, Pressable, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import Constants from "expo-constants";
import { useAuth } from "../lib/store";
import { useAccess } from "../lib/access";
import { colors, radius } from "../constants/theme";

const BASE_URL =
  (Constants.expoConfig?.extra?.apiUrl as string) ||
  "https://coreknow.onrender.com";

export default function Trial() {
  const user = useAuth((s) => s.user);
  const refresh = useAccess((s) => s.refresh);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const start = async () => {
    if (!user) { setError('Sign in first'); return; }
    setLoading(true); setError(null);
    try {
      const r = await fetch(BASE_URL + '/api/trial/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, email: user.email }),
      });
      const d = await r.json();
      if (!d.ok) { setError(d.error); setLoading(false); return; }
      await refresh();
      router.replace('/(tabs)');
    } catch (e: any) {
      setError(e.message);
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}>
          <Text style={{ color: colors.text, fontSize: 32 }}>‹</Text>
        </Pressable>
      </View>
      <View style={{ flex: 1, padding: 28, justifyContent: "center" }}>
        <View style={{ alignItems: "center", marginBottom: 40 }}>
          <View style={{ width: 120, height: 120, borderRadius: 60, backgroundColor: colors.green, justifyContent: "center", alignItems: "center" }}>
            <Text style={{ color: "#fff", fontSize: 60, fontWeight: "800" }}>7</Text>
          </View>
          <Text style={{ color: colors.text, fontSize: 32, fontWeight: "800", marginTop: 24, textAlign: "center" }}>
            Free trial
          </Text>
          <Text style={{ color: colors.textDim, fontSize: 16, marginTop: 12, textAlign: "center", lineHeight: 24 }}>
            Full access to every lesson, video, and quiz for 7 days.
          </Text>
        </View>

        {["All 18 topics unlocked", "No card required now", "Cancel anytime", "7 days free"].map((f, i) => (
          <View key={i} style={{ flexDirection: "row", alignItems: "center", marginBottom: 14 }}>
            <Ionicons name="checkmark-circle" size={22} color={colors.green} />
            <Text style={{ color: colors.text, fontSize: 16, marginLeft: 12 }}>{f}</Text>
          </View>
        ))}

        {error && (
          <Text style={{ color: colors.red, fontSize: 14, marginTop: 20, textAlign: "center" }}>{error}</Text>
        )}

        <Pressable onPress={start} disabled={loading} style={{ backgroundColor: colors.green, borderRadius: radius.md, padding: 20, alignItems: "center", marginTop: 40 }}>
          {loading ? <ActivityIndicator color="#fff" /> :
            <Text style={{ color: "#fff", fontSize: 16, fontWeight: "800", letterSpacing: 1 }}>START FREE TRIAL</Text>}
        </Pressable>
      </View>
    </SafeAreaView>
  );
}