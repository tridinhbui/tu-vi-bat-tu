// One-screen layout helpers (css/dash.css). On a wide, tall window the written reading is one viewport tall with its text scrolling
// inside, so the long "what was calculated" note must start collapsed there; it stays open on narrow screens, where the page flows.
export const dashMode = () => matchMedia('(min-width:1100px) and (min-height:600px)').matches;
export function collapseWhenDash(host) {
  if (!host) return;
  const fold = () => { if (dashMode()) host.querySelectorAll('details.sc[open]').forEach(d => { if (!d.dataset.userToggled) d.open = false; }); };
  host.addEventListener('toggle', e => { if (e.target.matches?.('details.sc')) e.target.dataset.userToggled = '1'; }, true);
  new MutationObserver(fold).observe(host, { childList: true });
  fold();
}
