import { useState } from "react";
import { View, Text, TextInput, Pressable, ScrollView, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import Constants from "expo-constants";
import { useAuth } from "../../lib/store";
import { colors, radius } from "../../constants/theme";

const BASE_URL =
  (Constants.expoConfig?.extra?.apiUrl as string) ||
  "https://coreknow.onrender.com";

export default function SchoolScreen() {
  const user = useAuth((s) => s.user);
  const [schoolName, setSchoolName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [maxStudents, setMaxStudents] = useState("100");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    if (!user) { setError('Sign in first'); return; }
    if (!schoolName || !email) { setError('School name and email required'); return; }
    setLoading(true); setError(null);
    try {
      const r = await fetch(BASE_URL + '/api/school/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          school_name: schoolName,
          contact_email: email,
          contact_phone: phone,
          max_students: parseInt(maxStudents) || 100,
          user_id: user.id,
        }),
      });
      const d = await r.json();
      if (!d.ok) { setError(d.error); setLoading(false); return; }
      setResult(d);
      setLoading(false);
    } catch (e: any) {
      setError(e.message);
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>School License</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        {!result && (
          <>
            <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700" }}>Buy for your school</Text>
            <Text style={{ color: colors.textDim, fontSize: 15, marginTop: 8, marginBottom: 24, lineHeight: 22 }}>
              One license. Up to 500 students. All subjects. One year.
            </Text>
            <Text style={{ color: colors.textFaint, fontSize: 11, fontWeight: "600", letterSpacing: 1.5, marginBottom: 8 }}>SCHOOL NAME</Text>
            <TextInput value={schoolName} onChangeText={setSchoolName} placeholder="e.g. King\'s College Lagos" placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 16, color: colors.text, fontSize: 16, marginBottom: 16 }} />
            <Text style={{ color: colors.textFaint, fontSize: 11, fontWeight: "600", letterSpacing: 1.5, marginBottom: 8 }}>CONTACT EMAIL</Text>
            <TextInput value={email} onChangeText={setEmail} placeholder="admin@school.edu.ng" placeholderTextColor={colors.textFaint} keyboardType="email-address" autoCapitalize="none" style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 16, color: colors.text, fontSize: 16, marginBottom: 16 }} />
            <Text style={{ color: colors.textFaint, fontSize: 11, fontWeight: "600", letterSpacing: 1.5, marginBottom: 8 }}>PHONE (optional)</Text>
            <TextInput value={phone} onChangeText={setPhone} placeholder="+234..." placeholderTextColor={colors.textFaint} keyboardType="phone-pad" style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 16, color: colors.text, fontSize: 16, marginBottom: 16 }} />
            <Text style={{ color: colors.textFaint, fontSize: 11, fontWeight: "600", letterSpacing: 1.5, marginBottom: 8 }}>STUDENT SLOTS</Text>
            <TextInput value={maxStudents} onChangeText={setMaxStudents} keyboardType="number-pad" style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 16, color: colors.text, fontSize: 16, marginBottom: 24 }} />

            {error && <Text style={{ color: colors.red, fontSize: 14, marginBottom: 12, textAlign: "center" }}>{error}</Text>}

            <Pressable onPress={submit} disabled={loading} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 20, alignItems: "center" }}>
              {loading ? <ActivityIndicator color="#fff" /> :
                <Text style={{ color: "#fff", fontSize: 16, fontWeight: "800", letterSpacing: 1 }}>REQUEST INVOICE — N500,000</Text>}
            </Pressable>
          </>
        )}

        {result && (
          <View style={{ alignItems: "center", paddingVertical: 40 }}>
            <Ionicons name="checkmark-circle" size={80} color={colors.green} />
            <Text style={{ color: colors.text, fontSize: 24, fontWeight: "800", marginTop: 20 }}>Request received</Text>
            <Text style={{ color: colors.textDim, fontSize: 15, marginTop: 12, textAlign: "center", lineHeight: 22 }}>
              Our team will contact you at {email} within 24 hours with the invoice.
            </Text>
            <View style={{ backgroundColor: colors.card, borderRadius: radius.md, padding: 20, marginTop: 24, width: "100%" }}>
              <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5 }}>REFERENCE</Text>
              <Text style={{ color: colors.accent, fontSize: 18, fontWeight: "700", marginTop: 4 }}>{result.reference}</Text>
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}