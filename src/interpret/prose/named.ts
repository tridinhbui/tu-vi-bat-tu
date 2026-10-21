// Stars named the way a reader expects them (prose-style plan S3): "Cự Môn (Hãm Địa)", "Kình Dương (Đắc Địa)". The brightness shown is the
// one the dignity tables give for this palace, and only when the cell is VERIFIED (dignity_status, with its page); a star without a checked
// cell is named bare. Nothing here is a reading: it names chart positions.
import type { ChartInput, Palace } from '../types.ts';
import { CAT, SAT } from '../kg/atoms.ts';

export const DIG_TITLE: Record<string, string> = { 'miếu': 'Miếu Địa', 'vượng': 'Vượng Địa', 'đắc': 'Đắc Địa', 'lợi': 'Lợi Địa', 'bình': 'Bình Hòa', 'hãm': 'Hãm Địa' };
const HOA = ['Hóa Lộc', 'Hóa Quyền', 'Hóa Khoa', 'Hóa Kỵ'];
type Dig = { status: string; value?: string; locator?: string };

export const joinVi = (xs: string[]) => xs.length <= 1 ? (xs[0] ?? '') : xs.slice(0, -1).join(', ') + ' và ' + xs[xs.length - 1];

/** The checked brightness of a star in a palace, with the page it comes from; null when the cell is not VERIFIED. */
export function dignityOf(p: Palace, star: string): { value: string; cite?: string } | null {
  const d = (p as Palace & { dignity_status?: Record<string, Dig> }).dignity_status?.[star];
  return d?.status === 'VERIFIED' && d.value ? { value: d.value, cite: d.locator } : null;
}
/** "Cự Môn (Hãm Địa)", or the bare name when the brightness is not checked. */
export function named(p: Palace, star: string): string {
  const d = dignityOf(p, star);
  return d && DIG_TITLE[d.value] ? `${star} (${DIG_TITLE[d.value]})` : star;
}
/** The natal Hóa a star carries ("hóa Lộc"), when it stands in this palace. */
export function hoaOn(chart: ChartInput, p: Palace, star: string): string[] {
  return HOA.filter(h => chart.tu_hoa[h]?.star === star && chart.tu_hoa[h]?.branch === p.branch_index).map(h => h.replace(/^Hóa\s+/, 'hóa '));
}

export interface PalaceConfig {
  /** chính tinh, named with brightness and their Hóa: "Cự Môn (Hãm Địa) hóa Lộc" */
  majors: string[];
  /** the six sát, the six cát tinh, Lộc Tồn and Thiên Mã standing in the palace, named with brightness */
  sat: string[]; cat: string[]; other: string[];
  tuanTriet: string[];
  /** pages of the brightness cells used */
  cites: string[];
}
const NOTABLE = ['Lộc Tồn', 'Thiên Mã'];
export function palaceConfig(chart: ChartInput, p: Palace): PalaceConfig {
  const cites = new Set<string>();
  const nm = (s: string) => { const d = dignityOf(p, s); if (d?.cite) cites.add(d.cite); return named(p, s); };
  const majors = p.major_stars.map(s => [nm(s), ...hoaOn(chart, p, s)].join(' '));
  const minorHoa = (s: string) => [nm(s), ...hoaOn(chart, p, s)].join(' ');
  return {
    majors,
    sat: SAT.filter(s => p.stars.includes(s)).map(minorHoa),
    cat: CAT.filter(s => p.stars.includes(s)).map(minorHoa),
    other: NOTABLE.filter(s => p.stars.includes(s)).map(minorHoa),
    tuanTriet: [p.tuan && 'Tuần', p.triet && 'Triệt'].filter(Boolean) as string[],
    cites: [...cites].sort(),
  };
}
/** One clause naming a palace's configuration: "Cự Môn (Hãm Địa) hóa Lộc tọa thủ, cùng Kình Dương (Đắc Địa) và Hữu Bật (Đắc Địa); Tuần án ngữ".
 *  For a palace without chính tinh, the stars of the opposite palace are named as borrowed. */
export function configClause(chart: ChartInput, p: Palace): { text: string; cites: string[] } {
  const c = palaceConfig(chart, p);
  const with_ = [...c.sat, ...c.cat, ...c.other];
  let head: string;
  if (c.majors.length) head = `${joinVi(c.majors)} ${c.majors.length > 1 ? 'đồng cung' : 'tọa thủ'}`;
  else {
    const opp = chart.palaces.find(x => x.branch_index === (p.branch_index + 6) % 12);
    const borrowed = opp?.major_stars.map(s => named(opp, s)) ?? [];
    head = borrowed.length ? `vô chính diệu, mượn ${joinVi(borrowed)} ở cung đối diện` : 'vô chính diệu';
  }
  const tail = with_.length ? `${c.majors.length ? ', cùng' : '; trong cung có'} ${joinVi(with_)}` : '';
  const tt = c.tuanTriet.length ? `; ${joinVi(c.tuanTriet)} án ngữ` : '';
  return { text: `${head}${tail}${tt}`, cites: c.cites };
}
