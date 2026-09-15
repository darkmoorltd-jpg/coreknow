import { View, Text, Pressable, ScrollView, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useState } from "react";
import { colors, radius, font } from "../../constants/theme";

const EXAMS = [
  { id: "JAMB", desc: "Joint Admissions and Matriculation Board", icon: "school" },
  { id: "WAEC", desc: "West African Examinations Council", icon: "book" },
  { id: "NECO", desc: "National Examinations Council", icon: "ribbon" },
  { id: "GCE",  desc: "General Certificate of Education", icon: "document-text" },
];

export default function ExamPreference() {
  const [selected, setSelected] = useState("JAMB");

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20, paddingBottom: 8 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={[font.h2, { color: colors.text, marginLeft: 16 }]}>Exam Preference</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        <Text style={{ color: colors.textDim, fontSize: 15, marginBottom: 24 }}>Which exam are you preparing for?</Text>

        {EXAMS.map((e) => {
          const isSel = selected === e.id;
          return (
            <Pressable
              key={e.id}
              onPress={() => setSelected(e.id)}
              style={{ backgroundColor: isSel ? colors.accent : colors.card, borderRadius: radius.md, borderWidth: 2, borderColor: isSel ? colors.accentHi : colors.stroke, padding: 20, marginBottom: 12, flexDirection: "row", alignItems: "center" }}
            >
              <Ionicons name={e.icon as any} size={28} color={isSel ? "#fff" : colors.accent} />
              <View style={{ flex: 1, marginLeft: 16 }}>
                <Text style={{ color: isSel ? "#fff" : colors.text, fontSize: 17, fontWeight: "700" }}>{e.id}</Text>
                <Text style={{ color: isSel ? "#dbe4ff" : colors.textDim, fontSize: 13, marginTop: 2 }}>{e.desc}</Text>
              </View>
              {isSel && <Ionicons name="checkmark-circle" size={26} color="#fff" />}
            </Pressable>
          );
        })}
      </ScrollView>
    </SafeAreaView>
  );
}