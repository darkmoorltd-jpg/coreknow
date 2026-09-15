import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, Switch, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../lib/store";
import { day4 } from "../lib/day4";
import { colors, radius } from "../constants/theme";

export default function Preferences() {
  const user = useAuth((s) => s.user);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [biometric, setBiometric] = useState(false);
  const [push, setPush] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) { setLoading(false); return; }
    day4.getPrefs(user.id).then((d) => {
      setTheme(d.theme || 'dark');
      setBiometric(d.biometric_enabled || false);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [user]);

  const save = async (t: string, b: boolean) => {
    if (!user?.id) return;
    await day4.savePrefs(user.id, t, b);
  };

  if (loading) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}><ActivityIndicator color={colors.accent} /></View>;
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Preferences</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20 }}>

        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 12 }}>APPEARANCE</Text>
        <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 18, marginBottom: 24, flexDirection: "row", alignItems: "center" }}>
          <Ionicons name={theme === "dark" ? "moon" : "sunny"} size={22} color={colors.accent} />
          <Text style={{ flex: 1, marginLeft: 14, color: colors.text, fontSize: 16 }}>Dark mode</Text>
          <Switch
            value={theme === "dark"}
            onValueChange={(v) => { setTheme(v ? 'dark' : 'light'); save(v ? 'dark' : 'light', biometric); }}
            trackColor={{ false: colors.stroke, true: colors.accent }}
            thumbColor='#fff'
          />
        </View>

        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 12 }}>SECURITY</Text>
        <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 18, marginBottom: 24, flexDirection: "row", alignItems: "center" }}>
          <Ionicons name="finger-print" size={22} color={colors.accent} />
          <Text style={{ flex: 1, marginLeft: 14, color: colors.text, fontSize: 16 }}>Biometric login</Text>
          <Switch
            value={biometric}
            onValueChange={(v) => { setBiometric(v); save(theme, v); }}
            trackColor={{ false: colors.stroke, true: colors.accent }}
            thumbColor='#fff'
          />
        </View>

        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 12 }}>NOTIFICATIONS</Text>
        <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 18, marginBottom: 24, flexDirection: "row", alignItems: "center" }}>
          <Ionicons name="notifications" size={22} color={colors.accent} />
          <Text style={{ flex: 1, marginLeft: 14, color: colors.text, fontSize: 16 }}>Study reminders</Text>
          <Switch
            value={push}
            onValueChange={setPush}
            trackColor={{ false: colors.stroke, true: colors.accent }}
            thumbColor='#fff'
          />
        </View>

        <View style={{ backgroundColor: colors.bg2, borderRadius: radius.md, padding: 18 }}>
          <Text style={{ color: colors.textDim, fontSize: 13, lineHeight: 20 }}>
            Theme changes apply on next app reload. Biometric setup will be requested the next time you open the app.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}