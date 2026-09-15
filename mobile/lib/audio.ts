// Device-side text-to-speech via expo-speech
// No backend cost, works offline

let Speech: any = null;
try {
  Speech = require("expo-speech");
} catch (e) {}

export function speak(text: string) {
  if (!Speech) return;
  try {
    Speech.stop();
    Speech.speak(text, {
      language: "en-NG",
      rate: 0.95,
      pitch: 1.0,
    });
  } catch (e) {}
}

export function stopSpeaking() {
  if (!Speech) return;
  try {
    Speech.stop();
  } catch (e) {}
}