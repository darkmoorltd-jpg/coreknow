import { View, Text, ScrollView, Pressable, StatusBar, ActivityIndicator, RefreshControl } from "react-native";
import { useState, useEffect, useCallback } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { useAuth } from "../../lib/store";
import { getPaymentHistory, Payment } from "../../lib/payments";
import { colors, radius, font } from "../../constants/theme";

const STATUS_COLOR: Record<string, string> = {
  paid: colors.green,
  pending: colors.yellow,
  failed: colors.red,
};

const STATUS_ICON: Record<string, string> = {
  paid: "checkmark-circle",
  pending: "time",
  failed: "close-circle",
};

export default function PaymentsScreen() {
  const user = useAuth((s) => s.user);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    if (!user?.id) {
      setLoading(false);
      return;
    }
    const p = await getPaymentHistory(user.id);
    setPayments(p);
    setLoading(false);
  }, [user]);

  useEffect(() => {
    load();
  }, [load]);

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const paidOnly = payments.filter((p) => p.status === 'paid');
  const totalSpent = paidOnly.reduce((sum, p) => sum + p.amount, 0);

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <StatusBar barStyle="light-content" />

      <View style={{ flexDirection: "row", alignItems: "center", padding: 20, paddingBottom: 8 }}>
        <Pressable onPress={() => router.back()}>
          <Text style={{ color: colors.text, fontSize: 32 }}>‹</Text>
        </Pressable>
        <Text style={{ color: colors.text, fontSize: 24, fontWeight: "700", marginLeft: 16 }}>
          Payment History
        </Text>
      </View>

      <ScrollView
        contentContainerStyle={{ padding: 20, paddingBottom: 60 }}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor={colors.accent}
          />
        }
      >
        {/* Summary card */}
        <View style={{ backgroundColor: colors.card, borderRadius: radius.lg, borderWidth: 2, borderColor: colors.strokeHi, padding: 24, marginBottom: 24 }}>
          <View style={{ position: "absolute", left: 0, top: 24, bottom: 24, width: 4, backgroundColor: colors.accent, borderTopRightRadius: 4, borderBottomRightRadius: 4 }} />
          <Text style={{ color: colors.accentHi, fontSize: 11, fontWeight: "600", letterSpacing: 1.5 }}>
            TOTAL SPENT
          </Text>
          <Text style={{ color: colors.text, fontSize: 40, fontWeight: "800", marginTop: 8 }}>
            N{totalSpent.toLocaleString()}
          </Text>
          <Text style={{ color: colors.textDim, fontSize: 14, marginTop: 4 }}>
            {paidOnly.length} successful payments
          </Text>
        </View>

        {loading && (
          <ActivityIndicator color={colors.accent} size="large" style={{ marginTop: 40 }} />
        )}

        {!loading && payments.length === 0 && (
          <View style={{ alignItems: "center", paddingVertical: 60 }}>
            <Ionicons name="receipt-outline" size={64} color={colors.textFaint} />
            <Text style={{ color: colors.textDim, fontSize: 16, marginTop: 16 }}>
              No payments yet
            </Text>
            <Text style={{ color: colors.textFaint, fontSize: 13, marginTop: 6, textAlign: "center", paddingHorizontal: 40 }}>
              Your payment history will appear here after you subscribe.
            </Text>
          </View>
        )}

        {payments.map((p) => (
          <View
            key={p.id}
            style={{
              backgroundColor: colors.card,
              borderRadius: radius.md,
              borderWidth: 1,
              borderColor: colors.stroke,
              padding: 18,
              marginBottom: 12,
              flexDirection: "row",
              alignItems: "center",
            }}
          >
            <View
              style={{
                width: 48,
                height: 48,
                borderRadius: 24,
                backgroundColor: STATUS_COLOR[p.status] + '22',
                justifyContent: "center",
                alignItems: "center",
              }}
            >
              <Ionicons
                name={STATUS_ICON[p.status] as any}
                size={24}
                color={STATUS_COLOR[p.status]}
              />
            </View>
            <View style={{ flex: 1, marginLeft: 14 }}>
              <Text style={{ color: colors.text, fontSize: 16, fontWeight: "700" }}>
                {p.plan.charAt(0).toUpperCase() + p.plan.slice(1)} plan
              </Text>
              <Text style={{ color: colors.textFaint, fontSize: 12, marginTop: 2 }}>
                {new Date(p.created_at).toLocaleDateString("en-NG")}
                {'  ·  '}
                {p.reference || '—'}
              </Text>
            </View>
            <View style={{ alignItems: "flex-end" }}>
              <Text style={{ color: colors.text, fontSize: 17, fontWeight: "800" }}>
                N{p.amount.toLocaleString()}
              </Text>
              <Text
                style={{
                  color: STATUS_COLOR[p.status],
                  fontSize: 11,
                  fontWeight: "700",
                  marginTop: 4,
                  letterSpacing: 1,
                  textTransform: "uppercase",
                }}
              >
                {p.status}
              </Text>
            </View>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}