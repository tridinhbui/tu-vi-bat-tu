// The four guides' names and their inline-SVG avatars. Kept apart from mascots.js (which needs the chart modules) so the site-wide
// chat (ask.js, "Hỏi Bát Bát") can draw Bát Bát on any page without loading the chart code.
export const GUIDES = {
  tu1: { name: 'Tử Tử', side: 'tv', role: 'người dẫn đường Tử Vi' },
  vi: { name: 'Vi Vi', side: 'tv', role: 'người bạn Tử Vi' },
  bat: { name: 'Bát Bát', side: 'bt', role: 'người dẫn đường Bát Tự' },
  tu2: { name: 'Tự Tự', side: 'bt', role: 'người bạn Bát Tự' },
};

// ---------- avatars (inline SVG, colour from CSS variables per guide) ----------
/** `decorative`: next to a visible name (the chat button, its header), so screen readers skip it. */
export function avatar(id, size = 52, decorative = false) {
  const acc = {
    tu1: '<path class="gd-acc" d="M32 5l2.6 5.6 6 .7-4.5 4.1 1.2 6L32 18.5 26.7 21.4l1.2-6-4.5-4.1 6-.7z"/>',
    vi: '<path class="gd-acc" d="M20 13a8 8 0 1 0 10 9 6.5 6.5 0 0 1-10-9z"/><circle class="gd-acc" cx="44" cy="15" r="2.6"/>',
    bat: '<path class="gd-tuft" d="M24 14c-3-6 1-9 4-8M33 12c-1-6 4-8 7-5" fill="none" stroke-width="3" stroke-linecap="round"/><text x="32" y="60" class="gd-glyph" text-anchor="middle" lang="zh">八</text>',
    tu2: '<circle class="gd-glass" cx="25" cy="34" r="6.4"/><circle class="gd-glass" cx="39" cy="34" r="6.4"/><path class="gd-glass" d="M31.4 34h1.2"/><text x="32" y="60" class="gd-glyph" text-anchor="middle" lang="zh">字</text>',
  }[id];
  return `<svg class="gd-av gd-${id}" width="${size}" height="${size}" viewBox="0 0 64 64" ${decorative ? 'aria-hidden="true" focusable="false"' : `role="img" aria-label="${GUIDES[id].name}"`}><circle class="gd-face" cx="32" cy="34" r="22"/>${acc}
    <g class="gd-eyes"><circle class="gd-eye" cx="25" cy="34" r="2.6"/><circle class="gd-eye" cx="39" cy="34" r="2.6"/></g>
    <ellipse class="gd-cheek" cx="20.5" cy="41" rx="3.4" ry="2.2"/><ellipse class="gd-cheek" cx="43.5" cy="41" rx="3.4" ry="2.2"/>
    <path class="gd-mouth" d="M27 43q5 5 10 0" fill="none" stroke-width="2" stroke-linecap="round"/></svg>`;
}
