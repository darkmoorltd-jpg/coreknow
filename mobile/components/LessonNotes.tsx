import { useState, useEffect } from "react";
import { View, Text, TextInput, Pressable, ActivityIndicator } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../lib/store";
import { api } from "../lib/day1";
import { colors, radius } from "../constants/theme";

export default function LessonNotes({ lessonId }: { lessonId: number }) {
  const user = useAuth((s) => s.user);
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!user?.id) { setLoading(false); return; }
    api.getNote(user.id, lessonId).then((d) => {
      if (d.note) setNote(d.note.content || '');
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [user, lessonId]);

  const save = async () => {
    if (!user?.id) return;
    setSaving(true);
    await api.saveNote(user.id, lessonId, note);
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  if (loading) return <ActivityIndicator color={colors.accent} style={{ marginTop: 20 }} />;

  return (
    <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 1, borderColor: colors.stroke, padding: 20, marginTop: 24 }}>
      <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 12 }}>
        <Ionicons name="create-outline" size={20} color={colors.accent} />
        <Text style={{ color: colors.text, fontSize: 16, fontWeight: "700", marginLeft: 8 }}>My Notes</Text>
      </View>
      <TextInput
        value={note}
        onChangeText={setNote}
        placeholder="Write your notes here..."
        placeholderTextColor={colors.textFaint}
        multiline
        style={{ color: colors.text, fontSize: 15, minHeight: 100, textAlignVertical: "top", borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 12 }}
      />
      <Pressable onPress={save} disabled={saving} style={{ backgroundColor: saved ? colors.green : colors.accent, borderRadius: radius.md, padding: 14, alignItems: "center", marginTop: 12 }}>
        {saving ? <ActivityIndicator color="#fff" /> :
          <Text style={{ color: "#fff", fontWeight: "700" }}>{saved ? "SAVED ✓" : "SAVE NOTE"}</Text>}
      </Pressable>
    </View>
  );
}