// Mời bạn. On every page: a ?ref=CODE link is remembered on this device (and removed from the address bar). Where the account
// menu exists (#acct, home page) and the visitor is signed in: claim the remembered code once (the server only pays a NEW account),
// and add a "Mời bạn" button that shows the visitor's own code and link. Coins are credited by the server through the wallet.
const KEY = 'tvbt-ref', CODE = /^[A-HJ-NP-Z2-9]{8}$/;
const ls = { get: () => { try { return JSON.parse(localStorage.getItem(KEY)); } catch { return null; } },
  set: v => { try { v ? localStorage.setItem(KEY, JSON.stringify(v)) : localStorage.removeItem(KEY); } catch { /* private mode */ } } };
const api = (path, opts = {}) => fetch(path, { credentials: 'same-origin', ...opts, headers: { 'x-tvbt': '1', 'content-type': 'application/json', ...(opts.headers || {}) } });
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

const url = new URL(location.href), incoming = (url.searchParams.get('ref') || '').trim().toUpperCase();
if (incoming) {
  if (CODE.test(incoming)) ls.set({ code: incoming, at: Date.now() });
  url.searchParams.delete('ref');
  history.replaceState(null, '', url.pathname + (url.search || '') + url.hash);
}

const CSS = `.acct-ref{font:600 .8rem var(--sans);color:var(--text2);background:none;border:1px solid var(--line);border-radius:99px;padding:5px 10px;cursor:pointer;white-space:nowrap;min-height:32px}
.acct-ref:hover{border-color:var(--brass);color:var(--ink)}@media (max-width:600px){.acct-ref{display:none}}
.ref-dlg .ref-code{font:600 1.6rem/1 ui-monospace,Menlo,monospace;letter-spacing:.12em;background:var(--raise);border:1px dashed var(--brass);border-radius:12px;padding:12px 16px}
.ref-dlg .ref-row{display:flex;gap:8px;flex-wrap:wrap;width:100%}.ref-dlg input{flex:1;min-width:0;height:42px;border:1px solid var(--line);border-radius:10px;padding:0 10px;font:.9rem var(--sans);background:var(--raise)}
.ref-dlg .ref-note{font-size:.85rem;color:var(--muted);margin:0}.ref-dlg .ref-msg{font-size:.9rem;margin:0}
.ref-toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:90;background:var(--ink);color:#FFF8F0;border-radius:12px;padding:12px 18px;font-size:.9rem;max-width:min(92vw,480px);box-shadow:var(--sh)}`;

function toast(text) {
  const t = document.createElement('div'); t.className = 'ref-toast'; t.setAttribute('role', 'status'); t.textContent = text;
  document.body.append(t); setTimeout(() => t.remove(), 6000);
}

async function refreshWallet() {
  try { const r = await api('/api/me/wallet'); if (r.ok) dispatchEvent(new CustomEvent('tvbt:wallet', { detail: await r.json() })); } catch { /* chip refreshes next visit */ }
}

const REASON = { bad_code: 'Mã mời không đúng.', own_code: 'Đây là mã của chính bạn.', too_old: 'Mã mời chỉ dành cho tài khoản mới (trong 7 ngày đầu).',
  already_claimed: 'Tài khoản này đã nhận lời mời của một người khác.', inviter_full: 'Mã này đã đạt số lượt mời tối đa.' };

async function doClaim(code) {
  const r = await api('/api/me/referral/claim', { method: 'POST', body: JSON.stringify({ code }) });
  const j = await r.json().catch(() => ({}));
  if (j.ok) { await refreshWallet(); return { ok: true, text: `Đã nhận lời mời: bạn được cộng ${j.inviteeCoins} xu, người mời được ${j.inviterCoins} xu.` }; }
  return { ok: false, reason: j.reason || '', text: REASON[j.reason] || 'Chưa nhận được lời mời, vui lòng thử lại sau.' };
}

