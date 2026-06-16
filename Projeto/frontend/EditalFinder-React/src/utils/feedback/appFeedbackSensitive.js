const SENSITIVE_KEY_PATTERNS = [
  'access_token',
  'refresh_token',
  'authorization',
  'apikey',
  'api_key',
  'supabase_key',
  'password',
  'senha',
  'secret',
  'session',
  'jwt',
  'bearer',
];

const SENSITIVE_INLINE_PATTERN =
  /(access_token|refresh_token|authorization|apikey|api_key|supabase_key|password|senha|secret|session|jwt)\s*[=:]/i;

const BEARER_PATTERN = /Bearer\s+[A-Za-z0-9._-]+/gi;

export function redactSensitiveFeedbackValue(key, value) {
  const normalizedKey = String(key || '').toLowerCase();

  if (SENSITIVE_KEY_PATTERNS.some((pattern) => normalizedKey.includes(pattern))) {
    return '[REDACTED]';
  }

  if (typeof value === 'string') {
    const out = value.replace(BEARER_PATTERN, 'Bearer [REDACTED]');
    if (SENSITIVE_INLINE_PATTERN.test(out)) {
      return '[REDACTED]';
    }
    return out;
  }

  return value;
}

/**
 * Redige recursivamente objetos (metadata, platform_context, extras).
 */
export function redactSensitiveFeedbackObject(input, depth = 0) {
  if (depth > 8) return '[REDACTED]';
  if (input == null) return input;

  if (Array.isArray(input)) {
    return input.map((item) => redactSensitiveFeedbackObject(item, depth + 1));
  }

  if (typeof input !== 'object') {
    if (typeof input === 'string') {
      return redactSensitiveFeedbackValue('', input);
    }
    return input;
  }

  const out = {};
  for (const [key, value] of Object.entries(input)) {
    if (value != null && typeof value === 'object') {
      out[key] = redactSensitiveFeedbackObject(value, depth + 1);
    } else {
      out[key] = redactSensitiveFeedbackValue(key, value);
    }
  }
  return out;
}

/** Payload seguro para assunto/corpo do mailto. */
export function sanitizePayloadForSupportEmail(payload = {}) {
  const safe = { ...payload };

  if (safe.platform_context) {
    safe.platform_context = redactSensitiveFeedbackObject(safe.platform_context);
  }
  if (safe.metadata) {
    safe.metadata = redactSensitiveFeedbackObject(safe.metadata);
  }
  if (safe.extras) {
    safe.extras = redactSensitiveFeedbackObject(safe.extras);
  }

  safe.user_agent = redactSensitiveFeedbackValue('user_agent', safe.user_agent);
  safe.mensagem_erro = redactSensitiveFeedbackValue('mensagem_erro', safe.mensagem_erro);
  safe.stack_erro = redactSensitiveFeedbackValue('stack_erro', safe.stack_erro);
  safe.descricao = redactSensitiveFeedbackValue('descricao', safe.descricao);
  safe.comentario = redactSensitiveFeedbackValue('comentario', safe.comentario);

  return safe;
}
