import { View, Text, ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { colors, spacing } from "../../constants/theme";

export default function ProfileScreen() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView contentContainerStyle={{ padding: spacing.lg }}>
        <View style={{ alignItems: "center" }}>
          <View style={{ width: 88, height: 88, borderRadius: 44, backgroundColor: colors.accent, justifyContent: 'center', alignItems: 'center' }}>
            <Text style={{ fontSize: 40 }}>🧠</Text>
          </View>
          <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700", marginTop: 12 }}>CoreKnow Student</Text>
          <Text style={{ color: colors.textDim, fontSize: 13, marginTop: 4 }}>Powered by Darkmoor Ltd</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}