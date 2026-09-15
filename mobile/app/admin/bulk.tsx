import { useState } from "react";
import { View, Text, TextInput, Pressable, ScrollView, ActivityIndicator, StatusBar, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { useAuth } from "../../lib/store";
import { admin } from "../../lib/admin";
import { colors, radius } from "../../constants/theme";

export default function BulkImport() {
  const user = useAuth((s) => s.user);
  const [subject, setSubject] = useState("Chemistry");
  const [startTopic, setStartTopic] = useState("7");
  const [raw, setRaw] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const parseItems = () => {
    const parts = raw.split(/^##\s+/m).filter((p) => p.trim());
    return parts.map((p) => {
      const lines = p.split('\n');
      const title = lines[0].trim();
      const body = lines.slice(1).join('\n').trim();
      return { title, text: body };
    });
  };

  const run = async () => {
    const items = parseItems();
    if (items.length === 0) {
      Alert.alert('Nothing to import', 'Paste markdown with ## Title lines');
      return;
    }
    setLoading(true);
    const d = await admin.bulkImport({
      admin_id: user?.id,
      exam: 'JAMB',
      subject,
      start_topic: parseInt(startTopic) || 7,
      items,
    });
    setLoading(false);
    setResult(d);
  };

  const previewCount = raw ? parseItems().length : 0;

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700", marginLeft: 16 }}>Bulk Import</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 80 }}>
        <Text style={{ color: colors.textDim, fontSize: 13, lineHeight: 20, marginBottom: 16 }}>
          Paste multiple lessons. Each lesson starts with ## Title, followed by the lesson body. The importer assigns topic numbers sequentially starting from the value below.
        </Text>
        <View style={{ flexDirection: "row", gap: 12, marginBottom: 12 }}>
          <View style={{ flex: 2 }}>
            <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 6 }}>SUBJECT</Text>
            <TextInput value={subject} onChangeText={setSubject} style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 12, color: colors.text }} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 6 }}>START #</Text>
            <TextInput value={startTopic} onChangeText={setStartTopic} keyboardType='number-pad' style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 12, color: colors.text }} />
          </View>
        </View>
        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 6 }}>MARKDOWN</Text>
        <TextInput
          value={raw}
          onChangeText={setRaw}
          multiline
          placeholder={'## Solubility\n\nSolubility is...\n\n## Environmental Pollution\n\n...'}
          placeholderTextColor={colors.textFaint}
          style={{ backgroundColor: colors.card, borderWidth: 1, borderColor: colors.stroke, borderRadius: radius.md, padding: 14, color: colors.text, minHeight: 260, textAlignVertical: 'top', fontFamily: 'monospace', fontSize: 12, marginBottom: 16 }}
        />

        <View style={{ backgroundColor: colors.bg2, borderRadius: radius.md, padding: 12, marginBottom: 16, flexDirection: "row", justifyContent: "space-between" }}>
          <Text style={{ color: colors.textDim, fontSize: 13 }}>Detected lessons</Text>
          <Text style={{ color: colors.accent, fontSize: 13, fontWeight: "800" }}>{previewCount}</Text>
        </View>

        <Pressable onPress={run} disabled={loading || previewCount === 0} style={{ backgroundColor: colors.violet, borderRadius: radius.md, padding: 20, alignItems: "center", marginBottom: 16, opacity: previewCount === 0 ? 0.5 : 1 }}>
          {loading ? <ActivityIndicator color="#fff" /> :
            <Text style={{ color: "#fff", fontSize: 16, fontWeight: "800", letterSpacing: 1 }}>IMPORT {previewCount} LESSONS</Text>}
        </Pressable>

        {result ? (
          <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderLeftWidth: 4, borderLeftColor: result.ok ? colors.green : colors.red, padding: 16 }}>
            <Text style={{ color: result.ok ? colors.green : colors.red, fontSize: 14, fontWeight: "700" }}>
              {result.ok ? 'Imported ' + result.created + ' lessons' : 'Failed: ' + result.error}
            </Text>
          </View>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}
