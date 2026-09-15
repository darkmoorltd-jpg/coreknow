import { View, Text, ScrollView, StatusBar, Pressable, Linking } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { colors, font } from "../../constants/theme";

export default function About() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20, paddingBottom: 8 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={[font.h2, { color: colors.text, marginLeft: 16 }]}>About</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 24, alignItems: "center" }}>
        <View style={{ width: 100, height: 100, borderRadius: 50, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center", marginTop: 20 }}>
          <Text style={{ color: "#fff", fontSize: 48, fontWeight: "800" }}>C</Text>
        </View>
        <Text style={[font.h1, { color: colors.text, marginTop: 20 }]}>CoreKnow</Text>
        <Text style={{ color: colors.textDim, fontSize: 14, marginTop: 4 }}>Version 1.0.0</Text>
        <Text style={{ color: colors.text, fontSize: 15, marginTop: 24, textAlign: "center", lineHeight: 24 }}>
          AI tutor for Nigerian students. Learn any subject, any level, at your own pace.
        </Text>
        <Text style={{ color: colors.textFaint, fontSize: 13, marginTop: 40 }}>Powered by Darkmoor Ltd</Text>
      </ScrollView>
    </SafeAreaView>
  );
}