function dialog(info) {
  let d = document.getElementById('ref-dlg');
  if (!d) { d = document.createElement('dialog'); d.id = 'ref-dlg'; d.className = 'dlg ref-dlg'; document.body.append(d); }
  const share = navigator.share ? '<button type="button" class="btn btn-sm" data-share>Chia sẻ</button>' : '';
  d.innerHTML = `<form method="dialog"><h3>Mời bạn</h3>
    <p class="ref-msg">Mỗi người bạn mở tài khoản mới qua liên kết của bạn: bạn nhận <b>${info.reward.inviter} xu</b>, bạn của bạn nhận <b>${info.reward.invitee} xu</b> (tối đa ${info.maxPerInviter} người).</p>
    <div class="ref-code" aria-label="Mã mời của bạn">${esc(info.code)}</div>
    <div class="ref-row"><input readonly value="${esc(info.url)}" aria-label="Liên kết mời"><button type="button" class="btn btn-sm btn-ghost" data-copy>Sao chép</button>${share}</div>
    <p class="ref-note">Đã có ${info.invited} người tham gia qua mã này · bạn đã nhận ${info.coinsEarned} xu.</p>
    ${info.canClaim ? `<p class="ref-msg">Bạn được ai đó mời? Nhập mã của họ:</p><div class="ref-row"><input name="claim" maxlength="8" autocomplete="off" autocapitalize="characters" placeholder="Mã 8 ký tự" aria-label="Mã mời của người khác"><button type="button" class="btn btn-sm" data-claim>Nhận</button></div><p class="ref-note" data-out aria-live="polite"></p>` : ''}
    <button class="btn btn-ghost">Đóng</button></form>`;
  d.querySelector('[data-copy]').onclick = async e => { try { await navigator.clipboard.writeText(info.url); e.target.textContent = 'Đã chép'; } catch { d.querySelector('input').select(); } };
  const sh = d.querySelector('[data-share]'); if (sh) sh.onclick = () => navigator.share({ title: 'Thiên Bàn', text: 'Lập lá số Tử Vi và Bát Tự, luận giải có ghi nguồn sách.', url: info.url }).catch(() => {});
  const cl = d.querySelector('[data-claim]');
  if (cl) cl.onclick = async () => { const r = await doClaim(d.querySelector('[name=claim]').value.trim().toUpperCase()); d.querySelector('[data-out]').textContent = r.text; if (r.ok) { ls.set(null); info.canClaim = false; } };
  d.showModal();
}

async function signedIn(host) {
  const pending = ls.get();
  let info;
  try { const r = await api('/api/me/referral'); if (!r.ok) return; info = await r.json(); } catch { return; }
  if (pending && info.canClaim && pending.code !== info.code) {
    const r = await doClaim(pending.code); toast(r.text);
    if (r.ok || r.reason) ls.set(null);              // a definite answer (paid or refused): do not try again; a network error retries next visit
    if (r.ok) info.canClaim = false;
  } else if (pending && !info.canClaim) ls.set(null);           // an existing account: nothing to claim, forget the code
  if (host.querySelector('.acct-ref')) return;
  const b = document.createElement('button'); b.type = 'button'; b.className = 'acct-ref'; b.textContent = 'Mời bạn'; b.title = 'Mã mời và liên kết giới thiệu của bạn';
  b.onclick = async () => { try { const r = await api('/api/me/referral'); if (r.ok) info = await r.json(); } catch { /* show the last one */ } dialog(info); };
  host.querySelector('.acct-out')?.before(b);
}

const host = document.getElementById('acct');
if (host) {
  const st = document.createElement('style'); st.textContent = CSS; document.head.append(st);
  let told = false;
  const check = () => {
    if (host.querySelector('.acct-out')) { obs.disconnect(); signedIn(host); }
    else if (!told && host.querySelector('.acct-in') && incoming && ls.get()) { told = true; toast('Bạn được bạn bè mời dùng Thiên Bàn. Đăng nhập với Google để cả hai cùng nhận xu.'); }
  };
  const obs = new MutationObserver(check);
  obs.observe(host, { childList: true, subtree: true });
  check();
}
