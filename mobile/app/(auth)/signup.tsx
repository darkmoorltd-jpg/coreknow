import { useState } from "react";
import { View, Text, TextInput, Pressable, ActivityIndicator, KeyboardAvoidingView, Platform, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { useAuth } from "../../lib/store";
import { colors, radius, font } from "../../constants/theme";

export default function Signup() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const signUp = useAuth((s) => s.signUp);

  const submit = async () => {
    if (!name || !email || !password) { setError('Please fill all fields'); return; }
    if (password.length < 6) { setError('Password must be at least 6 characters'); return; }
    setLoading(true); setError(null);
    const err = await signUp(email.trim(), password, name.trim());
    setLoading(false);
    if (err) setError(err);
    else router.replace("/(tabs)");
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined} style={{ flex: 1 }}>
        <View style={{ flex: 1, justifyContent: "center", padding: 28 }}>
          <View style={{ alignItems: "center", marginBottom: 40 }}>
            <Text style={[font.h1, { color: colors.text }]}>Create account</Text>
            <Text style={{ color: colors.textDim, fontSize: 15, marginTop: 6 }}>Start learning with CoreKnow</Text>
          </View>

          <TextInput value={name} onChangeText={setName} placeholder="Full name" placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 18, color: colors.text, fontSize: 16, marginBottom: 14 }} />
          <TextInput value={email} onChangeText={setEmail} placeholder="Email" placeholderTextColor={colors.textFaint} keyboardType="email-address" autoCapitalize="none" style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 18, color: colors.text, fontSize: 16, marginBottom: 14 }} />
          <TextInput value={password} onChangeText={setPassword} placeholder="Password (min 6 chars)" placeholderTextColor={colors.textFaint} secureTextEntry style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 18, color: colors.text, fontSize: 16, marginBottom: 20 }} />

          {error && <Text style={{ color: colors.red, fontSize: 14, marginBottom: 14, textAlign: "center" }}>{error}</Text>}

          <Pressable onPress={submit} disabled={loading} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 20, alignItems: "center" }}>
            {loading ? <ActivityIndicator color="#fff" /> :
              <Text style={{ color: "#fff", fontSize: 16, fontWeight: "700", letterSpacing: 1 }}>CREATE ACCOUNT</Text>}
          </Pressable>

          <Pressable onPress={() => router.back()} style={{ marginTop: 20, alignItems: "center" }}>
            <Text style={{ color: colors.textDim, fontSize: 14 }}>Already have an account? <Text style={{ color: colors.accent, fontWeight: "700" }}>Sign in</Text></Text>
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}