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
import { resolveAppUserId } from '../utils/appUserId';

const LOGIN_MESSAGE = 'Entre na sua conta para favoritar editais.';

function backendFavoritosConfigured() {
  return FEATURE_EDITAL_FAVORITOS && isSupabaseConfigured;
}

/** @deprecated Preferir resolveAppUserId — mantido para compatibilidade. */
export function resolveFavoriteUserId(user, hookUserIdOverride) {
  return resolveAppUserId(user, hookUserIdOverride);
}

/**
 * Favoritos persistentes (Supabase) + resumo de alertas de prazo.
 */
export function useEditalFavorites(options = {}) {
  const { user, loading: authLoading } = useAuth();
  const { userId: hookUserIdOverride } = options;

  const favoriteUserId = useMemo(() => {
    if (authLoading) return null;
    return resolveFavoriteUserId(user, hookUserIdOverride);
  }, [user, hookUserIdOverride, authLoading]);

  const favoritosRemoteEnabled = useMemo(
    () => backendFavoritosConfigured() && favoriteUserId != null,
    [favoriteUserId],
  );

  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [toggleError, setToggleError] = useState(null);
  const [optimisticKeys, setOptimisticKeys] = useState(() => new Set());

  const editalFavoriteKey = useCallback((edital) => {
    const id = getEditalNumericoId(edital);
    const link = normalizeEditalLink(edital);
    if (id != null) return `id:${id}`;
    if (link) return `link:${link}`;
    return edital?.id ? String(edital.id) : null;
  }, []);

  useEffect(() => {
    if (!import.meta.env.DEV || authLoading) return undefined;
    let cancelled = false;
    (async () => {
      const { data: sessWrap } = await supabase.auth.getSession();
      if (cancelled) return;
      console.info('[favoritos] hook', {
        appUser_id_usuario: user?.id_usuario ?? null,
        favoriteUserId,
        auth_user_id: sessWrap?.session?.user?.id ?? user?.auth_user_id ?? null,
        favoritosRemoteEnabled,
        authLoading,
      });
    })();
    return () => {
      cancelled = true;
    };
  }, [user?.id_usuario, user?.auth_user_id, favoriteUserId, favoritosRemoteEnabled, authLoading]);

  const refreshFavorites = useCallback(async () => {
    if (!favoritosRemoteEnabled) {
      setFavorites([]);
      return;
    }
    try {
      const rows = await fetchFavoritos({
        id_usuario: favoriteUserId,
        auth_user_id: user?.auth_user_id,
      });
      setFavorites(rows);
      setOptimisticKeys(new Set());
    } catch (e) {
      setError(e);
      setFavorites([]);
    }
  }, [favoritosRemoteEnabled, favoriteUserId, user?.auth_user_id]);

  useEffect(() => {
    let alive = true;
    (async () => {
      if (authLoading) {
        setLoading(true);
        return;
      }
      if (!favoritosRemoteEnabled) {
        setFavorites([]);
        setLoading(false);
        setError(null);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const rows = await fetchFavoritos({
          id_usuario: favoriteUserId,
          auth_user_id: user?.auth_user_id,
        });
        if (alive) {
          setFavorites(rows);
          setOptimisticKeys(new Set());
        }
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
  }, [favoritosRemoteEnabled, favoriteUserId, user?.auth_user_id, authLoading]);

  const isFavorite = useCallback(
    (edital) => {
      if (!edital || !favoritosRemoteEnabled) return false;
      const key = editalFavoriteKey(edital);
      if (key && optimisticKeys.has(key)) return true;
      return favorites.some((r) => r && r.ativo !== false && favoritoRowMatchesEdital(r, edital));
    },
    [favorites, favoritosRemoteEnabled, optimisticKeys, editalFavoriteKey],
  );

  const clearToggleError = useCallback(() => setToggleError(null), []);

  const toggleFavorite = useCallback(
    async (edital, opts = {}) => {
      if (!edital) return { ok: false, skipped: true };
      if (!favoritosRemoteEnabled || favoriteUserId == null) {
        return {
          ok: false,
          skipped: true,
          needsLogin: true,
          message: LOGIN_MESSAGE,
        };
      }

      setToggleError(null);
      const key = editalFavoriteKey(edital);
      const wasFavorite = favorites.some(
        (r) => r && r.ativo !== false && favoritoRowMatchesEdital(r, edital),
      );

      if (key) {
        setOptimisticKeys((prev) => {
          const next = new Set(prev);
          if (wasFavorite) next.delete(key);
          else next.add(key);
          return next;
        });
      }

      const merged = {
        ...opts,
        id_usuario: favoriteUserId,
        auth_user_id: user?.auth_user_id ?? opts.auth_user_id,
        contexto: opts.contexto ?? 'editais',
      };

      const res = await toggleFavoritoRequest(edital, favorites, merged);

      if (!res.ok) {
        if (key) {
          setOptimisticKeys((prev) => {
            const next = new Set(prev);
            if (wasFavorite) next.add(key);
            else next.delete(key);
            return next;
          });
        }
        const err = res.error;
        const msg =
          res.message ||
          (typeof err === 'object' && err && (err.message || err.hint || err.details)) ||
          String(err || 'Não foi possível atualizar favoritos.');
        setToggleError(msg);
      } else {
        setToggleError(null);
      }

      await refreshFavorites();
      return res;
    },
    [
      favorites,
      favoritosRemoteEnabled,
      favoriteUserId,
      user?.auth_user_id,
      refreshFavorites,
      editalFavoriteKey,
    ],
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
      needsLoginForFavorites: backendFavoritosConfigured() && !authLoading && favoriteUserId == null,
      loginMessage: LOGIN_MESSAGE,
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
      authLoading,
    ],
  );
}
