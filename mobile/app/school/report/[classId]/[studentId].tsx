import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { school } from "../../lib/school";
import { colors, radius } from "../../constants/theme";

export default function ReportCard() {
  const params = useLocalSearchParams();
  const classId = Number(params.classId);
  const studentId = String(params.studentId);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    school.reportCard(classId, studentId).then((d) => {
      if (d.ok) setData(d);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [classId, studentId]);

  if (loading) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}><ActivityIndicator color={colors.accent} /></View>;
  }

  if (!data) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center", padding: 20 }}><Text style={{ color: colors.red, textAlign: "center" }}>Report not available</Text></View>;
  }

  const gradeColor = data.grade === 'A' ? colors.green : data.grade === 'B' ? colors.accent : data.grade === 'C' ? colors.yellow : colors.red;

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700", marginLeft: 16 }}>Report Card</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 2, borderColor: gradeColor, padding: 24, alignItems: "center", marginBottom: 20 }}>
          <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5 }}>STUDENT</Text>
          <Text style={{ color: colors.text, fontSize: 22, fontWeight: "800", marginTop: 6 }}>{data.student}</Text>
          <View style={{ flexDirection: "row", alignItems: "center", marginTop: 20, gap: 24 }}>
            <View style={{ alignItems: "center" }}>
              <Text style={{ color: colors.textFaint, fontSize: 11 }}>AVERAGE</Text>
              <Text style={{ color: colors.text, fontSize: 32, fontWeight: "800", marginTop: 4 }}>{data.average}</Text>
            </View>
            <View style={{ alignItems: "center" }}>
              <Text style={{ color: colors.textFaint, fontSize: 11 }}>GRADE</Text>
              <Text style={{ color: gradeColor, fontSize: 48, fontWeight: "800", marginTop: 2 }}>{data.grade}</Text>
            </View>
          </View>
        </View>
        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 12 }}>ASSIGNMENT BREAKDOWN</Text>
        {data.assignments?.map((a: any, i: number) => (
          <View key={i} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 14, marginBottom: 8 }}>
            <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
              <Text style={{ color: colors.text, fontSize: 14, fontWeight: "600", flex: 1 }} numberOfLines={2}>{a.assignment}</Text>
              <Text style={{ color: a.score !== null && a.score !== undefined ? (a.score / a.max_score >= 0.65 ? colors.green : a.score / a.max_score >= 0.45 ? colors.yellow : colors.red) : colors.textFaint, fontSize: 14, fontWeight: "800", marginLeft: 8 }}>
                {a.score !== null && a.score !== undefined ? a.score + '/' + a.max_score : '—'}
              </Text>
            </View>
            {a.feedback ? <Text style={{ color: colors.textDim, fontSize: 12, marginTop: 6, fontStyle: "italic" }}>{a.feedback}</Text> : null}
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
