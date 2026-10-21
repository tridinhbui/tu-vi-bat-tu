// VNPAY payment gateway (API version 2.1.0). Signed URLs and HMAC only, no SDK to install in the Worker.
//
//   1. createPaymentUrl: the visitor is sent to VNPAY_URL with the order's parameters, signed with HMAC-SHA512 (VNPAY_HASH_SECRET).
//   2. IPN (GET /api/vnpay/ipn, URL registered in the VNPAY merchant portal): VNPAY's server tells us the result. We verify the signature,
//      find OUR order by vnp_TxnRef, check the amount against it, and credit the coins once. This is the only place coins are credited.
//   3. Return URL (GET /api/vnpay/return): the visitor's browser comes back. We verify the signature only to show the right message,
//      then send the visitor to the receipt page; nothing is credited here (VNPAY's own rule: the database is updated from the IPN).
//
// Signing follows VNPAY's 2.1.0 integration code: every vnp_* field except vnp_SecureHash / vnp_SecureHashType, sorted by key, each key
// and value URL-encoded the way PHP's urlencode does it (space as "+"), joined as key=value&...; the hash is the lower-case hex HMAC-SHA512
// of that string. The same encoded string is the query string of the payment URL.
//
// Disabled unless VNPAY_ENABLED is "1" AND VNPAY_TMN_CODE and VNPAY_HASH_SECRET are set: the owner turns it on with real merchant keys.
import type { Order } from "./orders.ts";
import { completeOrder, failOrder, getOrder } from "./orders.ts";

export const VNPAY_SANDBOX_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html";
export interface VnpayEnv { VNPAY_ENABLED?: string; VNPAY_TMN_CODE?: string; VNPAY_HASH_SECRET?: string; VNPAY_URL?: string }
export interface VnpayConfig { tmnCode: string; hashSecret: string; url: string }

export function vnpayConfig(env: VnpayEnv): VnpayConfig | null {
  if (env.VNPAY_ENABLED !== "1" || !env.VNPAY_TMN_CODE || !env.VNPAY_HASH_SECRET) return null;
  return { tmnCode: env.VNPAY_TMN_CODE, hashSecret: env.VNPAY_HASH_SECRET, url: env.VNPAY_URL || VNPAY_SANDBOX_URL };
}

