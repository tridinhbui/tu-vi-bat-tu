// Micro-planning (prose plan §4.5): deterministic variant choice with report-wide memory. Same chart + same library = same text.
//   - a variant list is entered at hash(seed|key) and the first variant whose two-word opener is not among the last four openers wins;
//   - a connective is never reused within a chapter;
//   - the person is named by the frame first, then by rotating anaphors, never the same one twice in a row.
import type { Connective, ConnRel, Frames } from './types.ts';

export function fnv(s: string): number { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
const opener = (s: string) => s.replace(/^\{[^}]+\}\s*/, '').split(/\s+/).slice(0, 2).join(' ').toLowerCase();

export class Micro {
  private openers: string[] = []; private usedConn = new Set<string>(); private usedVar = new Set<string>(); private lastSubj: string[] = [];
  readonly seed: string; private conns: Connective[]; private frames: Frames;
  constructor(seed: string, conns: Connective[], frames: Frames) { this.seed = seed; this.conns = conns; this.frames = frames; }

  pick(key: string, variants: string[]): string {
    if (!variants.length) return '';
    const start = fnv(`${this.seed}|${key}`) % variants.length;
    for (let i = 0; i < variants.length; i++) {
      const v = variants[(start + i) % variants.length];
      if (this.usedVar.has(v) || this.openers.slice(-4).includes(opener(v))) continue;
      this.usedVar.add(v);
      return v;
    }
    const v = variants[start];
    this.usedVar.add(v);
    return v;
  }
  /** Records a finished sentence's opener so the next picks avoid it. */
  said(sentence: string) { this.openers.push(opener(sentence)); }

  conn(rel: ConnRel, key: string, pos: 'initial' | 'medial' = 'initial'): string {
    const xs = this.conns.filter(c => c.rel === rel && c.pos === pos && !this.usedConn.has(c.id));
    if (!xs.length) return '';
    const c = xs[fnv(`${this.seed}|conn|${key}`) % xs.length];
    this.usedConn.add(c.id);
    return c.text;
  }

  /** The next anaphor for the person (or, given a list, for the other people a chapter speaks of), never one of the last two. */
  subject(list?: string[]): string {
    const all = list ?? this.frames.subject.next;
    // never one of the last two; with a two-item list that leaves at least the one not used just now
    const xs = all.filter(x => !this.lastSubj.includes(x)).length ? all.filter(x => !this.lastSubj.includes(x)) : all.filter(x => x !== this.lastSubj[0]);
    const s = xs[fnv(`${this.seed}|subj|${this.openers.length}`) % xs.length];
    this.lastSubj = [s, ...this.lastSubj].slice(0, 2);
    return s;
  }
}

/** Sentence surface: capital first letter, single spaces, one final period, no space before punctuation. */
export function finish(s: string): string {
  let t = s.replace(/\s+/g, ' ').replace(/\s+([,.;:])/g, '$1').replace(/[,;:\s]+$/, '').trim();
  if (!/[.!?]$/.test(t)) t += '.';
  return t.charAt(0).toLocaleUpperCase('vi') + t.slice(1);
}
export const lowerFirst = (s: string) => s.charAt(0).toLocaleLowerCase('vi') + s.slice(1);
/** A connective glued to a following clause: 'Tuy nhiên,' + 'họ …' / 'Nhưng' + 'họ …'. */
export const lead = (conn: string, clause: string) => conn ? `${conn} ${lowerFirst(clause)}` : clause;
