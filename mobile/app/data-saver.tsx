import { useState, useEffect } from "react";
import { View, Text, ScrollView, Pressable, Switch, StatusBar } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { colors, radius } from "../constants/theme";

export default function DataSaver() {
  const [saver, setSaver] = useState(false);
  const [autoWifi, setAutoWifi] = useState(true);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    (async () => {
      const s = await AsyncStorage.getItem('@ck_data_saver');
      const w = await AsyncStorage.getItem('@ck_auto_wifi');
      setSaver(s === 'true');
      setAutoWifi(w !== 'false');
      setLoaded(true);
    })();
  }, []);

  const save = async (s: boolean, w: boolean) => {
    await AsyncStorage.setItem('@ck_data_saver', String(s));
    await AsyncStorage.setItem('@ck_auto_wifi', String(w));
  };

  if (!loaded) return null;

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => router.back()}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Data & Storage</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20 }}>
        <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 18, marginBottom: 12, flexDirection: "row", alignItems: "center" }}>
          <Ionicons name="cellular" size={22} color={colors.accent} />
          <View style={{ flex: 1, marginLeft: 14 }}>
            <Text style={{ color: colors.text, fontSize: 16, fontWeight: "600" }}>Data-saver mode</Text>
            <Text style={{ color: colors.textFaint, fontSize: 12, marginTop: 2 }}>Skip videos, load text only</Text>
          </View>
          <Switch
            value={saver}
            onValueChange={(v) => { setSaver(v); save(v, autoWifi); }}
            trackColor={{ false: colors.stroke, true: colors.accent }}
            thumbColor='#fff'
          />
        </View>

        <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 18, marginBottom: 24, flexDirection: "row", alignItems: "center" }}>
          <Ionicons name="wifi" size={22} color={colors.green} />
          <View style={{ flex: 1, marginLeft: 14 }}>
            <Text style={{ color: colors.text, fontSize: 16, fontWeight: "600" }}>Auto-download on Wi-Fi</Text>
            <Text style={{ color: colors.textFaint, fontSize: 12, marginTop: 2 }}>Sync when connected to Wi-Fi only</Text>
          </View>
          <Switch
            value={autoWifi}
            onValueChange={(v) => { setAutoWifi(v); save(saver, v); }}
            trackColor={{ false: colors.stroke, true: colors.green }}
            thumbColor='#fff'
          />
        </View>

        <View style={{ backgroundColor: colors.bg2, borderRadius: radius.md, padding: 18 }}>
          <Text style={{ color: colors.textDim, fontSize: 13, lineHeight: 20 }}>
            Data-saver skips video downloads when saving lessons offline. Text, questions, and diagrams are always included.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}