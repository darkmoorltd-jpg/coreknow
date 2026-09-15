import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../../constants/theme";

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: colors.accent,
        tabBarInactiveTintColor: colors.textFaint,
        tabBarStyle: {
          backgroundColor: colors.card,
          borderTopColor: colors.stroke,
          borderTopWidth: 1,
          height: 72,
          paddingBottom: 10,
          paddingTop: 8,
        },
        tabBarLabelStyle: { fontSize: 11, fontWeight: '600' },
        headerStyle: { backgroundColor: colors.bg },
        headerTintColor: colors.text,
        headerShown: false,
      }}
    >
      <Tabs.Screen name="index" options={{ title: "Home", tabBarIcon: ({ color, size }) => <Ionicons name="home" size={size} color={color} /> }} />
      <Tabs.Screen name="subjects" options={{ title: "Learn", tabBarIcon: ({ color, size }) => <Ionicons name="book" size={size} color={color} /> }} />
      <Tabs.Screen name="chat" options={{ title: "Chat", tabBarIcon: ({ color, size }) => <Ionicons name="chatbubble" size={size} color={color} /> }} />
      <Tabs.Screen name="profile" options={{ title: "Me", tabBarIcon: ({ color, size }) => <Ionicons name="person" size={size} color={color} /> }} />
    </Tabs>
  );
}