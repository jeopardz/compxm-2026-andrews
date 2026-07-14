// Lemon Squeezy order webhook. Required secrets: LS_SIGNING_SECRET,
// LS_STORE_ID, LS_VARIANT_IDS (comma-separated), SUPABASE_URL and
// SUPABASE_SERVICE_ROLE_KEY.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { createHmac } from "node:crypto";

function verifySignature(raw: string, signature: string, secret: string): boolean {
  const digest = createHmac("sha256", secret).update(raw).digest("hex");
  if (digest.length !== signature.length) return false;
  let diff = 0;
  for (let i = 0; i < digest.length; i++) diff |= digest.charCodeAt(i) ^ signature.charCodeAt(i);
  return diff === 0;
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("method not allowed", { status: 405 });
  const secret = Deno.env.get("LS_SIGNING_SECRET") ?? "";
  if (!secret) return new Response("server not configured", { status: 500 });

  const raw = await req.text();
  if (!verifySignature(raw, req.headers.get("X-Signature") ?? "", secret)) {
    return new Response("invalid signature", { status: 401 });
  }
  let event: any;
  try { event = JSON.parse(raw); } catch { return new Response("bad json", { status: 400 }); }

  const attrs = event?.data?.attributes ?? {};
  if (event?.meta?.event_name !== "order_created" || attrs.status !== "paid") {
    return new Response("ignored", { status: 200 });
  }
  const userId = String(event?.meta?.custom_data?.user_id ?? "");
  const orderId = String(event?.data?.id ?? "");
  if (!userId || !orderId) return new Response("missing user_id/order", { status: 400 });

  const expectedStore = Deno.env.get("LS_STORE_ID") ?? "";
  const allowedVariants = (Deno.env.get("LS_VARIANT_IDS") ?? "")
    .split(",").map((v) => v.trim()).filter(Boolean);
  const storeId = String(attrs.store_id ?? "");
  const variantId = String(attrs.first_order_item?.variant_id ?? attrs.variant_id ??
    event?.data?.relationships?.variant?.data?.id ?? "");
  if (!expectedStore || allowedVariants.length === 0) {
    return new Response("product validation not configured", { status: 500 });
  }
  if (storeId !== expectedStore || !allowedVariants.includes(variantId)) {
    return new Response("order is not for CompMastery", { status: 200 });
  }

  const url = Deno.env.get("SUPABASE_URL");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !serviceKey) return new Response("database not configured", { status: 500 });
  const supabase = createClient(url, serviceKey);
  const { error } = await supabase.rpc("process_ls_order", {
    p_user_id: userId, p_order_id: orderId,
    p_amount: typeof attrs.total === "number" ? attrs.total / 100 : null,
    p_currency: attrs.currency ?? "USD", p_raw: event,
  });
  if (error) return new Response(`order processing failed: ${error.message}`, { status: 500 });
  return new Response("ok", { status: 200 });
});
