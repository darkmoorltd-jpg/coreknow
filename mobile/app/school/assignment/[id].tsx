import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, TextInput, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../../lib/store";
import { school } from "../../../lib/school";
import { colors, radius } from "../../../constants/theme";

export default function AssignmentDetail() {
  const params = useLocalSearchParams();
  const user = useAuth((s) => s.user);
  const assignmentId = Number(params.id);
  const [assignment, setAssignment] = useState<any>(null);
  const [submissions, setSubmissions] = useState<any[]>([]);
  const [myText, setMyText] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const load = async () => {
    const d = await school.assignmentDetail(assignmentId);
    if (d.ok) {
      setAssignment(d.assignment);
      setSubmissions(d.submissions || []);
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, [assignmentId]);

  const submit = async () => {
    if (!myText.trim()) { Alert.alert('Empty', 'Write your answer'); return; }
    setSubmitting(true);
    const d = await school.submitAssignment(assignmentId, user?.id || '', myText);
    setSubmitting(false);
    if (d.ok) {
      Alert.alert('Submitted', 'Score: ' + d.score + '. Feedback: ' + d.feedback);
      setMyText('');
      load();
    } else {
      Alert.alert('Error', d.error || 'Failed');
    }
  };

  if (loading) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}><ActivityIndicator color={colors.accent} /></View>;
  }

  const mySubmission = submissions.find((s) => s.student_id === user?.id);
  const isTeacher = assignment?.teacher_id === user?.id;

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>›</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 20, fontWeight: "700", marginLeft: 16, flex: 1 }} numberOfLines={1}>{assignment?.title || "Assignment"}</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        <Text style={{ color: colors.accentHi, fontSize: 11, letterSpacing: 1.5, marginBottom: 6 }}>{assignment?.subject} · MAX {assignment?.max_score}</Text>
        {assignment?.description ? <Text style={{ color: colors.textDim, fontSize: 14, marginBottom: 20 }}>{assignment.description}</Text> : null}

        {isTeacher ? (
          <>
            <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 12 }}>SUBMISSIONS ({submissions.length})</Text>
            {submissions.length === 0 ? <Text style={{ color: colors.textDim }}>No submissions yet</Text> : null}
            {submissions.map((s) => (
              <View key={s.id} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 14, marginBottom: 10 }}>
                <Text style={{ color: colors.textFaint, fontSize: 11 }}>{s.student_id.slice(0, 12)}...</Text>
                <Text style={{ color: colors.text, fontSize: 14, marginTop: 6 }} numberOfLines={3}>{s.text}</Text>
                {s.score !== null && s.score !== undefined ? (
                  <Text style={{ color: colors.green, fontSize: 14, fontWeight: "800", marginTop: 8 }}>Score: {s.score}/{assignment?.max_score}</Text>
                ) : (
                  <Text style={{ color: colors.yellow, fontSize: 12, marginTop: 8 }}>Not graded</Text>
                )}
              </View>
            ))}
          </>
        ) : (
          <>
            {mySubmission ? (
              <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: colors.green, padding: 16 }}>
                <Text style={{ color: colors.green, fontSize: 11, letterSpacing: 1.5, marginBottom: 8 }}>YOUR SUBMISSION</Text>
                <Text style={{ color: colors.text, fontSize: 14, lineHeight: 22 }}>{mySubmission.text}</Text>
                {mySubmission.score !== null && mySubmission.score !== undefined ? (
                  <Text style={{ color: colors.accentHi, fontSize: 18, fontWeight: "800", marginTop: 12 }}>Score: {mySubmission.score}/{assignment?.max_score}</Text>
                ) : null}
                {mySubmission.feedback ? <Text style={{ color: colors.textDim, fontSize: 13, marginTop: 8, fontStyle: "italic" }}>{mySubmission.feedback}</Text> : null}
              </View>
            ) : (
              <>
                <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 8 }}>YOUR ANSWER</Text>
                <TextInput value={myText} onChangeText={setMyText} multiline placeholder='Type your answer here...' placeholderTextColor={colors.textFaint} style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 14, color: colors.text, minHeight: 200, textAlignVertical: 'top', fontSize: 15, marginBottom: 16 }} />
                <Pressable onPress={submit} disabled={submitting} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 18, alignItems: "center" }}>
                  {submitting ? <ActivityIndicator color="#fff" /> : <Text style={{ color: "#fff", fontWeight: "800", letterSpacing: 1 }}>SUBMIT FOR AI GRADING</Text>}
                </Pressable>
              </>
            )}
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
