// "Luận AI" under a report chapter: the long reading of that chapter written by the model (POST /api/me/deep, src/chat/deep.ts), not to be
// confused with the book-based "Đọc sâu (theo sách)". The AI chapters are fewer than the report's (src/interpret/chapters.ts groups Phụ
// Mẫu, Huynh Đệ, Tử Tức and Thiên Di, Nô Bộc, Tật Ách), so a grouped card sits under the last palace of its group. A written chapter is
// replayed free; the chart's Cao cấp package writes every chapter without xu (POST /api/me/deep/status says which).
import { esc } from './util.js';
import { COIN_SVG } from './account.js';

const AI_OF = {
  menh: 'menh', cong_danh: 'cong_danh', tai_bach: 'tai_bach', phu_the: 'phu_the', phuc_duc: 'phuc_duc', dien_trach: 'dien_trach',
  phu_mau: 'gia_dao', tat_ach: 'di_no_tat', van_han: 'van_han', 'bat_tu:nhat-chu': 'bat_tu',
};
const AI_TITLE = {
  menh: 'Mệnh, Thân và tính cách', cong_danh: 'Công danh', tai_bach: 'Tài Bạch', phu_the: 'Phu Thê', phuc_duc: 'Phúc Đức', dien_trach: 'Điền Trạch',
  gia_dao: 'Phụ Mẫu, Huynh Đệ và Tử Tức', di_no_tat: 'Thiên Di, Nô Bộc và Tật Ách', van_han: 'Đại hạn và tiểu hạn', bat_tu: 'Bát Tự',
};

/** The empty card for a report chapter ('' when the chapter has no AI reading of its own); initAiCards fills it. */
export function aiSlot(chapter) {
  const id = AI_OF[chapter];
  return id ? `<div class="ai-card" data-ai="${id}"><p class="eyebrow">Luận riêng · ${esc(AI_TITLE[id])}</p><div class="ai-body"></div></div>` : '';
}

const post = (path, body) => fetch(path, { method: 'POST', credentials: 'same-origin', headers: { 'content-type': 'application/json', 'x-tvbt': '1' }, body: JSON.stringify(body) });
const FIELDS = ['year', 'month', 'day', 'hour', 'minute', 'gender', 'tz', 'calendar', 'zi_rule', 'level', 'use_true_solar_time', 'longitude'];
const pick = r => Object.fromEntries(FIELDS.filter(k => r[k] !== undefined).map(k => [k, r[k]]));

