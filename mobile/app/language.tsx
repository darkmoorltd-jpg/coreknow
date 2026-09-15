import { useState } from "react";
import { View, Text, Pressable, ScrollView, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../lib/store";
import { day3 } from "../lib/day3";
import { colors, radius } from "../constants/theme";

const LANGS = [
  { code: "en", label: "English", desc: "Standard English" },
  { code: "pidgin", label: "Pidgin", desc: "Nigerian Pidgin English" },
  { code: "yoruba", label: "Yoruba", desc: "Èdè Yorùbá" },
  { code: "igbo", label: "Igbo", desc: "Asụsụ Igbo" },
  { code: "hausa", label: "Hausa", desc: "Harshen Hausa" },
];

export default function LanguageScreen() {
  const user = useAuth((s) => s.user);
  const [selected, setSelected] = useState("en");

  const choose = async (code: string) => {
    setSelected(code);
    if (user?.id) await day3.setLanguage(user.id, code);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Language</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        <Text style={{ color: colors.textDim, fontSize: 15, marginBottom: 20 }}>
          AI responses will be given in your chosen language.
        </Text>
        {LANGS.map((l) => {
          const isSel = selected === l.code;
          return (
            <Pressable
              key={l.code}
              onPress={() => choose(l.code)}
              style={{ backgroundColor: isSel ? colors.accent : colors.card, borderRadius: radius.md, borderWidth: 2, borderColor: isSel ? colors.accent : colors.stroke, padding: 18, marginBottom: 10, flexDirection: "row", alignItems: "center" }}
            >
              <View style={{ flex: 1 }}>
                <Text style={{ color: isSel ? "#fff" : colors.text, fontSize: 16, fontWeight: "700" }}>{l.label}</Text>
                <Text style={{ color: isSel ? "#dbe4ff" : colors.textDim, fontSize: 13, marginTop: 2 }}>{l.desc}</Text>
              </View>
              {isSel && <Ionicons name="checkmark-circle" size={24} color="#fff" />}
            </Pressable>
          );
        })}
      </ScrollView>
    </SafeAreaView>
  );
}