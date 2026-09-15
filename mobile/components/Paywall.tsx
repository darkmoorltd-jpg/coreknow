import { View, Text, Pressable } from "react-native";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { colors, radius } from "../constants/theme";

export default function Paywall() {
  return (
    <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center", padding: 28 }}>
      <View style={{ alignItems: "center", marginBottom: 32 }}>
        <View style={{ width: 96, height: 96, borderRadius: 48, backgroundColor: colors.card, borderWidth: 2, borderColor: colors.accent, justifyContent: "center", alignItems: "center" }}>
          <Ionicons name="lock-closed" size={44} color={colors.accent} />
        </View>
        <Text style={{ color: colors.text, fontSize: 26, fontWeight: "800", marginTop: 24, textAlign: "center" }}>
          Unlock all lessons
        </Text>
        <Text style={{ color: colors.textDim, fontSize: 15, marginTop: 10, textAlign: "center", lineHeight: 22 }}>
          You've finished your free lessons. Subscribe to continue.
        </Text>
      </View>

      <Pressable onPress={() => router.push("/subscribe")} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 20, alignItems: "center", marginBottom: 12 }}>
        <Text style={{ color: "#fff", fontSize: 16, fontWeight: "800", letterSpacing: 1 }}>
          SUBSCRIBE — N5,000/MONTH
        </Text>
      </Pressable>

      <Pressable onPress={() => router.push("/trial")} style={{ backgroundColor: colors.card, borderWidth: 2, borderColor: colors.accent, borderRadius: radius.md, padding: 20, alignItems: "center" }}>
        <Text style={{ color: colors.accent, fontSize: 16, fontWeight: "800", letterSpacing: 1 }}>
          START FREE TRIAL
        </Text>
      </Pressable>
    </View>
  );
}