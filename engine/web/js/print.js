// "Tải PDF": uses the browser's own print dialog ("Lưu thành PDF"), with a print layout that shows both systems.
// The default PDF is the reading (plan magical-magpie W4): Chân dung lá số, the chapters' prose with their Đọc sâu folds open, and a short
// appendix of rules and book pages per chapter; the evidence folds (Vì sao?, Căn cứ, Luận giải chuyên sâu, the calculation trace) stay out.
// "In bản đầy đủ (kiểm toán)" (body.print-full) prints as before: every fold open.
import { $, $$ } from './util.js';

let undo = null, full = false;
/** the folds the reading itself is made of: the Tử Vi and Bát Tự Đọc sâu (a Bát Tự "Số liệu" fold holds numbers, not reading) */
const READING_FOLDS = '#chart-view details.pr-deep:not([open]), #chart-view details.bt-sau:not(.bt-num):not([open])';
/** Opens the folds to print and shows the full Tử Vi board; returns a function that restores the screen state. */
function prepare() {
  if (undo) return;
  // the board's view switch lives on the element carrying data-view inside #tuvi-host (.tv-stage in the observatory layout)
  const opened = $$(full ? '#chart-view details:not([open])' : READING_FOLDS), host = $('#tuvi-host [data-view]') || $('#tuvi-host'), view = host?.dataset.view;
  opened.forEach(d => { d.open = true; });
  // chapter bubbles type their text when scrolled into view: make sure every one is complete before printing
  $$('.gd-chap .gd-t').forEach(t => { if (!t.textContent) t.textContent = ($('.gd-sr', t.parentElement)?.textContent || '').replace(/^[^:]+:\s*/, ''); });
  if (host) host.dataset.view = 'full';
  document.body.classList.add('printing');
  document.body.classList.toggle('print-full', full);
  // the Trưởng thành pane is interactive; with the layer switched off (tab hidden) or empty it would print a header over nothing
  document.body.classList.toggle('print-no-growth', !!$('#tab-growth')?.hidden || !$('#growth-host')?.children.length);
  undo = () => {
    opened.forEach(d => { d.open = false; });
    if (host && view) host.dataset.view = view;
    document.body.classList.remove('printing', 'print-no-growth', 'print-full');
    full = false; undo = null;
  };
}
export function initPrint(btn, fullBtn) {
  addEventListener('beforeprint', prepare); // also covers Ctrl/Cmd+P (the reading version)
  addEventListener('afterprint', () => undo?.());
  btn.onclick = () => printNow();
  if (fullBtn) fullBtn.onclick = () => printNow(true);
}
/** `audit`: the full version for checking, every fold open (the PDF as it was before the reading version) */
export function printNow(audit = false) { undo?.(); full = audit; prepare(); requestAnimationFrame(() => requestAnimationFrame(() => window.print())); }
