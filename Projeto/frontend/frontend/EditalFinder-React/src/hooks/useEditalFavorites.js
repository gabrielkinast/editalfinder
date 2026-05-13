import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  FEATURE_EDITAL_FAVORITOS,
  isSupabaseConfigured,
} from '../config/env';
import { useAuth } from '../contexts/AuthContext';
import { supabase } from '../services/supabaseClient';
import {
  fetchFavoritos,
  toggleFavorito as toggleFavoritoRequest,
  favoritoRowMatchesEdital,
  getEditalNumericoId,
  normalizeEditalLink,
} from '../services/favoritosService';
import { getFavoriteDeadlineSummary } from '../utils/deadlineAlerts';

function backendFavoritosConfigured() {
  return FEATURE_EDITAL_FAVORITOS && isSupabaseConfigured;
}

/**
 * Resolve o id numérico usado em edital_favorito.id_usuario.
 * Produção: só a partir do utilizador em sessão (AuthContext / localStorage).
 * Desenvolvimento: se não houver id no utilizador, usa VITE_DEV_FAVORITOS_USER_ID ou 1.
 */
export function resolveFavoriteUserId(user, hookUserIdOverride) {
  if (hookUserIdOverride != null && hookUserIdOverride !== '') {
    const o = Number(hookUserIdOverride);
    if (Number.isFinite(o) && o > 0) return o;
  }
  const raw = user?.id_usuario;
  if (raw != null && raw !== '' && Number.isFinite(Number(raw)) && Number(raw) > 0) {
    return Number(raw);
  }
  if (import.meta.env.DEV) {
    const d = Number(import.meta.env.VITE_DEV_FAVORITOS_USER_ID);
    return Number.isFinite(d) && d > 0 ? d : 1;
  }
  return null;
}

/**
 * Favoritos persistentes (Supabase) + resumo de alertas de prazo.
 * Requer utilizador com `id_usuario` em produção; sem isso, usa favoritos locais (localStorage) nas páginas.
 */
export function useEditalFavorites(options = {}) {
  const { user } = useAuth();
  const { userId: hookUserIdOverride } = options;

  const favoriteUserId = useMemo(
    () => resolveFavoriteUserId(user, hookUserIdOverride),
    [user, hookUserIdOverride],
  );

  const favoritosRemoteEnabled = useMemo(
    () => backendFavoritosConfigured() && favoriteUserId != null,
    [favoriteUserId],
  );

  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [toggleError, setToggleError] = useState(null);

  useEffect(() => {
    if (!import.meta.env.DEV) return undefined;
    let cancelled = false;
    (async () => {
      const { data: sessWrap } = await supabase.auth.getSession();
      if (cancelled) return;
      console.info('[useEditalFavorites][DEV]', {
        currentUser_id_usuario: user?.id_usuario,
        favoriteUserId,
        favoritosRemoteEnabled,
        FEATURE_EDITAL_FAVORITOS,
        isSupabaseConfigured,
        hasSupabaseSession: !!sessWrap?.session?.user,
        auth_user_id: sessWrap?.session?.user?.id ?? null,
      });
    })();
    return () => {
      cancelled = true;
    };
  }, [user?.id_usuario, favoriteUserId, favoritosRemoteEnabled]);

  const refreshFavorites = useCallback(async () => {
    if (!favoritosRemoteEnabled) {
      setFavorites([]);
      return;
    }
    try {
      const rows = await fetchFavoritos({ id_usuario: favoriteUserId });
      setFavorites(rows);
    } catch (e) {
      setError(e);
      setFavorites([]);
    }
  }, [favoritosRemoteEnabled, favoriteUserId]);

  useEffect(() => {
    let alive = true;
    (async () => {
      if (!favoritosRemoteEnabled) {
        setFavorites([]);
        setLoading(false);
        setError(null);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const rows = await fetchFavoritos({ id_usuario: favoriteUserId });
        if (alive) setFavorites(rows);
      } catch (e) {
        if (alive) {
          setError(e);
          setFavorites([]);
        }
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, [favoritosRemoteEnabled, favoriteUserId]);

  const isFavorite = useCallback(
    (edital) => {
      if (!edital || !favoritosRemoteEnabled) return false;
      return favorites.some((r) => r && r.ativo !== false && favoritoRowMatchesEdital(r, edital));
    },
    [favorites, favoritosRemoteEnabled],
  );

  const clearToggleError = useCallback(() => setToggleError(null), []);

  const toggleFavorite = useCallback(
    async (edital, opts = {}) => {
      if (!favoritosRemoteEnabled || !edital) {
        return { ok: false, skipped: true };
      }
      setToggleError(null);
      const merged = { ...opts };
      const uid = opts.id_usuario ?? opts.userId ?? hookUserIdOverride ?? favoriteUserId;
      if (uid != null) merged.id_usuario = Number(uid);

      const wasFavorite = favorites.some(
        (r) => r && r.ativo !== false && favoritoRowMatchesEdital(r, edital),
      );

      const res = await toggleFavoritoRequest(edital, favorites, merged);

      if (!res.ok) {
        const err = res.error;
        const msg =
          (typeof err === 'object' && err && (err.message || err.hint || err.details)) ||
          String(err || 'toggle_favorito_failed');
        setToggleError(msg);
        if (import.meta.env.DEV) {
          console.warn('[useEditalFavorites] toggle falhou', {
            ok: res.ok,
            id_edital: getEditalNumericoId(edital),
            tem_link: Boolean(normalizeEditalLink(edital)),
            wasFavorite,
            code: typeof err === 'object' && err ? err.code : undefined,
            message: typeof err === 'object' && err ? err.message : undefined,
            details: typeof err === 'object' && err ? err.details : undefined,
            hint: typeof err === 'object' && err ? err.hint : undefined,
          });
          if (err && typeof err === 'object') console.error('[useEditalFavorites] toggle erro bruto', err);
        }
      } else {
        setToggleError(null);
        if (import.meta.env.DEV) {
          console.info('[useEditalFavorites] toggle ok', {
            id_edital: getEditalNumericoId(edital),
            wasFavorite,
            agora_favorito: !wasFavorite,
          });
        }
      }

      await refreshFavorites();
      return res;
    },
    [favorites, favoritosRemoteEnabled, favoriteUserId, hookUserIdOverride, refreshFavorites],
  );

  const favoriteAlertsSummary = useMemo(() => getFavoriteDeadlineSummary(favorites), [favorites]);

  return useMemo(
    () => ({
      favorites,
      loading,
      error,
      toggleError,
      clearToggleError,
      isFavorite,
      toggleFavorite,
      refreshFavorites,
      favoriteAlertsSummary,
      favoritosRemoteEnabled,
      favoriteUserId,
    }),
    [
      favorites,
      loading,
      error,
      toggleError,
      clearToggleError,
      isFavorite,
      toggleFavorite,
      refreshFavorites,
      favoriteAlertsSummary,
      favoritosRemoteEnabled,
      favoriteUserId,
    ],
  );
}
