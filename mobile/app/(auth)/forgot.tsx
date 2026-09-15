import { useState } from "react";
import { View, Text, TextInput, Pressable, ActivityIndicator, KeyboardAvoidingView, Platform, StatusBar, ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { day8 } from "../../lib/day8";
import { colors, radius } from "../../constants/theme";

export default function Forgot() {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [devCode, setDevCode] = useState<string | null>(null);

  const sendCode = async () => {
    if (!email.trim()) { setError('Enter your email'); return; }
    setLoading(true); setError(null);
    const d = await day8.forgotPassword(email.trim());
    setLoading(false);
    if (!d.ok) { setError(d.error); return; }
    if (d.dev_code) setDevCode(d.dev_code);
    setStep(2);
  };

  const doReset = async () => {
    if (!code.trim() || !newPassword) { setError('Fill both fields'); return; }
    if (newPassword.length < 6) { setError('Min 6 characters'); return; }
    setLoading(true); setError(null);
    const d = await day8.resetPassword(email.trim(), code.trim(), newPassword);
    setLoading(false);
    if (!d.ok) { setError(d.error); return; }
    router.replace('/(auth)/login');
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : undefined} style={{ flex: 1 }}>
        <ScrollView contentContainerStyle={{ flexGrow: 1, justifyContent: "center", padding: 28 }}>
          <View style={{ alignItems: "center", marginBottom: 40 }}>
            <View style={{ width: 80, height: 80, borderRadius: 40, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center" }}>
              <Ionicons name="key" size={40} color="#fff" />
            </View>
            <Text style={{ color: colors.text, fontSize: 26, fontWeight: "800", marginTop: 20 }}>Reset Password</Text>
            <Text style={{ color: colors.textDim, fontSize: 14, marginTop: 8, textAlign: "center" }}>
              {step === 1 ? 'Enter your email. We will send a 6-character code.' : 'Enter the code and your new password.'}
            </Text>
          </View>

          {step === 1 ? (
            <>
              <TextInput
                value={email}
                onChangeText={setEmail}
                placeholder="you@example.com"
                placeholderTextColor={colors.textFaint}
                keyboardType="email-address"
                autoCapitalize="none"
                style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 18, color: colors.text, fontSize: 16, marginBottom: 16 }}
              />
              {error ? <Text style={{ color: colors.red, fontSize: 14, marginBottom: 12, textAlign: "center" }}>{error}</Text> : null}
              <Pressable onPress={sendCode} disabled={loading} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 20, alignItems: "center" }}>
                {loading ? <ActivityIndicator color="#fff" /> :
                  <Text style={{ color: "#fff", fontSize: 16, fontWeight: "800" }}>SEND CODE</Text>}
              </Pressable>
            </>
          ) : (
            <>
              {devCode ? (
                <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 2, borderColor: colors.yellow, padding: 16, marginBottom: 16 }}>
                  <Text style={{ color: colors.yellow, fontSize: 11, fontWeight: "700", letterSpacing: 1.5 }}>DEV MODE CODE</Text>
                  <Text style={{ color: colors.text, fontSize: 24, fontWeight: "800", marginTop: 4 }}>{devCode}</Text>
                  <Text style={{ color: colors.textDim, fontSize: 12, marginTop: 4 }}>
                    Add RESEND_API_KEY to Render to send real emails.
                  </Text>
                </View>
              ) : null}
              <TextInput
                value={code}
                onChangeText={setCode}
                placeholder="Reset code"
                placeholderTextColor={colors.textFaint}
                autoCapitalize="characters"
                style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 18, color: colors.text, fontSize: 16, marginBottom: 12 }}
              />
              <TextInput
                value={newPassword}
                onChangeText={setNewPassword}
                placeholder="New password (min 6)"
                placeholderTextColor={colors.textFaint}
                secureTextEntry
                style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 18, color: colors.text, fontSize: 16, marginBottom: 16 }}
              />
              {error ? <Text style={{ color: colors.red, fontSize: 14, marginBottom: 12, textAlign: "center" }}>{error}</Text> : null}
              <Pressable onPress={doReset} disabled={loading} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 20, alignItems: "center" }}>
                {loading ? <ActivityIndicator color="#fff" /> :
                  <Text style={{ color: "#fff", fontSize: 16, fontWeight: "800" }}>RESET PASSWORD</Text>}
              </Pressable>
            </>
          )}

          <Pressable onPress={() => router.back()} style={{ marginTop: 20, alignItems: "center" }}>
            <Text style={{ color: colors.textDim, fontSize: 14 }}>Back to sign in</Text>
          </Pressable>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
