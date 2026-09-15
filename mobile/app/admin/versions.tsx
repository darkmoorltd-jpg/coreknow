import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../lib/store";
import { admin } from "../../lib/admin";
import { colors, radius } from "../../constants/theme";

export default function Versions() {
  const params = useLocalSearchParams();
  const user = useAuth((s) => s.user);
  const lessonId = Number(params.lesson_id || 0);
  const [versions, setVersions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    if (!user?.id) return;
    const d = await admin.versions(lessonId, user.id);
    if (d.ok) setVersions(d.versions || []);
    setLoading(false);
  };

  useEffect(() => { load(); }, [user, lessonId]);

  const rollback = (version: number) => {
    Alert.alert('Rollback', 'Restore version ' + version + '?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Restore', style: 'destructive', onPress: async () => {
        const d = await admin.rollback(lessonId, user?.id || '', version);
        if (d.ok) { Alert.alert('Restored', 'Version ' + version + ' is now live'); router.back(); }
        else Alert.alert('Error', d.error || 'Rollback failed');
      }},
    ]);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700", marginLeft: 16 }}>Version History</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        {loading && <ActivityIndicator color={colors.accent} />}
        {!loading && versions.length === 0 && (
          <View style={{ alignItems: "center", paddingVertical: 60 }}>
            <Ionicons name="time-outline" size={56} color={colors.textFaint} />
            <Text style={{ color: colors.textDim, marginTop: 16 }}>No version history yet</Text>
            <Text style={{ color: colors.textFaint, fontSize: 13, marginTop: 6, textAlign: "center", paddingHorizontal: 40 }}>Versions are saved automatically when you edit a lesson.</Text>
          </View>
        )}
        {versions.map((v) => (
          <View key={v.id} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 16, marginBottom: 10 }}>
            <View style={{ flexDirection: "row", alignItems: "center" }}>
              <View style={{ width: 44, height: 44, borderRadius: 22, backgroundColor: colors.accent, justifyContent: "center", alignItems: "center" }}>
                <Text style={{ color: "#fff", fontWeight: "800" }}>v{v.version}</Text>
              </View>
              <View style={{ flex: 1, marginLeft: 12 }}>
                <Text style={{ color: colors.text, fontSize: 14, fontWeight: "600" }} numberOfLines={1}>{v.topic_title}</Text>
                <Text style={{ color: colors.textFaint, fontSize: 11, marginTop: 4 }}>{v.created_at?.slice(0, 16)}</Text>
              </View>
              <Pressable onPress={() => rollback(v.version)} style={{ backgroundColor: colors.yellow, paddingHorizontal: 14, paddingVertical: 8, borderRadius: 999 }}>
                <Text style={{ color: "#000", fontWeight: "800", fontSize: 12 }}>RESTORE</Text>
              </Pressable>
            </View>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
