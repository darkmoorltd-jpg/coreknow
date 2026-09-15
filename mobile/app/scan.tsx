import { useState } from "react";
import { View, Text, Pressable, ScrollView, Image, ActivityIndicator, TextInput, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import * as ImagePicker from "expo-image-picker";
import { useAuth } from "../lib/store";
import { day3 } from "../lib/day3";
import { colors, radius } from "../constants/theme";

export default function Scan() {
  const user = useAuth((s) => s.user);
  const [image, setImage] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pick = async () => {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) { setError('Camera permission needed'); return; }
    const res = await ImagePicker.launchCameraAsync({
      allowsEditing: false,
      quality: 0.7,
    });
    if (!res.canceled && res.assets[0]) {
      setImage(res.assets[0].uri);
      setAnswer(null);
    }
  };

  const pickGallery = async () => {
    const res = await ImagePicker.launchImageLibraryAsync({
      allowsEditing: false,
      quality: 0.7,
    });
    if (!res.canceled && res.assets[0]) {
      setImage(res.assets[0].uri);
      setAnswer(null);
    }
  };

  const ask = async () => {
    if (!question.trim()) { setError('Type the question'); return; }
    setLoading(true); setError(null);
    try {
      const d = await day3.askFromText(user?.id || '', question.trim());
      if (!d.ok) { setError(d.error); setLoading(false); return; }
      setAnswer(d.answer);
    } catch (e: any) {
      setError(e.message);
    }
    setLoading(false);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Scan Homework</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>

        {!image && (
          <View style={{ alignItems: "center", paddingVertical: 40 }}>
            <Ionicons name="camera" size={64} color={colors.accent} />
            <Text style={{ color: colors.text, fontSize: 20, fontWeight: "700", marginTop: 20 }}>Snap your homework</Text>
            <Text style={{ color: colors.textDim, fontSize: 14, marginTop: 8, textAlign: "center" }}>
              Point camera at any question — I will solve it step by step.
            </Text>
          </View>
        )}

        {image && (
          <Image source={{ uri: image }} style={{ width: "100%", height: 260, borderRadius: radius.md, marginBottom: 20 }} resizeMode="cover" />
        )}

        <View style={{ flexDirection: "row", gap: 12, marginBottom: 24 }}>
          <Pressable onPress={pick} style={{ flex: 1, backgroundColor: colors.accent, borderRadius: radius.md, padding: 18, alignItems: "center", flexDirection: "row", justifyContent: "center" }}>
            <Ionicons name="camera" size={20} color="#fff" />
            <Text style={{ color: "#fff", fontWeight: "700", marginLeft: 8 }}>Camera</Text>
          </Pressable>
          <Pressable onPress={pickGallery} style={{ flex: 1, backgroundColor: colors.card, borderWidth: 2, borderColor: colors.accent, borderRadius: radius.md, padding: 18, alignItems: "center", flexDirection: "row", justifyContent: "center" }}>
            <Ionicons name="images" size={20} color={colors.accent} />
            <Text style={{ color: colors.accent, fontWeight: "700", marginLeft: 8 }}>Gallery</Text>
          </Pressable>
        </View>

        <Text style={{ color: colors.textFaint, fontSize: 11, fontWeight: "600", letterSpacing: 1.5, marginBottom: 8 }}>OR TYPE THE QUESTION</Text>
        <TextInput
          value={question}
          onChangeText={setQuestion}
          placeholder="e.g. Balance: Fe + O2 -> Fe2O3"
          placeholderTextColor={colors.textFaint}
          multiline
          style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 16, color: colors.text, fontSize: 15, minHeight: 90, textAlignVertical: "top", marginBottom: 16 }}
        />

        {error && <Text style={{ color: colors.red, fontSize: 14, marginBottom: 12, textAlign: "center" }}>{error}</Text>}

        <Pressable onPress={ask} disabled={loading} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 20, alignItems: "center" }}>
          {loading ? <ActivityIndicator color="#fff" /> :
            <Text style={{ color: "#fff", fontSize: 16, fontWeight: "800", letterSpacing: 1 }}>SOLVE</Text>}
        </Pressable>

        {answer && (
          <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderLeftWidth: 4, borderLeftColor: colors.green, padding: 20, marginTop: 24 }}>
            <Text style={{ color: colors.green, fontSize: 12, fontWeight: "700", letterSpacing: 1, marginBottom: 10 }}>ANSWER</Text>
            <Text style={{ color: colors.text, fontSize: 15, lineHeight: 24 }}>{answer}</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}