// the model writes plain text with a few "## " headings, "- " lists and **bold**: escaped first, then only these marks become tags
function textHtml(t) {
  const inline = s => esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
  return t.split(/\n{2,}/).map(b => b.trim()).filter(Boolean).map(b => {
    const h = b.match(/^#{1,4}\s+(.*)$/);
    if (h && !b.includes('\n')) return `<h5>${inline(h[1])}</h5>`;
    const lines = b.split('\n');
    if (lines.every(l => /^\s*[-*•]\s+/.test(l))) return `<ul>${lines.map(l => `<li>${inline(l.replace(/^\s*[-*•]\s+/, ''))}</li>`).join('')}</ul>`;
    return `<p>${lines.map(inline).join('<br>')}</p>`;
  }).join('');
}

/** getReq(): the birth record of the chart on screen (null on a share link: no card is filled). */
export function initAiCards(getReq) {
  let me = null, key = '', status = null, busy = false;
  const meReady = fetch('/api/auth/me', { credentials: 'same-origin' }).then(r => r.ok ? r.json() : null).then(j => { me = j; }).catch(() => { me = null; });
  const statusFor = async req => {
    const k = JSON.stringify(pick(req));
    if (k !== key || !status) {
      key = k;
      status = post('/api/me/deep/status', { birth: pick(req) }).then(r => r.ok ? r.json() : null).catch(() => null);
    }
    return status;
  };

  async function fill(card) {
    card.dataset.ready = '1';
    const body = card.querySelector('.ai-body'), id = card.dataset.ai, req = getReq();
    if (!req) { card.hidden = true; return; }
    await meReady;
    if (!me?.user) {
      body.innerHTML = `<p class="small">Bài viết riêng cho lá số của bạn, khoảng 500–800 từ, soạn từ dữ kiện và luận giải đã có của chương này.</p>
        <p><a class="btn btn-sm btn-ghost" href="/api/auth/google" data-pw-signin>Đăng nhập để dùng Luận riêng</a></p>`;
      return;
    }
    const st = await statusFor(req);
    if (!st) { card.hidden = true; return; }                                       // not available on this server
    const written = st.written.includes(id);
    const label = written ? 'Đọc Luận riêng đã viết' : st.plan ? 'Viết Luận riêng (đã gồm trong gói Cao cấp)' : `Viết Luận riêng · ${COIN_SVG}<b>${Number(st.cost)}</b> xu`;
    body.innerHTML = `${written ? '' : `<p class="small">Bài viết riêng cho lá số của bạn, khoảng 500–800 từ: nối chương này với các cung liên quan, chỉ dùng dữ kiện và luận giải đã có, không thêm sao hay nhận định mới. Viết một lần, đọc lại không tốn thêm; viết hỏng thì không bị tính.${st.plan ? '' : ' <a href="/bang-gia">Gói Cao cấp</a> gồm Luận riêng mọi chương.'}</p>`}
      <p><button type="button" class="btn btn-sm${written ? ' btn-ghost' : ''}" data-ai-go>${label}</button></p><div class="ai-text"></div><p class="ai-msg small" role="status" aria-live="polite"></p>`;
  }

  async function write(card) {
    const req = getReq(); if (!req || busy) return;
    const id = card.dataset.ai, btn = card.querySelector('[data-ai-go]'), out = card.querySelector('.ai-text'), msg = card.querySelector('.ai-msg');
    busy = true; btn.disabled = true; msg.className = 'ai-msg small'; msg.textContent = 'Đang viết, khoảng nửa phút…';
    let got = '', failed = false;
    try {
      const res = await post('/api/me/deep', { birth: pick(req), chapter: id });
      if (res.status === 402) { const j = await res.json(); if (j.wallet) dispatchEvent(new CustomEvent('tvbt:wallet', { detail: j.wallet })); msg.innerHTML = `Cần ${Number(j.need)} xu, ví đang có ${Number(j.wallet?.coins ?? 0)} xu. <a href="/bang-gia#nap-xu">Nạp xu</a>`; msg.classList.add('err'); return; }
      if (res.status === 401) { msg.innerHTML = 'Phiên đăng nhập đã hết. <a href="/api/auth/google" data-pw-signin>Đăng nhập lại</a>'; msg.classList.add('err'); return; }
      if (res.status === 503) { msg.textContent = 'Luận riêng đang tạm dừng. Bạn thử lại sau nhé.'; msg.classList.add('err'); return; }
      if (!res.ok || !res.body) throw new Error(String(res.status));
      const rd = res.body.getReader(), dec = new TextDecoder(); let buf = '';
      for (;;) {
        const { value, done } = await rd.read(); if (done) break;
        buf += dec.decode(value, { stream: true });
        let i; while ((i = buf.indexOf('\n\n')) >= 0) {
          const line = buf.slice(0, i); buf = buf.slice(i + 2);
          if (!line.startsWith('data: ')) continue;
          const ev = JSON.parse(line.slice(6));
          if (ev.type === 'delta') { got += ev.text; out.innerHTML = textHtml(got); msg.textContent = ''; }
          else if (ev.type === 'error') { failed = true; msg.textContent = ev.message + (ev.refunded ? ' Lượt này không bị tính.' : ''); msg.classList.add('err'); }
          else if (ev.type === 'wallet') dispatchEvent(new CustomEvent('tvbt:wallet', { detail: ev.wallet }));
        }
      }
      if (got && !failed) { btn.closest('p').remove(); card.querySelector('.ai-body > p.small:not(.ai-msg)')?.remove(); status = null; }
    } catch { msg.textContent = 'Mất kết nối khi đang viết. Bài đang viết vẫn được lưu nếu đã xong: bấm lại để đọc, không bị tính thêm.'; msg.classList.add('err'); }
    finally { busy = false; if (btn.isConnected) btn.disabled = false; }
  }

  document.addEventListener('click', e => { const b = e.target.closest('.ai-card [data-ai-go]'); if (b) write(b.closest('.ai-card')); });
  // a package bought on this page may now cover the AI chapters
  addEventListener('tvbt:unlocked', () => { status = null; });
  const scan = () => document.querySelectorAll('.ai-card:not([data-ready])').forEach(fill);
  new MutationObserver(scan).observe(document.body, { childList: true, subtree: true });
  scan();
}
