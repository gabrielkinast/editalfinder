import { scientificButtonClick } from './scientificButtonClick';
import { logScientificWorkspace } from './scientificWorkspaceLog';
import { showScientificToastPayload, SCIENTIFIC_TOAST_MESSAGES } from './showScientificToast';

const SECTION_TOAST_INFO = {
  'scientific-route': SCIENTIFIC_TOAST_MESSAGES.scrollRota,
  'scientific-interests': SCIENTIFIC_TOAST_MESSAGES.scrollInteresses,
  'scientific-projects': SCIENTIFIC_TOAST_MESSAGES.scrollProjetos,
  'scientific-study-path': SCIENTIFIC_TOAST_MESSAGES.scrollTrilha,
  'scientific-notebook': SCIENTIFIC_TOAST_MESSAGES.scrollCaderno,
  'scientific-feed': SCIENTIFIC_TOAST_MESSAGES.scrollFeed,
};

const SECTION_DISPLAY_NAMES = {
  'scientific-route': 'Minha rota',
  'scientific-interests': 'Interesses',
  'scientific-projects': 'Ideias de projeto',
  'scientific-study-path': 'Trilha de estudo',
  'scientific-notebook': 'Caderno',
  'scientific-feed': 'Feed',
};

const HIGHLIGHT_MS = 1400;
const SCROLL_VERIFY_MS = 450;
const SCROLL_POSITION_TOLERANCE = 48;

/** @param {Element | null | undefined} el */
function isScrollableElement(el) {
  if (!el || el === document.body) return false;
  const style = window.getComputedStyle(el);
  const oy = style.overflowY;
  const o = style.overflow;
  const scrollableOverflow = /(auto|scroll|overlay)/.test(oy) || /(auto|scroll|overlay)/.test(o);
  return scrollableOverflow && el.scrollHeight > el.clientHeight + 1;
}

/** @param {Element} el */
export function getScrollParent(el) {
  let parent = el.parentElement;
  while (parent) {
    if (isScrollableElement(parent)) return parent;
    if (parent === document.body) break;
    parent = parent.parentElement;
  }
  return document.scrollingElement || document.documentElement;
}

/** @param {Element | null | undefined} el */
function isDocumentScrollContainer(el) {
  if (!el) return true;
  return (
    el === document.body ||
    el === document.documentElement ||
    el === document.scrollingElement
  );
}

/** Altura combinada do header principal + nav sticky + margem. */
export function getScientificStickyOffset() {
  const header = document.querySelector('.header');
  const nav = document.querySelector('.scientific-section-nav');
  const headerH = header?.getBoundingClientRect?.().height ?? header?.offsetHeight ?? 56;
  const navH = nav?.getBoundingClientRect?.().height ?? nav?.offsetHeight ?? 48;
  const measured = Math.round(headerH + navH + 16);
  const page = document.querySelector('.scientific-workspace-page');
  const fromCss = page
    ? parseInt(getComputedStyle(page).getPropertyValue('--scientific-scroll-offset'), 10)
    : NaN;
  if (Number.isFinite(fromCss) && fromCss > 0) {
    return Math.max(measured, fromCss);
  }
  return measured;
}

function getDocumentScrollTop() {
  return (
    window.pageYOffset ||
    document.documentElement.scrollTop ||
    document.body.scrollTop ||
    0
  );
}

/** @param {Element} scrollParent */
function collectScrollParentChain(target) {
  const chain = [];
  let parent = target?.parentElement;
  while (parent) {
    if (isScrollableElement(parent)) {
      chain.push({
        tag: parent.tagName,
        className: String(parent.className || '').slice(0, 80),
      });
    }
    parent = parent.parentElement;
  }
  return chain;
}

/**
 * @param {string} targetId
 * @param {Element} target
 * @param {number} offset
 */
function logScrollDiagnostics(targetId, target, offset) {
  if (!import.meta.env.DEV) return;
  try {
    const scrollParent = getScrollParent(target);
    const rect = target.getBoundingClientRect();
    logScientificWorkspace('scroll_diagnostics', {
      targetId,
      targetExists: true,
      windowScrollY: getDocumentScrollTop(),
      documentScrollHeight: document.documentElement.scrollHeight,
      viewportHeight: window.innerHeight,
      scrollParents: collectScrollParentChain(target),
      targetTop: Math.round(rect.top),
      nearestScrollParentClass: isDocumentScrollContainer(scrollParent)
        ? 'document'
        : String(scrollParent.className || scrollParent.tagName).slice(0, 80),
      stickyOffset: offset,
      computedScrollTop: Math.round(rect.top + getDocumentScrollTop() - offset),
    });
  } catch {
    /* dev only */
  }
}

