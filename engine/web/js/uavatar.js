// The signed-in user's picture: the Google profile photo saved at sign-in (users.picture), else the first letter of the given name.
// The photo is loaded first and swapped in only when it arrives, so a blocked or expired link leaves the initial in place.
const GOOGLE_PHOTO = /^https:\/\/[a-z0-9-]+\.googleusercontent\.com\//;

export const initialOf = u => ((u?.name || u?.email || '').split(' ').slice(-1)[0] || '?').charAt(0).toLocaleUpperCase('vi');

/** el: a .uav element; u: {name, email, picture}. */
export function paintAvatar(el, u) {
  if (!el) return;
  el.classList.remove('has-img');
  el.textContent = initialOf(u);
  const src = u?.picture || '';
  if (!GOOGLE_PHOTO.test(src)) return;
  const img = new Image();
  img.alt = '';
  img.decoding = 'async';
  img.referrerPolicy = 'no-referrer';               // Google refuses some photo requests that carry a referrer
  img.onload = () => { el.textContent = ''; el.append(img); el.classList.add('has-img'); };
  img.src = src;
}
