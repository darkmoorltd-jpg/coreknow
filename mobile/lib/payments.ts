import Constants from "expo-constants";

const BASE_URL =
  (Constants.expoConfig?.extra?.apiUrl as string) ||
  "https://coreknow.onrender.com";

export type Payment = {
  id: number;
  user_id: string;
  amount: number;
  currency: string;
  plan: string;
  reference: string;
  status: "pending" | "paid" | "failed";
  created_at: string;
};

export async function getPaymentHistory(userId: string): Promise<Payment[]> {
  try {
    const r = await fetch(BASE_URL + "/api/payments/history/" + userId);
    const d = await r.json();
    return d.payments || [];
  } catch (e) {
    return [];
  }
}

export async function getPaymentStatus(userId: string): Promise<boolean> {
  try {
    const r = await fetch(BASE_URL + "/api/payments/status/" + userId);
    const d = await r.json();
    return d.active === true;
  } catch (e) {
    return false;
  }
}

export async function createPayment(
  userId: string,
  amount: number,
  plan: string = "monthly"
): Promise<{ ok: boolean; error?: string }> {
  try {
    const r = await fetch(BASE_URL + "/api/payments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        amount,
        currency: "NGN",
        plan,
        reference: "CKN-" + Date.now(),
        status: "paid",
      }),
    });
    const d = await r.json();
    return { ok: d.ok === true, error: d.error };
  } catch (e: any) {
    return { ok: false, error: e.message };
  }
}