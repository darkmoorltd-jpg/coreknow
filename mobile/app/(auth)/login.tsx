import { useState } from "react";
import { View, Text, TextInput, Pressable, ActivityIndicator, KeyboardAvoidingView, Platform, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { useAuth } from "../../lib/store";
import { colors, radius, font } from "../../constants/theme";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const signIn = useAuth((s) => s.signIn);

  const submit = async () => {
    if (!email || !password) { setError('Please fill both fields'); return; }
    setLoading(true); setError(null);
    const err = await signIn(email.trim(), password);
    setLoading(false);
    if (err) setError(err);
    else router.replace("/(tabs)");
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined} style={{ flex: 1 }}>
        <View style={{ flex: 1, justifyContent: "center", padding: 28 }}>
          <View style={{ alignItems: "center", marginBottom: 48 }}>
            <View style={{ width: 80, height: 80, borderRadius: 40, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center" }}>
              <Text style={{ color: "#fff", fontSize: 40, fontWeight: "800" }}>C</Text>
            </View>
            <Text style={[font.h1, { color: colors.text, marginTop: 20 }]}>Welcome back</Text>
            <Text style={{ color: colors.textDim, fontSize: 15, marginTop: 6 }}>Sign in to continue learning</Text>
          </View>

          <TextInput
            value={email}
            onChangeText={setEmail}
            placeholder="Email"
            placeholderTextColor={colors.textFaint}
            keyboardType="email-address"
            autoCapitalize="none"
            style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 18, color: colors.text, fontSize: 16, marginBottom: 14 }}
          />
          <TextInput
            value={password}
            onChangeText={setPassword}
            placeholder="Password"
            placeholderTextColor={colors.textFaint}
            secureTextEntry
            style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 18, color: colors.text, fontSize: 16, marginBottom: 20 }}
          />

          {error && (
            <Text style={{ color: colors.red, fontSize: 14, marginBottom: 14, textAlign: "center" }}>{error}</Text>
          )}

          <Pressable onPress={submit} disabled={loading} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 20, alignItems: "center" }}>
            {loading ? <ActivityIndicator color="#fff" /> :
              <Text style={{ color: "#fff", fontSize: 16, fontWeight: "700", letterSpacing: 1 }}>SIGN IN</Text>}
          </Pressable>

          <Pressable onPress={() => router.push("/(auth)/forgot")} style={{ marginTop: 14, alignItems: "center" }}>
            <Text style={{ color: colors.accent, fontSize: 14, fontWeight: "600" }}>Forgot password?</Text>
          </Pressable>

          <Pressable onPress={() => router.push("/(auth)/signup")} style={{ marginTop: 20, alignItems: "center" }}>
            <Text style={{ color: colors.textDim, fontSize: 14 }}>Don't have an account? <Text style={{ color: colors.accent, fontWeight: "700" }}>Sign up</Text></Text>
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}