const enc = new TextEncoder();
/** PHP urlencode: encodeURIComponent plus !'()* encoded, and a space as "+". */
export const phpEncode = (s: string) => encodeURIComponent(s).replace(/[!'()*]/g, c => "%" + c.charCodeAt(0).toString(16).toUpperCase()).replace(/%20/g, "+");

/** The string that is signed: sorted vnp_* fields (the hash fields excluded), encoded key=value pairs joined by "&". */
export function signData(params: Record<string, string>, { keepEmpty = false } = {}): string {
  return Object.keys(params)
    .filter(k => k.startsWith("vnp_") && k !== "vnp_SecureHash" && k !== "vnp_SecureHashType" && (keepEmpty || params[k] !== ""))
    .sort()
    .map(k => `${phpEncode(k)}=${phpEncode(params[k])}`).join("&");
}

export async function hmacSha512(secret: string, msg: string): Promise<string> {
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-512" }, false, ["sign"]);
  return [...new Uint8Array(await crypto.subtle.sign("HMAC", key, enc.encode(msg)))].map(x => x.toString(16).padStart(2, "0")).join("");
}
const sameHex = (a: string, b: string) => { a = a.toLowerCase(); b = b.toLowerCase(); if (a.length !== b.length) return false; let d = 0; for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i); return d === 0; };

/** Checks vnp_SecureHash on a callback. VNPAY's sample code differs on fields sent with an empty value (the PHP and Node samples sign
 *  them, the Java and .NET samples skip them), so both forms are tried; either needs the secret. */
export async function verifyVnpay(params: URLSearchParams | Record<string, string>, secret: string): Promise<boolean> {
  const p = params instanceof URLSearchParams ? Object.fromEntries(params) : params;
  const got = p.vnp_SecureHash;
  if (!got || !/^[0-9a-fA-F]{128}$/.test(got)) return false;
  if (sameHex(got, await hmacSha512(secret, signData(p)))) return true;
  return Object.values(p).some(v => v === "") && sameHex(got, await hmacSha512(secret, signData(p, { keepEmpty: true })));
}

const pad = (n: number) => String(n).padStart(2, "0");
/** yyyyMMddHHmmss in Vietnam time (GMT+7), the format of vnp_CreateDate and vnp_ExpireDate. */
export function vnpTime(ms: number): string {
  const d = new Date(ms + 7 * 3600_000);
  return `${d.getUTCFullYear()}${pad(d.getUTCMonth() + 1)}${pad(d.getUTCDate())}${pad(d.getUTCHours())}${pad(d.getUTCMinutes())}${pad(d.getUTCSeconds())}`;
}
export const PAYMENT_WINDOW_MIN = 15;

/** The signed URL that opens VNPAY's payment page for an order. vnp_Amount is the VND amount times 100 (VNPAY's rule). */
export async function createPaymentUrl(cfg: VnpayConfig, o: { order: Pick<Order, "id" | "amount" | "coins">; returnUrl: string; ip: string; now?: number; locale?: "vn" | "en"; bankCode?: string }): Promise<string> {
  const now = o.now ?? Date.now();
  const params: Record<string, string> = {
    vnp_Version: "2.1.0", vnp_Command: "pay", vnp_TmnCode: cfg.tmnCode, vnp_Amount: String(o.order.amount * 100), vnp_CurrCode: "VND",
    vnp_TxnRef: o.order.id, vnp_OrderInfo: `Nap ${o.order.coins} xu Thien Ban, don ${o.order.id}`,          // VNPAY asks for plain ASCII here
    vnp_OrderType: "other", vnp_Locale: o.locale ?? "vn", vnp_ReturnUrl: o.returnUrl, vnp_IpAddr: o.ip || "127.0.0.1",
    vnp_CreateDate: vnpTime(now), vnp_ExpireDate: vnpTime(now + PAYMENT_WINDOW_MIN * 60_000),
  };
  if (o.bankCode) params.vnp_BankCode = o.bankCode;
  const data = signData(params);
  return `${cfg.url}?${data}&vnp_SecureHash=${await hmacSha512(cfg.hashSecret, data)}`;
}

/** VNPAY's IPN answer codes (the body VNPAY expects back, always with HTTP 200). */
export const IPN = {
  ok: { RspCode: "00", Message: "Confirm Success" },
  notFound: { RspCode: "01", Message: "Order not found" },
  already: { RspCode: "02", Message: "Order already confirmed" },
  badAmount: { RspCode: "04", Message: "Invalid amount" },
  badSignature: { RspCode: "97", Message: "Invalid signature" },
  error: { RspCode: "99", Message: "Unknown error" },
} as const;
export type IpnAnswer = (typeof IPN)[keyof typeof IPN];

/** Handles one IPN call. Safe to receive any number of times: a paid order answers "02" and credits nothing more. */
export async function handleIpn(db: D1Database, cfg: VnpayConfig, params: URLSearchParams, now = Date.now()): Promise<{ answer: IpnAnswer; result?: "credited" | "duplicate" | "failed" }> {
  if (!(await verifyVnpay(params, cfg.hashSecret)) || params.get("vnp_TmnCode") !== cfg.tmnCode) return { answer: IPN.badSignature };
  const id = params.get("vnp_TxnRef") ?? "";
  const order = /^[0-9a-f]{20}$/.test(id) ? await getOrder(db, id) : null;
  if (!order || order.provider !== "vnpay") return { answer: IPN.notFound };
  if (params.get("vnp_Amount") !== String(order.amount * 100)) return { answer: IPN.badAmount };
  if (order.status !== "pending") return { answer: IPN.already };
  const code = params.get("vnp_ResponseCode"), status = params.get("vnp_TransactionStatus");
  const detail = `vnp ${code}/${status} ${params.get("vnp_BankCode") ?? ""} ${params.get("vnp_PayDate") ?? ""}`.trim();
  if (code === "00" && status === "00") {
    const result = await completeOrder(db, order, params.get("vnp_TransactionNo") ?? "", detail, now);
    return { answer: IPN.ok, result };
  }
  await failOrder(db, order.id, detail);
  return { answer: IPN.ok, result: "failed" };                         // "00" acknowledges that we recorded the result, success or not
}

/** VNPAY response codes a visitor may see on return, in plain Vietnamese (the common ones; others show the code). */
export const RESPONSE_VI: Record<string, string> = {
  "00": "Giao dịch thành công.", "07": "Giao dịch bị nghi ngờ gian lận, đang chờ ngân hàng xác minh.", "09": "Thẻ hoặc tài khoản chưa đăng ký Internet Banking.",
  "10": "Xác thực thông tin thẻ hoặc tài khoản sai quá 3 lần.", "11": "Hết thời gian chờ thanh toán.", "12": "Thẻ hoặc tài khoản bị khóa.",
  "13": "Sai mật khẩu xác thực giao dịch (OTP).", "24": "Bạn đã hủy giao dịch.", "51": "Tài khoản không đủ số dư.", "65": "Tài khoản đã vượt hạn mức giao dịch trong ngày.",
  "75": "Ngân hàng thanh toán đang bảo trì.", "79": "Nhập sai mật khẩu thanh toán quá số lần quy định.", "99": "Lỗi không xác định.",
};
