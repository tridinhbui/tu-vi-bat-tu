// "Của bạn" layer: saved charts. Saving is for signed-in members (synced to the account); a guest who presses Save is asked to sign in,
// and the chart waits in this browser until the sign-in sync sends it. Charts a guest saved before this rule stay listed and sync on sign-in.
import { $, $$, esc } from './util.js';

const KEY = 'tvbt-saved-v1';
/** Set by account.js: hooks run after a local change, and whether this device is signed in (limit 12 local charts becomes 200). */
export const cloud = { on: false, push: null, remove: null, needLogin: false };   // needLogin: sign-in is available and nobody is signed in
const max = () => cloud.on ? 200 : 12;
const FIELDS = ['year', 'month', 'day', 'hour', 'minute', 'gender', 'tz', 'calendar', 'zi_rule', 'level', 'use_true_solar_time', 'longitude'];
/** 'Đã lập': a chart a member generated, kept automatically (autoSave) until they name it and say whose it is */
export const RELS = ['Tôi', 'Người thân', 'Bạn bè', 'Đã lập'];

export const readSaved = () => { try { const a = JSON.parse(localStorage.getItem(KEY)); return Array.isArray(a) ? a : []; } catch { return []; } };
export const writeSaved = a => { try { localStorage.setItem(KEY, JSON.stringify(a)); return true; } catch { return false; } };
const same = (a, b) => ['year', 'month', 'day', 'hour', 'minute', 'gender'].every(k => a[k] === b[k]);
const pick = req => Object.fromEntries(FIELDS.filter(k => req[k] !== undefined).map(k => [k, req[k]]));
const fmt = r => `${String(r.day).padStart(2, '0')}/${String(r.month).padStart(2, '0')}/${r.year} · ${String(r.hour).padStart(2, '0')}:${String(r.minute).padStart(2, '0')} · ${r.gender === 'male' ? 'Nam' : 'Nữ'}`;

export function saveChart(req, label, rel) {
  const list = readSaved(), r = pick(req), name = (label || '').trim().slice(0, 30) || rel;
  const i = list.findIndex(x => same(x.req, r));
  const item = { id: i >= 0 ? list[i].id : Date.now().toString(36), label: name, rel, req: r };
  if (i >= 0) list[i] = item; else list.unshift(item);
  if (!writeSaved(list.slice(0, max()))) return null;
  cloud.push?.(item);
  return item;
}
export const isSaved = req => readSaved().find(x => same(x.req, pick(req)));
export function removeSaved(id) { writeSaved(readSaved().filter(x => x.id !== id)); cloud.remove?.(id); }
export const fmtBirth = fmt;
/** A signed-in member never has to enter a birth twice: every chart they generate is kept in the account (the newest first). A chart
 *  already saved keeps its name; own (the profile's birth) is filed under 'Tôi', anything else under 'Đã lập'. */
export function autoSave(req, own) {
  if (!cloud.on || isSaved(req)) return null;
  return saveChart(req, own ? 'Tôi' : fmt(pick(req)).split(' · ')[0], own ? 'Tôi' : 'Đã lập');
}

/** Home list of saved charts; onOpen(req) generates the chart again from the stored birth data. Comparing two charts lives in compare.js. */
export function renderSaved(host, onOpen) {
  const list = readSaved(), sec = host.closest('section') || host;
  sec.hidden = !list.length;
  const head = sec.querySelector('.eyebrow'), h2 = sec.querySelector('h2'), sub = sec.querySelector('.sec-sub');
  if (head && h2 && sub) {
    head.textContent = cloud.on ? 'Tài khoản của bạn' : 'Trên máy này'; h2.textContent = cloud.on ? 'Lá số của tôi' : 'Lá số bạn đã lưu';
    sub.textContent = cloud.on ? 'Mọi lá số bạn đã lập đều được giữ ở đây; bấm để mở lại, không cần nhập lại ngày giờ sinh.' : 'Của bạn và người thân. Chỉ nằm trong trình duyệt này; bấm để mở lại.';
  }
  host.innerHTML = list.map(x => `<li><button type="button" class="sv-open" data-id="${esc(x.id)}"><span class="sv-rel">${esc(x.rel)}</span><b>${esc(x.label)}</b><small>${esc(fmt(x.req))}</small></button><button type="button" class="sv-del" data-id="${esc(x.id)}" aria-label="Xóa lá số ${esc(x.label)}">Xóa</button></li>`).join('');
  $$('.sv-open', host).forEach(b => b.onclick = () => onOpen(list.find(x => x.id === b.dataset.id).req));
  $$('.sv-del', host).forEach(b => b.onclick = () => { removeSaved(b.dataset.id); renderSaved(host, onOpen); });
}

/** Save control on the result page: one button that expands to name + relation. */
export function initSave(host, getReq, onChange) {
  host.innerHTML = `<button type="button" class="btn btn-ghost btn-sm" id="sv-btn" aria-expanded="false"></button>
    <form class="sv-form" id="sv-form" hidden><label>Tên gọi<input name="label" maxlength="30" placeholder="Ví dụ: Mẹ, Minh…" autocomplete="off"></label>
    <label>Mối quan hệ<select name="rel">${RELS.map(r => `<option>${r}</option>`).join('')}</select></label>
    <button class="btn btn-sm" type="submit"></button><p class="muted small sv-note"></p></form>`;
  const btn = $('#sv-btn', host), form = $('#sv-form', host);
  const note = () => { $('.sv-note', host).textContent = cloud.on ? 'Lưu vào tài khoản của bạn và đồng bộ giữa các thiết bị. Xóa được bất cứ lúc nào ở trang chủ.' : 'Chỉ lưu trong trình duyệt của bạn; máy chủ không nhận được gì. Đăng nhập để đồng bộ giữa các thiết bị.'; $('button[type=submit]', form).textContent = cloud.on ? 'Lưu vào tài khoản' : 'Lưu trên máy này'; };
  const guest = () => cloud.needLogin && !cloud.on;
  const paint = () => {
    note(); const s = getReq() && isSaved(getReq());
    btn.textContent = s ? `Đã lưu: ${s.label} · sửa tên` : 'Lưu lá số này';
    if (guest()) {
      $('.sv-note', host).innerHTML = 'Lưu lá số dành cho thành viên: đăng nhập bằng Google, lá số được lưu vào tài khoản và mở được trên mọi thiết bị. <a href="#quyen-loi" data-go="quyen-loi">Xem quyền lợi khi đăng nhập</a>';
      $('button[type=submit]', form).textContent = 'Đăng nhập Google và lưu';
    }
  };
  btn.onclick = () => { const o = form.hidden; form.hidden = !o; btn.setAttribute('aria-expanded', o); const s = isSaved(getReq()); if (s) { form.label.value = s.label; form.rel.value = s.rel; } };
  form.onsubmit = e => {
    e.preventDefault();
    const ok = saveChart(getReq(), form.label.value, form.rel.value);
    if (!ok) { $('.muted', form).textContent = 'Trình duyệt không cho phép lưu (chế độ riêng tư hoặc đã chặn lưu trữ).'; return; }
    // guest: the chart is now held in this browser; after Google sign-in, account.js syncs it into the account
    if (guest()) { location.href = '/api/auth/google'; return; }
    form.hidden = true; btn.setAttribute('aria-expanded', 'false'); paint(); onChange();
  };
  paint();
  return { paint };
}
