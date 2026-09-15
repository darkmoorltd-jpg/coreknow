import { useState, useEffect } from "react";
import { View, Text, TextInput, Pressable, Share, ScrollView, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import Constants from "expo-constants";
import { useAuth } from "../lib/store";
import { colors, radius } from "../constants/theme";

const BASE_URL =
  (Constants.expoConfig?.extra?.apiUrl as string) ||
  "https://coreknow.onrender.com";

export default function Referrals() {
  const user = useAuth((s) => s.user);
  const [code, setCode] = useState("");
  const [uses, setUses] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) { setLoading(false); return; }
    fetch(BASE_URL + '/api/referrals/my-code/' + user.id)
      .then((r) => r.json())
      .then((d) => {
        setCode(d.code || '');
        setUses(d.uses || 0);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [user]);

  const share = async () => {
    try {
      await Share.share({
        message: 'Join me on CoreKnow — the AI tutor for Nigerian students. Use my code ' + code + ' to get N1,000 off. https://coreknow.onrender.com',
      });
    } catch (e) {}
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}>
          <Text style={{ color: colors.text, fontSize: 32 }}>‹</Text>
        </Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Refer & Earn</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        {loading && <ActivityIndicator color={colors.accent} />}
        {!loading && (
          <>
            <View style={{ alignItems: "center", marginBottom: 32 }}>
              <View style={{ width: 96, height: 96, borderRadius: 48, backgroundColor: colors.violet, justifyContent: "center", alignItems: "center" }}>
                <Ionicons name="gift" size={48} color="#fff" />
              </View>
              <Text style={{ color: colors.text, fontSize: 26, fontWeight: "800", marginTop: 20 }}>
                Refer a friend
              </Text>
              <Text style={{ color: colors.textDim, fontSize: 15, marginTop: 8, textAlign: "center", lineHeight: 22 }}>
                Both of you get N1,000 off. They save on their first payment, you save on your next.
              </Text>
            </View>

            <Text style={{ color: colors.textFaint, fontSize: 11, fontWeight: "600", letterSpacing: 1.5, marginBottom: 8 }}>
              YOUR CODE
            </Text>
            <View style={{ backgroundColor: colors.card, borderWidth: 2, borderColor: colors.violet, borderRadius: radius.md, padding: 24, alignItems: "center", marginBottom: 16 }}>
              <Text style={{ color: colors.text, fontSize: 36, fontWeight: "800", letterSpacing: 4 }}>{code || "———"}</Text>
              <Text style={{ color: colors.textDim, fontSize: 13, marginTop: 8 }}>{uses} friend{uses === 1 ? "" : "s"} used your code</Text>
            </View>

            <Pressable onPress={share} style={{ backgroundColor: colors.violet, borderRadius: radius.md, padding: 20, alignItems: "center", flexDirection: "row", justifyContent: "center" }}>
              <Ionicons name="share-social" size={20} color="#fff" />
              <Text style={{ color: "#fff", fontSize: 16, fontWeight: "800", letterSpacing: 1, marginLeft: 10 }}>
                SHARE ON WHATSAPP
              </Text>
            </Pressable>
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}