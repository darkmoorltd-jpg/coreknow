import { useState } from "react";
import { View, Text, TextInput, Pressable, ScrollView, ActivityIndicator, Linking, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import Constants from "expo-constants";
import { useAuth } from "../lib/store";
import { useAccess } from "../lib/access";
import { colors, radius, font } from "../constants/theme";

const BASE_URL =
  (Constants.expoConfig?.extra?.apiUrl as string) ||
  "https://coreknow.onrender.com";

export default function Subscribe() {
  const user = useAuth((s) => s.user);
  const refresh = useAccess((s) => s.refresh);
  const [discount, setDiscount] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const start = async () => {
    if (!user) { setError('Please sign in first'); return; }
    setLoading(true); setError(null);
    try {
      const r = await fetch(BASE_URL + '/api/subscribe/init', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          email: user.email,
          tier: 'pro',
          discount_code: discount.trim(),
        }),
      });
      const d = await r.json();
      if (!d.ok) { setError(d.error || 'Could not start'); setLoading(false); return; }
      await Linking.openURL(d.authorization_url);
      setLoading(false);
    } catch (e: any) {
      setError(e.message);
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20, paddingBottom: 8 }}>
        <Pressable onPress={() => router.back()}>
          <Text style={{ color: colors.text, fontSize: 32 }}>‹</Text>
        </Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Subscribe</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 2, borderColor: colors.accent, padding: 24, marginBottom: 24 }}>
          <View style={{ position: "absolute", top: -12, right: 20, backgroundColor: colors.accent, paddingHorizontal: 12, paddingVertical: 4, borderRadius: 999 }}>
            <Text style={{ color: "#fff", fontSize: 11, fontWeight: "800", letterSpacing: 1 }}>MOST POPULAR</Text>
          </View>
          <Text style={{ color: colors.accentHi, fontSize: 12, fontWeight: "600", letterSpacing: 1.5 }}>PRO</Text>
          <Text style={{ color: colors.text, fontSize: 48, fontWeight: "800", marginTop: 8 }}>N5,000</Text>
          <Text style={{ color: colors.textDim, fontSize: 14 }}>per month</Text>
          <View style={{ height: 1, backgroundColor: colors.stroke, marginVertical: 20 }} />
          {["All 18 Chemistry topics", "All future subjects", "AI tutor unlimited", "Practice & Exam mode", "Video solutions", "Parent dashboard"].map((f, i) => (
            <View key={i} style={{ flexDirection: "row", alignItems: "center", marginBottom: 12 }}>
              <Ionicons name="checkmark-circle" size={20} color={colors.green} />
              <Text style={{ color: colors.text, fontSize: 15, marginLeft: 12 }}>{f}</Text>
            </View>
          ))}
        </View>

        <Text style={{ color: colors.textFaint, fontSize: 11, fontWeight: "600", letterSpacing: 1.5, marginBottom: 8 }}>
          DISCOUNT CODE (optional)
        </Text>
        <TextInput
          value={discount}
          onChangeText={setDiscount}
          placeholder="e.g. LAUNCH50"
          placeholderTextColor={colors.textFaint}
          autoCapitalize="characters"
          style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 16, color: colors.text, fontSize: 16, marginBottom: 20 }}
        />

        {error && (
          <Text style={{ color: colors.red, fontSize: 14, marginBottom: 12, textAlign: "center" }}>{error}</Text>
        )}

        <Pressable onPress={start} disabled={loading} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 20, alignItems: "center" }}>
          {loading ? <ActivityIndicator color="#fff" /> :
            <Text style={{ color: "#fff", fontSize: 16, fontWeight: "800", letterSpacing: 1 }}>PAY WITH PAYSTACK</Text>}
        </Pressable>

        <Pressable onPress={() => router.push("/trial")} style={{ marginTop: 16, alignItems: "center" }}>
          <Text style={{ color: colors.accent, fontSize: 14, fontWeight: "600" }}>Or start a free 7-day trial</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}