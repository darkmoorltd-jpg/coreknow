import { useState, useEffect } from "react";
import { day8 } from "./day8";
import { useAuth } from "./store";

export function useAB(testKey: string, fallback: string = 'a') {
  const user = useAuth((s) => s.user);
  const [variant, setVariant] = useState(fallback);

  useEffect(() => {
    if (!user?.id) return;
    day8.getVariant(testKey, user.id).then((d) => {
      if (d.variant) setVariant(d.variant);
    }).catch(() => {});
  }, [testKey, user]);

  return variant;
}
