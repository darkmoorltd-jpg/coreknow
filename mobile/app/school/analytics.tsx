import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, ActivityIndicator, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router, useLocalSearchParams } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { school } from "../../lib/school";
import { colors, radius } from "../../constants/theme";

export default function ClassAnalytics() {
  const params = useLocalSearchParams();
  const classId = Number(params.class_id);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    school.analytics(classId).then((d) => {
      if (d.ok) setData(d);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [classId]);

  if (loading) {
    return <View style={{ flex: 1, backgroundColor: colors.bg, justifyContent: "center" }}><ActivityIndicator color={colors.accent} /></View>;
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 22, fontWeight: "700", marginLeft: 16 }}>Class Analytics</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        {data ? (
          <View style={{ flexDirection: "row", gap: 12, marginBottom: 20 }}>
            <View style={{ flex: 1, backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 16 }}>
              <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1 }}>STUDENTS</Text>
              <Text style={{ color: colors.text, fontSize: 28, fontWeight: "800", marginTop: 6 }}>{data.total_students}</Text>
            </View>
            <View style={{ flex: 1, backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 16 }}>
              <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1 }}>ASSIGNMENTS</Text>
              <Text style={{ color: colors.text, fontSize: 28, fontWeight: "800", marginTop: 6 }}>{data.total_assignments}</Text>
            </View>
            <View style={{ flex: 1, backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 16 }}>
              <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1 }}>AVG</Text>
              <Text style={{ color: colors.green, fontSize: 28, fontWeight: "800", marginTop: 6 }}>{data.class_average}</Text>
            </View>
          </View>
        ) : null}

        <Text style={{ color: colors.textFaint, fontSize: 11, letterSpacing: 1.5, marginBottom: 12 }}>STUDENT RANKING</Text>
        {data?.students?.map((s: any, i: number) => (
          <Pressable key={s.user_id} onPress={() => router.push("/school/report/" + classId + "/" + s.user_id)} style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 14, marginBottom: 8, flexDirection: "row", alignItems: "center" }}>
            <Text style={{ color: colors.textFaint, width: 32, fontWeight: "800", fontSize: 14 }}>#{i + 1}</Text>
            <View style={{ flex: 1 }}>
              <Text style={{ color: colors.text, fontSize: 15, fontWeight: "600" }}>{s.name}</Text>
              <Text style={{ color: colors.textFaint, fontSize: 11, marginTop: 2 }}>{s.submitted} submitted · {s.graded} graded</Text>
            </View>
            <View style={{ alignItems: 'flex-end' }}>
              <Text style={{ color: s.avg_score >= 65 ? colors.green : s.avg_score >= 45 ? colors.yellow : colors.red, fontSize: 20, fontWeight: "800" }}>{s.avg_score}</Text>
              <Text style={{ color: colors.textFaint, fontSize: 10 }}>AVG</Text>
            </View>
          </Pressable>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
