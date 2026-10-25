// The six-line figure of a quẻ. Lines are buttons (hào Đầu at the bottom), so each hào can be opened; a dương line is one bar, an âm line
// two bars with a gap, and a moving line can turn into its changed form by animating the gap (CSS, no script timing).
import { esc } from './util.js';

const POS = ['Đầu', 'Hai', 'Ba', 'Tư', 'Năm', 'Trên'];
export const haoName = (p, yang) => `${yang ? 'Chín' : 'Sáu'} ${POS[p - 1]}`;

/** lines: hào 1..6 as 1 / 0. opts: moving (positions), values (6/7/8/9, marks ○ / ×),
 *  interactive (lines are buttons), cls (extra class), label (aria label of the figure), roles ({upper, lower}: a word beside each quái). */
export function figure(lines, opts = {}) {
  const { moving = [], values = null, interactive = false, cls = '', label = '', roles = null } = opts;
  const rows = [];
  for (let p = 6; p >= 1; p--) {
    const has = p <= lines.length;
    const yang = has && lines[p - 1] === 1;
    const mv = moving.includes(p);
    const v = values?.[p - 1];
    const mark = v === 9 ? '○' : v === 6 ? '×' : '';
    const name = has ? `Hào ${haoName(p, yang)}${mv ? ', động' : ''}` : `Hào ${POS[p - 1]}, chưa gieo`;
    const tag = interactive && has ? 'button' : 'div';
    const attrs = interactive && has ? ` type="button" data-hao="${p}" aria-label="${esc(name)}"` : ` aria-hidden="true"`;
    rows.push(`<${tag} class="hx-line${has ? (yang ? ' yang' : ' yin') : ' empty'}${mv ? ' mv' : ''}" data-p="${p}"${attrs}>`
      + `<span class="hx-bar"><i></i><i></i></span><span class="hx-mark">${mark}</span></${tag}>`);
    if (p === 4 && roles) rows.push(`<span class="hx-sep" aria-hidden="true"></span>`);
  }
  const roleTags = roles ? `<span class="hx-role up">${esc(roles.upper || '')}</span><span class="hx-role lo">${esc(roles.lower || '')}</span>` : '';
  return `<div class="hx ${cls}" role="group" aria-label="${esc(label)}">${rows.join('')}${roleTags}</div>`;
}

/** Turns the moving lines of a figure into their changed form (a dương line opens into âm, an âm line closes into dương). */
export function morph(el, moving) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  moving.forEach((p, i) => {
    const line = el.querySelector(`.hx-line[data-p="${p}"]`);
    if (!line) return;
    const go = () => { line.classList.toggle('yang'); line.classList.toggle('yin'); line.classList.add('changed'); };
    reduce ? go() : setTimeout(go, 250 + i * 220);
  });
}
