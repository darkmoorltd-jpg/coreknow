import { useState, useRef } from "react";
import { View, Text, Pressable, ScrollView, ActivityIndicator, StatusBar, Animated } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../lib/store";
import { day6 } from "../lib/day6";
import { speak, stopSpeaking } from "../lib/audio";
import { colors, radius } from "../constants/theme";

let SpeechRecognition: any = null;
try {
  SpeechRecognition = require("expo-speech-recognition").ExpoSpeechRecognitionModule;
} catch (e) {}

export default function VoiceScreen() {
  const user = useAuth((s) => s.user);
  const [transcript, setTranscript] = useState("");
  const [answer, setAnswer] = useState("");
  const [recording, setRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const start = async () => {
    if (!SpeechRecognition) { setError('Speech not available on this device'); return; }
    try {
      const perm = await SpeechRecognition.requestPermissionsAsync();
      if (perm.status !== 'granted') { setError('Mic permission denied'); return; }
      setError(null);
      setTranscript('');
      setAnswer('');
      setRecording(true);
      SpeechRecognition.start({ lang: 'en-NG', interimResults: true });
      SpeechRecognition.addListener('result', (e: any) => {
        setTranscript(e.results[0]?.transcript || '');
      });
      SpeechRecognition.addListener('end', () => {
        setRecording(false);
      });
    } catch (e: any) {
      setRecording(false);
      setError(e.message);
    }
  };

  const stop = async () => {
    if (SpeechRecognition) SpeechRecognition.stop();
    setRecording(false);
  };

  const ask = async () => {
    if (!transcript.trim()) { setError('Nothing to ask'); return; }
    setLoading(true); setError(null);
    const d = await day6.voiceAsk(user?.id || '', transcript, 'en', 0);
    setLoading(false);
    if (!d.ok) { setError(d.error); return; }
    setAnswer(d.answer);
    speak(d.answer.slice(0, 400));
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />
      <View style={{ flexDirection: "row", alignItems: "center", padding: 20 }}>
        <Pressable onPress={() => { stopSpeaking(); router.back(); }}><Text style={{ color: colors.text, fontSize: 32 }}>‹</Text></Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>Voice Tutor</Text>
      </View>
      <ScrollView contentContainerStyle={{ padding: 20, paddingBottom: 60 }}>
        <View style={{ alignItems: "center", marginBottom: 32 }}>
          <Pressable
            onPress={recording ? stop : start}
            style={{
              width: 160,
              height: 160,
              borderRadius: 80,
              backgroundColor: recording ? colors.red : colors.accent,
              justifyContent: 'center',
              alignItems: 'center',
              shadowColor: recording ? colors.red : colors.accent,
              shadowOpacity: 0.6,
              shadowRadius: 30,
              elevation: 20,
            }}
          >
            <Ionicons name={recording ? "stop" : "mic"} size={64} color="#fff" />
          </Pressable>
          <Text style={{ color: colors.textDim, fontSize: 14, marginTop: 20 }}>
            {recording ? 'Listening... tap to stop' : 'Tap to speak'}
          </Text>
        </View>

        {transcript ? (
          <View style={{ backgroundColor: colors.card, borderRadius: radius.md, borderWidth: 1, borderColor: colors.stroke, padding: 18, marginBottom: 16 }}>
            <Text style={{ color: colors.accentHi, fontSize: 11, fontWeight: "600", letterSpacing: 1.5, marginBottom: 6 }}>YOU SAID</Text>
            <Text style={{ color: colors.text, fontSize: 16, lineHeight: 24 }}>{transcript}</Text>
          </View>
        ) : null}

        {transcript && !answer ? (
          <Pressable onPress={ask} disabled={loading} style={{ backgroundColor: colors.accent, borderRadius: radius.md, padding: 20, alignItems: "center", marginBottom: 16 }}>
            {loading ? <ActivityIndicator color="#fff" /> :
              <Text style={{ color: "#fff", fontSize: 16, fontWeight: "800", letterSpacing: 1 }}>ASK COR EKNOW</Text>}
          </Pressable>
        ) : null}

        {error ? (
          <Text style={{ color: colors.red, fontSize: 14, textAlign: "center", marginBottom: 16 }}>{error}</Text>
        ) : null}

        {answer ? (
          <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderLeftWidth: 4, borderLeftColor: colors.green, padding: 20 }}>
            <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 10 }}>
              <Text style={{ color: colors.green, fontSize: 12, fontWeight: "700", letterSpacing: 1 }}>ANSWER</Text>
              <Pressable onPress={() => speak(answer.slice(0, 400))}>
                <Ionicons name="volume-high" size={20} color={colors.green} />
              </Pressable>
            </View>
            <Text style={{ color: colors.text, fontSize: 15, lineHeight: 24 }}>{answer}</Text>
          </View>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}