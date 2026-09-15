import { useState, useEffect } from "react";
import { View, Text, Pressable, ScrollView, Share, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../lib/store";
import { api } from "../lib/day1";
import { colors, radius } from "../constants/theme";

export default function ShareStreak() {
  const user = useAuth((s) => s.user);
  const [streak, setStreak] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user?.id) { setLoading(false); return; }
    api.getStreak(user.id).then((d) => {
      setStreak(d.streak?.current_streak || 0);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [user]);

  const share = async () => {
    const msg = '🔥 I am on a ' + streak + '-day study streak on CoreKnow! ' +
      'The AI tutor for Nigerian students. Join me: https://coreknow.onrender.com';
    try { await Share.share({ message: msg }); } catch {}
  };

  if (loading) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}><ActivityIndicator color={colors.yellow} size="large" /></View>;
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Streak Card</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>

        {/* The shareable card — screenshot this and use as phone widget */}
        <View style={{ backgroundColor: colors.card, borderRadius: 24, borderWidth: 3, borderColor: colors.yellow, padding: 40, alignItems: "center", marginBottom: 24 }}>
          <View style={{ position: "absolute", top: 16, left: 16 }}>
            <View style={{ width: 40, height: 40, borderRadius: 20, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center" }}>
              <Text style={{ color: "#fff", fontSize: 20, fontWeight: "800" }}>C</Text>
            </View>
          </View>
          <Text style={{ fontSize: 100, marginBottom: 12 }}>🔥</Text>
          <Text style={{ color: colors.text, fontSize: 80, fontWeight: "800", letterSpacing: -2 }}>{streak}</Text>
          <Text style={{ color: colors.textDim, fontSize: 20, fontWeight: "600", letterSpacing: 4 }}>DAY STREAK</Text>
          <View style={{ height: 1, backgroundColor: colors.stroke, width: "80%", marginVertical: 24 }} />
          <Text style={{ color: colors.accentHi, fontSize: 14, fontWeight: "700", letterSpacing: 2 }}>COR EKNOW</Text>
          <Text style={{ color: colors.textFaint, fontSize: 12, marginTop: 4 }}>Powered by Darkmoor Ltd</Text>
        </View>

        <View style={{ backgroundColor: colors.bg2, borderRadius: radius.md, padding: 16, marginBottom: 20 }}>
          <Text style={{ color: colors.textDim, fontSize: 13, lineHeight: 20 }}>
            📸 Screenshot this card and set it as your phone\'s lock screen or home widget. Or share it to show off your streak.
          </Text>
        </View>

        <Pressable onPress={share} style={{ backgroundColor: colors.yellow, borderRadius: radius.md, padding: 20, alignItems: "center", flexDirection: "row", justifyContent: "center" }}>
          <Ionicons name="share-social" size={20} color="#000" />
          <Text style={{ color: "#000", fontSize: 16, fontWeight: "800", letterSpacing: 1, marginLeft: 10 }}>
            SHARE TO WHATSAPP
          </Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}