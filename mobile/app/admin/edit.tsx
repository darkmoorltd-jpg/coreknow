import { useState, useEffect } from "react";
import { View, Text, TextInput, Pressable, ScrollView, ActivityIndicator, StatusBar, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../lib/store";
import { admin } from "../../lib/admin";
import Constants from "expo-constants";
import { colors, radius } from "../../constants/theme";

const BASE = (Constants.expoConfig?.extra?.apiUrl as string) || 'https://coreknow.onrender.com';

export default function EditLesson() {
  const params = useLocalSearchParams();
  const user = useAuth((s) => s.user);
  const lessonId = Number(params.lesson_id || 0);
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [status, setStatus] = useState("published");
  const [topicNumber, setTopicNumber] = useState("0");
  const [subject, setSubject] = useState("Chemistry");
  const [exam, setExam] = useState("JAMB");
  const [loading, setLoading] = useState(lessonId > 0);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!lessonId) return;
    fetch(BASE + '/api/lessons/' + lessonId)
      .then((r) => r.json())
      .then((d) => {
        if (d.lesson) {
          setTitle(d.lesson.topic_title || '');
          setText(d.lesson.lesson_text || '');
          setStatus(d.lesson.status || 'published');
        }
        if (d.syllabus) {
          setTopicNumber(String(d.syllabus.topic_number || 0));
          setSubject(d.syllabus.subject || 'Chemistry');
          setExam(d.syllabus.exam || 'JAMB');
        }
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [lessonId]);

  const save = async () => {
    if (!title.trim() || !text.trim()) {
      Alert.alert('Missing', 'Title and content are required');
      return;
    }
    setSaving(true);
    const d = await admin.saveLesson({
      admin_id: user?.id,
      lesson_id: lessonId,
      exam,
      subject,
      topic_number: parseInt(topicNumber) || 0,
      topic_title: title.trim(),
      lesson_text: text,
      status,
    });
    setSaving(false);
    if (d.ok) {
      Alert.alert('Saved', 'Version ' + d.version + ' published');
      router.back();
    } else {
      Alert.alert('Error', d.error || 'Save failed');
    }
  };

  if (loading) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}><ActivityIndicator color={colors.accent} /></View>;
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700", marginLeft: 16, flex: 1 }}>{lessonId ? "Edit Lesson" : "New Lesson"}</Text>
        {lessonId > 0 ? (
          <Pressable onPress={() => router.push("/admin/versions?lesson_id=" + lessonId)}>
            <Ionicons name="time-outline" size={22} color={colors.accent} />
          </Pressable>
        ) : null}
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 80 }}>
        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 6 }}>EXAM</Text>
        <TextInput value={exam} onChangeText={setExam} style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 12, color: colors.text, marginBottom: 12 }} />
        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 6 }}>SUBJECT</Text>
        <TextInput value={subject} onChangeText={setSubject} style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 12, color: colors.text, marginBottom: 12 }} />
        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 6 }}>TOPIC NUMBER</Text>
        <TextInput value={topicNumber} onChangeText={setTopicNumber} keyboardType='number-pad' style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 12, color: colors.text, marginBottom: 12 }} />
        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 6 }}>TITLE</Text>
        <TextInput value={title} onChangeText={setTitle} style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 12, color: colors.text, marginBottom: 12 }} />
        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 6 }}>LESSON TEXT (markdown)</Text>
        <TextInput
          value={text}
          onChangeText={setText}
          multiline
          style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 14, color: colors.text, minHeight: 320, textAlignVertical: 'top', fontFamily: 'monospace', fontSize: 13, marginBottom: 16 }}
        />

        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 8 }}>STATUS</Text>
        <View style={{ flexDirection: "row", gap: 8, marginBottom: 20 }}>
          {['published','draft','scheduled'].map((s) => (
            <Pressable key={s} onPress={() => setStatus(s)} style={{ flex: 1, padding: 12, borderRadius: radius.md, backgroundColor: status === s ? colors.accent : colors.card, borderWidth: 1, borderColor: status === s ? colors.accent : colors.stroke, alignItems: 'center' }}>
              <Text style={{ color: status === s ? "#fff" : colors.text, fontWeight: "700", fontSize: 13 }}>{s}</Text>
            </Pressable>
          ))}
        </View>

        <Pressable onPress={save} disabled={saving} style={{ backgroundColor: colors.green, borderRadius: radius.md, padding: 20, alignItems: "center" }}>
          {saving ? <ActivityIndicator color="#000" /> :
            <Text style={{ color: "#000", fontSize: 16, fontWeight: "800", letterSpacing: 1 }}>SAVE</Text>}
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}
