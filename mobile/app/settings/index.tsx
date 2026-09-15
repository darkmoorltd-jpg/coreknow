import { View, Text, Pressable, ScrollView, StatusBar, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../lib/store";
import { colors, radius, font } from "../../constants/theme";

const ROWS = [
  { icon: "camera-outline", label: "Scan Homework", route: "/scan", color: colors.green },
  { icon: "people-outline", label: "Parent Dashboard", route: "/parent", color: colors.pink },
  { icon: "sparkles-outline", label: "AI Practice", route: "/ai-practice", color: colors.violet },
  { icon: "document-text-outline", label: "Formula Sheets", route: "/formulas", color: colors.cyan },
  { icon: "bookmark-outline", label: "My Bookmarks", route: "/bookmarks", color: colors.yellow },
  { icon: "star-outline", label: "Upgrade to Pro", route: "/subscribe", color: colors.accent },
  { icon: "gift-outline", label: "Refer & Earn", route: "/referrals", color: colors.violet },
  { icon: "business-outline", label: "School License", route: "/school", color: colors.green },
  { icon: "person-outline", label: "Edit profile", route: "/settings/profile", color: colors.accent },
  { icon: "language-outline", label: "Language", route: "/language", color: colors.accent },
  { icon: "trophy-outline", label: "Leaderboard", route: "/leaderboard", color: colors.yellow },
  { icon: "options-outline", label: "Preferences", route: "/preferences", color: colors.accent },
  { icon: "school-outline", label: "Exam preference", route: "/settings/exam", color: colors.green },
  { icon: "book-outline", label: "Grade level", route: "/settings/grade", color: colors.yellow },
  { icon: "notifications-outline", label: "Notifications", route: "/settings/notifications", color: colors.violet },
  { icon: "card-outline", label: "Payment history", route: "/payments", color: colors.yellow },
  { icon: "color-palette-outline", label: "Appearance", route: "/settings/appearance", color: colors.cyan },
  { icon: "information-circle-outline", label: "About", route: "/settings/about", color: colors.pink },
];

export default function Settings() {
  const signOut = useAuth((s) => s.signOut);

  const doSignOut = () => {
    Alert.alert('Sign out', 'Are you sure?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Sign out', style: 'destructive', onPress: async () => { await signOut(); router.replace('/(auth)/login'); } },
    ]);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />

      <View style={{ flexDirection: "row", alignItems: "center", padding: 20, paddingBottom: 8 }}>
        <Pressable onPress={() => router.back()}>
          <Text style={{ color: colors.text, fontSize: 32 }}>‹</Text>
        </Pressable>
        <Text style={[font.h2, { color: colors.text, marginLeft: 16 }]}>Settings</Text>
      </View>

      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        {ROWS.map((r, i) => (
          <Pressable
            key={i}
            onPress={() => router.push(r.route as any)}
            style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 18, marginBottom: 10, flexDirection: "row", alignItems: "center" }}
          >
            <View style={{ position: "absolute", left: 0, top: 18, bottom: 18, width: 3, backgroundColor: r.color, borderTopRightRadius: 3, borderBottomRightRadius: 3 }} />
            <Ionicons name={r.icon as any} size={22} color={r.color} />
            <Text style={{ flex: 1, marginLeft: 14, color: colors.text, fontSize: 16, fontWeight: "500" }}>{r.label}</Text>
            <Ionicons name="chevron-forward" size={18} color={colors.textFaint} />
          </Pressable>
        ))}

        <Pressable onPress={doSignOut} style={{ marginTop: 30, borderWidth: 2, borderColor: colors.red, borderRadius: radius.md, padding: 18, alignItems: "center" }}>
          <Text style={{ color: colors.red, fontSize: 15, fontWeight: "700", letterSpacing: 1 }}>SIGN OUT</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}