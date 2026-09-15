import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, TextInput, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../lib/store";
import { school } from "../../lib/school";
import { colors, radius } from "../../constants/theme";

export default function ExamSchedule() {
  const params = useLocalSearchParams();
  const user = useAuth((s) => s.user);
  const classId = Number(params.class_id);
  const [exams, setExams] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [subject, setSubject] = useState("Chemistry");
  const [date, setDate] = useState("");
  const [creating, setCreating] = useState(false);

  const load = async () => {
    const d = await school.listExams(classId);
    if (d.ok) setExams(d.exams || []);
    setLoading(false);
  };

  useEffect(() => { load(); }, [classId]);

  const create = async () => {
    if (!title.trim() || !date.trim()) {
      Alert.alert('Missing', 'Title and date required (YYYY-MM-DD)');
      return;
    }
    setCreating(true);
    const d = await school.scheduleExam({
      school_license_id: 0,
      class_id: classId,
      created_by: user?.id,
      title: title.trim(),
      subject,
      exam_date: date.trim() + 'T09:00:00Z',
      duration_minutes: 60,
      total_questions: 40,
    });
    setCreating(false);
    if (d.ok) {
      setTitle('');
      setDate('');
      load();
    } else Alert.alert('Error', d.error || 'Failed');
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700", marginLeft: 16 }}>Exam Schedule</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 2, borderColor: colors.cyan, padding: 14, marginBottom: 20 }}>
          <Text style={{ color: colors.cyan, fontSize: 11, letterSpacing: 1.5, marginBottom: 8 }}>SCHEDULE NEW EXAM</Text>
          <TextInput value={title} onChangeText={setTitle} placeholder='Title (e.g. Mid-term Chemistry)' placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.bg2, borderRadius: radius.sm, padding: 12, color: colors.text, marginBottom: 8 }} />
          <TextInput value={subject} onChangeText={setSubject} placeholder='Subject' placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.bg2, borderRadius: radius.sm, padding: 12, color: colors.text, marginBottom: 8 }} />
          <TextInput value={date} onChangeText={setDate} placeholder='Date YYYY-MM-DD' placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.bg2, borderRadius: radius.sm, padding: 12, color: colors.text, marginBottom: 12 }} />
          <Pressable onPress={create} disabled={creating} style={{ backgroundColor: colors.cyan, borderRadius: radius.md, padding: 14, alignItems: "center" }}>
            {creating ? <ActivityIndicator color="#000" /> : <Text style={{ color: "#000", fontWeight: "800", letterSpacing: 1 }}>SCHEDULE</Text>}
          </Pressable>
        </View>

        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 12 }}>UPCOMING</Text>
        {loading ? <ActivityIndicator color={colors.accent} /> : null}
        {!loading && exams.length === 0 ? (
          <Text style={{ color: colors.textDim, textAlign: "center", marginTop: 20 }}>No exams scheduled</Text>
        ) : null}
        {exams.map((e) => (
          <View key={e.id} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: colors.cyan, padding: 14, marginBottom: 10 }}>
            <Text style={{ color: colors.cyan, fontSize: 11, letterSpacing: 1 }}>{e.subject}</Text>
            <Text style={{ color: colors.text, fontSize: 16, fontWeight: "700", marginTop: 4 }}>{e.title}</Text>
            <Text style={{ color: colors.textDim, fontSize: 12, marginTop: 4 }}>{e.exam_date?.slice(0, 10)} · {e.duration_minutes} min · {e.total_questions} questions</Text>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
