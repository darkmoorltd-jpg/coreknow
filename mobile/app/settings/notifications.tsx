import { View, Text, StatusBar, Pressable } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { colors, font } from "../../constants/theme";

export default function Placeholder() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center", padding: 24 }}>
      <StatusBar barStyle="light-content" />
      <Pressable onPress={() => router.back()} style={{ position: "absolute", top: 20, left: 20 }}>
        <Text style={{ color: colors.text, fontSize: 32 }}>‹</Text>
      </Pressable>
      <Text style={[font.h1, { color: colors.text, textAlign: "center" }]}>Coming soon</Text>
      <Text style={{ color: colors.textDim, fontSize: 15, marginTop: 12, textAlign: "center" }}>
        This feature is under development.
      </Text>
    </SafeAreaView>
  );
}