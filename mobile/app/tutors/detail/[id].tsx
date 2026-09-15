import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, TextInput, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../../lib/store";
import { tutors } from "../../../lib/tutors";
import { colors, radius } from "../../../constants/theme";

export default function TutorDetail() {
  const params = useLocalSearchParams();
  const user = useAuth((s) => s.user);
  const tutorId = Number(params.id);
  const [tutor, setTutor] = useState<any>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [topic, setTopic] = useState("");
  const [when, setWhen] = useState("");
  const [booking, setBooking] = useState(false);

  useEffect(() => {
    tutors.detail(tutorId).then((d) => {
      if (d.ok) {
        setTutor(d.tutor);
        setReviews(d.reviews || []);
      }
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [tutorId]);

  const book = async () => {
    if (!when.trim()) { Alert.alert('Missing', 'Enter date/time (YYYY-MM-DDTHH:00:00Z)'); return; }
    setBooking(true);
    const d = await tutors.book({
      tutor_id: tutorId,
      student_id: user?.id,
      subject: (tutor?.subjects || [])[0] || 'Chemistry',
      topic,
      scheduled_at: when.trim(),
      duration_minutes: 60,
    });
    setBooking(false);
    if (d.ok) {
      Alert.alert('Booked', 'Amount: N' + d.amount + '. You will be redirected to Paystack.');
      router.push('/tutors/my-bookings');
    } else Alert.alert('Error', d.error || 'Failed');
  };

  if (loading) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}><ActivityIndicator color={colors.accent} /></View>;
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 20, fontWeight: "700", marginLeft: 16 }}>Tutor</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        <View style={{ alignItems: "center", marginBottom: 20 }}>
          <View style={{ width: 96, height: 96, borderRadius: 48, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center" }}>
            <Text style={{ color: "#fff", fontSize: 40, fontWeight: "800" }}>{tutor?.full_name?.[0] || "T"}</Text>
          </View>
          <Text style={{ color: colors.text, fontSize: 24, fontWeight: "800", marginTop: 12 }}>{tutor?.full_name}</Text>
          <Text style={{ color: colors.textDim, fontSize: 14, marginTop: 4 }}>{tutor?.qualification}</Text>
          <View style={{ flexDirection: "row", alignItems: "center", marginTop: 8, gap: 12 }}>
            <Text style={{ color: colors.yellow, fontSize: 14, fontWeight: "700" }}>★ {tutor?.avg_rating || "—"}</Text>
            <Text style={{ color: colors.textFaint, fontSize: 13 }}>{tutor?.total_sessions || 0} sessions</Text>
          </View>
        </View>

        <View style={{ backgroundColor: colors.card, borderRadius: radius.md, padding: 16, marginBottom: 16 }}>
          <Text style={{ color: colors.accentHi, fontSize: 11, letterSpacing: 1.5, marginBottom: 6 }}>ABOUT</Text>
          <Text style={{ color: colors.text, fontSize: 14, lineHeight: 22 }}>{tutor?.bio || "No bio"}</Text>
        </View>

        <View style={{ backgroundColor: colors.card, borderRadius: radius.md, padding: 16, marginBottom: 16 }}>
          <Text style={{ color: colors.accentHi, fontSize: 11, letterSpacing: 1.5, marginBottom: 8 }}>SUBJECTS</Text>
          <Text style={{ color: colors.text, fontSize: 14 }}>{(tutor?.subjects || []).join(" · ") || "—"}</Text>
        </View>

        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 8 }}>BOOK A SESSION</Text>
        <TextInput value={topic} onChangeText={setTopic} placeholder='What topic?' placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.card, borderRadius: radius.md, padding: 14, color: colors.text, borderWidth: 1, borderColor: colors.stroke, marginBottom: 10 }} />
        <TextInput value={when} onChangeText={setWhen} placeholder='2026-09-20T15:00:00Z' placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.card, borderRadius: radius.md, padding: 14, color: colors.text, borderWidth: 1, borderColor: colors.stroke, marginBottom: 12 }} />
        <Pressable onPress={book} disabled={booking} style={{ backgroundColor: colors.green, borderRadius: radius.md, padding: 18, alignItems: "center", marginBottom: 24 }}>
          {booking ? <ActivityIndicator color="#000" /> : <Text style={{ color: "#000", fontWeight: "800", letterSpacing: 1 }}>BOOK · N{tutor?.rate_per_hour}</Text>}
        </Pressable>

        {reviews.length > 0 ? <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 12 }}>REVIEWS ({reviews.length})</Text> : null}
        {reviews.map((r) => (
          <View key={r.id} style={{ backgroundColor: colors.card, borderRadius: radius.md, padding: 14, marginBottom: 8 }}>
            <Text style={{ color: colors.yellow, fontSize: 13, fontWeight: "700" }}>{"★".repeat(r.rating)}{"☆".repeat(5 - r.rating)}</Text>
            {r.comment ? <Text style={{ color: colors.text, fontSize: 14, marginTop: 6 }}>{r.comment}</Text> : null}
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
