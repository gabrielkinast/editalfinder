import { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { supabase, isSupabaseConfigured } from '../services/api';
import { authService } from '../services/authService';
import {
  shouldDeferAuthBootstrap,
  isAuthCallbackHandling,
} from '../auth/authCallbackCoordinator';

const AuthContext = createContext({});

const BOOTSTRAP_TIMEOUT_MS = 9000;

function withTimeout(promise, ms, label) {
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      setTimeout(() => reject(new Error(`${label} timeout (${ms}ms)`)), ms);
    }),
  ]);
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const initDone = useRef(false);

  const setAppUser = useCallback((appUser) => {
    setUser(appUser ?? null);
    if (appUser) authService.persistProfileCache(appUser);
    else authService.clearProfileCache();
  }, []);

  useEffect(() => {
    let cancelled = false;
    let authListener = null;

    async function applySessionToUser(session) {
      if (!session?.user?.id) return null;
      let row = await authService.fetchProfileByAuthUserId(session.user.id);
      if (!row) {
        const ensured = await authService.ensureInternalProfileFromAuthUser(session.user);
        if (ensured) {
          authService.persistProfileCache(ensured);
          return ensured;
        }
        await authService.logout();
        return null;
      }
      const u = authService.buildAppUser(row, session.user.id);
      authService.persistProfileCache(u);
      return u;
    }

    async function initFromSupabase() {
      const session = await authService.getCurrentSession();
      if (cancelled) return;
      if (session?.user?.id) {
        const u = await applySessionToUser(session);
        if (!cancelled) setUser(u);
        return;
      }

      if (import.meta.env.DEV) {
        const legacy = authService.hydrateDevLegacyFromCache();
        if (!cancelled && legacy) {
          setUser(legacy);
          return;
        }
      }

      const stale = authService.getUser();
      if (stale?.auth_user_id) {
        authService.clearProfileCache();
      }
      if (!cancelled) setUser(null);
    }

    async function bootstrap() {
      if (shouldDeferAuthBootstrap()) {
        initDone.current = true;
        if (!cancelled) setLoading(false);
        return;
      }

      setLoading(true);
      try {
        if (isSupabaseConfigured) {
          await withTimeout(initFromSupabase(), BOOTSTRAP_TIMEOUT_MS, 'auth bootstrap');
        } else if (import.meta.env.DEV) {
          const legacy = authService.hydrateDevLegacyFromCache();
          if (!cancelled && legacy) setUser(legacy);
          else if (!cancelled) setUser(null);
        } else if (!cancelled) {
          setUser(null);
        }
      } catch (e) {
        console.warn('[Auth] init', e);
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) {
          initDone.current = true;
          setLoading(false);
        }
      }
    }

    bootstrap();

    if (isSupabaseConfigured) {
      const { data } = supabase.auth.onAuthStateChange(async (event, session) => {
        if (!initDone.current) return;
        if (isAuthCallbackHandling() || shouldDeferAuthBootstrap()) {
          return;
        }

        if (event === 'SIGNED_OUT') {
          setUser(null);
          authService.clearProfileCache();
          return;
        }

        if (event === 'SIGNED_IN' || event === 'TOKEN_REFRESHED' || event === 'USER_UPDATED') {
          if (!session?.user?.id) {
            setUser(null);
            return;
          }
          if (event === 'TOKEN_REFRESHED' || event === 'USER_UPDATED') {
            const row = await authService.fetchProfileByAuthUserId(session.user.id);
            if (row) {
              const u = authService.buildAppUser(row, session.user.id);
              authService.persistProfileCache(u);
              setUser(u);
            }
            return;
          }
          const u = await applySessionToUser(session);
          setUser(u);
        }
      });
      authListener = data.subscription;
    }

    return () => {
      cancelled = true;
      authListener?.unsubscribe();
    };
  }, []);

  const login = async (email, password) => {
    const userData = await authService.login(email, password);
    setUser(userData);
    return userData;
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const register = async (payload) => {
    const result = await authService.registerUser(payload);
    if (result?.status === 'complete') {
      setUser(result.user);
    }
    return result;
  };

  const onCallbackRoute = shouldDeferAuthBootstrap();
  const showGlobalLoader = loading && !onCallbackRoute;

  return (
    <AuthContext.Provider
      value={{ user, login, register, logout, setAppUser, authenticated: !!user, loading }}
    >
      {showGlobalLoader ? (
        <div
          style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: 'Inter, system-ui, sans-serif',
            color: '#333',
            background: '#fff',
          }}
        >
          Carregando…
        </div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};
