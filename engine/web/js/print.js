// "Tải PDF": uses the browser's own print dialog ("Lưu thành PDF"), with a print layout that shows both systems in the plain-language mode.
import { $, $$ } from './util.js';

let undo = null;
/** Opens collapsed sections, switches to 'Dễ hiểu', and shows the full Tử Vi board; returns a function that restores the screen state. */
function prepare() {
  if (undo) return;
  // the board's view switch lives on the element carrying data-view inside #tuvi-host (.tv-stage in the observatory layout)
  const opened = $$('#chart-view details:not([open])'), depth = document.body.dataset.depth, host = $('#tuvi-host [data-view]') || $('#tuvi-host'), view = host?.dataset.view;
  opened.forEach(d => { d.open = true; });
  // chapter bubbles type their text when scrolled into view: make sure every one is complete before printing
  $$('.gd-chap .gd-t').forEach(t => { if (!t.textContent) t.textContent = ($('.gd-sr', t.parentElement)?.textContent || '').replace(/^[^:]+:\s*/, ''); });
  document.body.dataset.depth = 'easy';
  if (host) host.dataset.view = 'full';
  document.body.classList.add('printing');
  // the Trưởng thành pane is interactive; with the layer switched off (tab hidden) or empty it would print a header over nothing
  document.body.classList.toggle('print-no-growth', !!$('#tab-growth')?.hidden || !$('#growth-host')?.children.length);
  undo = () => {
    opened.forEach(d => { d.open = false; });
    document.body.dataset.depth = depth;
    if (host && view) host.dataset.view = view;
    document.body.classList.remove('printing', 'print-no-growth');
    undo = null;
  };
}
export function initPrint(btn) {
  addEventListener('beforeprint', prepare); // also covers Ctrl/Cmd+P
  addEventListener('afterprint', () => undo?.());
  btn.onclick = () => { prepare(); requestAnimationFrame(() => requestAnimationFrame(() => window.print())); };
}