/**
 * @param {Element} target
 * @param {number} offset
 * @param {ScrollBehavior} behavior
 * @returns {number} scrollTop aplicado
 */
function performScroll(target, offset, behavior = 'smooth') {
  const scrollParent = getScrollParent(target);
  const useDocument = isDocumentScrollContainer(scrollParent);

  if (useDocument) {
    const scrollTop = getDocumentScrollTop();
    const top = Math.max(0, target.getBoundingClientRect().top + scrollTop - offset);
    window.scrollTo({ top, behavior });
    const scrollingEl = document.scrollingElement;
    if (scrollingEl && scrollingEl.scrollTo) {
      scrollingEl.scrollTo({ top, behavior });
    }
    return top;
  }

  const parentRect = scrollParent.getBoundingClientRect();
  const targetRect = target.getBoundingClientRect();
  const top = Math.max(0, scrollParent.scrollTop + targetRect.top - parentRect.top - offset);
  scrollParent.scrollTo({ top, behavior });
  return top;
}

/** @param {Element} target */
function scrollIntoViewFallback(target) {
  try {
    target.scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' });
  } catch {
    try {
      target.scrollIntoView(true);
    } catch {
      /* ignore */
    }
  }
}

/** @param {Element} target */
function verifyScrollPosition(target, offset) {
  const rect = target.getBoundingClientRect();
  return rect.top >= offset - SCROLL_POSITION_TOLERANCE && rect.top <= offset + SCROLL_POSITION_TOLERANCE;
}

export function highlightScientificSection(sectionId) {
  const el = document.getElementById(sectionId);
  if (!el) return;
  el.classList.add('scientific-section-highlight');
  window.setTimeout(() => {
    el.classList.remove('scientific-section-highlight');
  }, HIGHLIGHT_MS);
}

function showScrollToast(meta, sectionId, type, message) {
  if (!meta.onToast || !message) return;
  meta.onToast(showScientificToastPayload(message, type));
  if (type === 'info') {
    window.setTimeout(() => meta.onToast?.(null), 1600);
  } else {
    window.setTimeout(() => meta.onToast?.(null), 2200);
  }
}

/**
 * Navegação interna unificada do Workspace Científico.
 * @param {string} sectionId
 * @param {{ source?: string, label?: string, onToast?: (payload: { message: string, type: string } | null) => void }} [meta]
 * @returns {boolean}
 */
export function scientificScrollToSection(sectionId, meta = {}) {
  scientificButtonClick({
    action: meta.source || 'scroll_to_section',
    section: sectionId,
    label: meta.label,
  });

  const target = document.getElementById(sectionId);
  const displayName =
    meta.label || SECTION_DISPLAY_NAMES[sectionId] || sectionId;

  if (!target) {
    logScientificWorkspace('section_scroll_missing', { section: sectionId });
    showScrollToast(
      meta,
      sectionId,
      'warning',
      `Não encontrei a seção ${displayName}`,
    );
    return false;
  }

  const offset = getScientificStickyOffset();
  logScrollDiagnostics(sectionId, target, offset);

  performScroll(target, offset, 'smooth');

  window.requestAnimationFrame(() => {
    highlightScientificSection(sectionId);
  });

  window.setTimeout(() => {
    if (!verifyScrollPosition(target, offset)) {
      scrollIntoViewFallback(target);
      logScientificWorkspace('section_scroll_fallback', { section: sectionId });
    }
  }, SCROLL_VERIFY_MS);

  logScientificWorkspace('section_scroll_success', { section: sectionId });

  const toastMsg = SECTION_TOAST_INFO[sectionId];
  if (toastMsg) {
    showScrollToast(meta, sectionId, 'info', toastMsg);
  }

  return true;
}

/**
 * Alias para CTAs — mesmo comportamento que scientificScrollToSection.
 */
export function navigateScientificSection(sectionId, meta = {}) {
  return scientificScrollToSection(sectionId, meta);
}
