import { View, Text, ScrollView, Pressable, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors, spacing, radius, font } from "../../constants/theme";

const STATS = [
  { n: "5", label: "Topics done", color: colors.green },
  { n: "0", label: "Day streak", color: colors.yellow },
  { n: "12", label: "Quizzes taken", color: colors.cyan },
  { n: "78%", label: "Avg score", color: colors.pink },
];

const SETTINGS = [
  { icon: "school-outline", label: "Exam", value: "JAMB", color: colors.accent },
  { icon: "book-outline", label: "Grade level", value: "SS3", color: colors.green },
  { icon: "flame-outline", label: "Notifications", value: "Off", color: colors.yellow },
  { icon: "help-circle-outline", label: "Help & support", value: "", color: colors.cyan },
  { icon: "information-circle-outline", label: "About", value: "v1.0.0", color: colors.violet },
];

export default function ProfileScreen() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 100 }} showsVerticalScrollIndicator={false}>

        {/* Avatar + name */}
        <View style={{ alignItems: "center", marginBottom: 28 }}>
          <View style={{ width: 100, height: 100, borderRadius: 50, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center" }}>
            <Text style={{ color: "#fff", fontSize: 44, fontWeight: "800" }}>A</Text>
          </View>
          <Text style={[font.h2, { color: colors.text, marginTop: 16 }]}>Ade Johnson</Text>
          <Text style={{ color: colors.textDim, fontSize: 14, marginTop: 4 }}>SS3 Student  ·  JAMB Candidate</Text>
          <View style={{ marginTop: 12, backgroundColor: colors.accent, paddingHorizontal: 18, paddingVertical: 6, borderRadius: 999 }}>
            <Text style={{ color: "#fff", fontSize: 12, fontWeight: "700", letterSpacing: 1 }}>⭐ PRO MEMBER</Text>
          </View>
        </View>

        {/* Stats grid */}
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 12, marginBottom: 28 }}>
          {STATS.map((s, i) => (
            <View key={i} style={{ width: "48%", backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 18 }}>
              <View style={{ position: "absolute", left: 0, top: 18, bottom: 18, width: 3, backgroundColor: s.color, borderTopRightRadius: 3, borderBottomRightRadius: 3 }} />
              <Text style={{ color: colors.text, fontSize: 28, fontWeight: "800" }}>{s.n}</Text>
              <Text style={{ color: colors.textFaint, fontSize: 12, marginTop: 4 }}>{s.label}</Text>
            </View>
          ))}
        </View>

        <Text style={[font.tiny, { color: colors.textFaint, marginBottom: 12 }]}>SETTINGS</Text>

        {SETTINGS.map((row, i) => (
          <Pressable key={i} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 16, marginBottom: 10, flexDirection: "row", alignItems: "center" }}>
            <View style={{ position: "absolute", left: 0, top: 16, bottom: 16, width: 3, backgroundColor: row.color, borderTopRightRadius: 3, borderBottomRightRadius: 3 }} />
            <Ionicons name={row.icon as any} size={22} color={row.color} />
            <Text style={{ flex: 1, marginLeft: 14, color: colors.text, fontSize: 16, fontWeight: "500" }}>{row.label}</Text>
            {row.value ? <Text style={{ color: colors.textDim, fontSize: 14, marginRight: 8 }}>{row.value}</Text> : null}
            <Ionicons name="chevron-forward" size={18} color={colors.textFaint} />
          </Pressable>
        ))}

        {/* Sign out */}
        <Pressable style={{ marginTop: 20, borderWidth: 2, borderColor: colors.red, borderRadius: radius.md, padding: 18, alignItems: "center" }}>
          <Text style={{ color: colors.red, fontSize: 15, fontWeight: "700", letterSpacing: 1 }}>SIGN OUT</Text>
        </Pressable>

      </ScrollView>
    </SafeAreaView>
  );
}