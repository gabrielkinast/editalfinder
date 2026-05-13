import { useMemo } from 'react';

/** Destaca substring case-insensitive (busca atual). Tokens vêm já normalizados em minúsculas sem acento. */
export default function HighlightedText({ text, tokensNorm }) {
  const nodes = useMemo(() => buildParts(String(text ?? ''), tokensNorm || []), [text, tokensNorm]);

  if (!tokensNorm?.length || !text) {
    return <>{text ?? ''}</>;
  }

  return (
    <>
      {nodes.map((n, i) =>
        n.mark ? (
          <mark key={i} className="edital-search-hit">
            {n.s}
          </mark>
        ) : (
          <span key={i}>{n.s}</span>
        ),
      )}
    </>
  );
}

function normalizeForMatch(ch) {
  return String(ch)
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
}

function buildParts(original, tokensNormSet) {
  const s = original;
  if (!s) return [];

  /** Encontra próximo índice de qualquer token a partir de `start` (fold case). */
  const findNext = (start) => {
    let best = -1;
    let len = 0;
    let tok = '';

    const sliceFold = normalizeForMatch(s.slice(start));

    for (const t of tokensNormSet) {
      if (!t) continue;
      const idx = sliceFold.indexOf(t);
      if (idx >= 0 && (best < 0 || idx < best || (idx === best && t.length > len))) {
        best = idx;
        len = t.length;
        tok = t;
      }
    }

    return best >= 0 ? { idx: start + best, len } : null;
  };

  const out = [];
  let pos = 0;

  while (pos < s.length) {
    const hit = findNext(pos);
    if (!hit) {
      out.push({ s: s.slice(pos), mark: false });
      break;
    }
    const { idx, len } = hit;

    if (idx > pos) {
      out.push({ s: s.slice(pos, idx), mark: false });
    }

    out.push({
      s: s.slice(idx, idx + len),
      mark: true,
    });

    pos = idx + len;
    if (!len) pos++;
  }

  return out;
}
