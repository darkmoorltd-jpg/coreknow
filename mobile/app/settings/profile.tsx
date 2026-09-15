import { useState } from "react";
import { View, Text, TextInput, Pressable, ScrollView, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { useAuth } from "../../lib/store";
import { colors, radius, font } from "../../constants/theme";

export default function EditProfile() {
  const user = useAuth((s) => s.user);
  const [name, setName] = useState(user?.name || "Ade Johnson");
  const [phone, setPhone] = useState("");
  const [school, setSchool] = useState("");

  const save = () => { router.back(); };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20, paddingBottom: 8 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={[font.h2, { color: colors.text, marginLeft: 16 }]}>Edit Profile</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        <View style={{ alignItems: "center", marginBottom: 30 }}>
          <View style={{ width: 100, height: 100, borderRadius: 50, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center" }}>
            <Text style={{ color: "#fff", fontSize: 40, fontWeight: "800" }}>{name[0] || "A"}</Text>
          </View>
          <Pressable style={{ marginTop: 12 }}><Text style={{ color: colors.accent, fontSize: 14, fontWeight: "600" }}>Change photo</Text></Pressable>
        </View>

        {[{label: 'Full name', value: name, set: setName, keyboard: 'default' as const},
          {label: 'Phone number', value: phone, set: setPhone, keyboard: 'phone-pad' as const},
          {label: 'School', value: school, set: setSchool, keyboard: 'default' as const}].map((f, i) => (
          <View key={i} style={{ marginBottom: 20 }}>
            <Text style={[font.tiny, { color: colors.textFaint, marginBottom: 8 }]}>{f.label.toUpperCase()}</Text>
            <TextInput
              value={f.value}
              onChangeText={f.set}
              keyboardType={f.keyboard}
              style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 16, color: colors.text, fontSize: 16 }}
            />
          </View>
        ))}

        <Pressable onPress={save} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 20, alignItems: "center", marginTop: 10 }}>
          <Text style={{ color: "#fff", fontSize: 16, fontWeight: "700", letterSpacing: 1 }}>SAVE CHANGES</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}