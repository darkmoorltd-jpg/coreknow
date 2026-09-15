import { useState } from "react";
import { View, Text, TextInput, Pressable, ScrollView, ActivityIndicator, StatusBar, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { useAuth } from "../../lib/store";
import { tutors } from "../../lib/tutors";
import { colors, radius } from "../../constants/theme";

export default function BecomeTutor() {
  const user = useAuth((s) => s.user);
  const [name, setName] = useState("");
  const [bio, setBio] = useState("");
  const [subjects, setSubjects] = useState("Chemistry, Mathematics");
  const [rate, setRate] = useState("2000");
  const [years, setYears] = useState("0");
  const [qual, setQual] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!name.trim()) { Alert.alert('Missing', 'Enter your name'); return; }
    setLoading(true);
    const d = await tutors.apply({
      user_id: user?.id,
      full_name: name.trim(),
      bio: bio.trim(),
      subjects: subjects.split(',').map((s) => s.trim()).filter((s) => s),
      rate_per_hour: parseInt(rate) || 2000,
      years_experience: parseInt(years) || 0,
      qualification: qual.trim(),
    });
    setLoading(false);
    if (d.ok) {
      Alert.alert('Submitted', 'We will review your application within 24 hours.');
      router.back();
    } else Alert.alert('Error', d.error || 'Failed');
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700", marginLeft: 16 }}>Become a Tutor</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        <Text style={{ color: colors.textDim, fontSize: 14, lineHeight: 21, marginBottom: 20 }}>
          Earn N1,500–5,000 per session. We handle payments, scheduling, and video rooms. You focus on teaching.
        </Text>
        {[
          {label: 'Full name', value: name, set: setName},
          {label: 'Qualification (e.g. BSc Chemistry)', value: qual, set: setQual},
          {label: 'Subjects (comma-separated)', value: subjects, set: setSubjects},
          {label: 'Rate per hour (N)', value: rate, set: setRate},
          {label: 'Years of experience', value: years, set: setYears},
        ].map((f, i) => (
          <View key={i} style={{ marginBottom: 12 }}>
            <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 6 }}>{f.label.toUpperCase()}</Text>
            <TextInput value={f.value} onChangeText={f.set} placeholder={f.label} placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.card, borderRadius: radius.md, padding: 14, color: colors.text, borderWidth: 1, borderColor: colors.stroke }} />
          </View>
        ))}
        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 6 }}>BIO</Text>
        <TextInput value={bio} onChangeText={setBio} multiline placeholder='Short bio (2-3 sentences)' placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.card, borderRadius: radius.md, padding: 14, color: colors.text, borderWidth: 1, borderColor: colors.stroke, minHeight: 100, textAlignVertical: 'top', marginBottom: 20 }} />
        <Pressable onPress={submit} disabled={loading} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 18, alignItems: "center" }}>
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={{ color: "#fff", fontWeight: "800", letterSpacing: 1 }}>SUBMIT APPLICATION</Text>}
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}
