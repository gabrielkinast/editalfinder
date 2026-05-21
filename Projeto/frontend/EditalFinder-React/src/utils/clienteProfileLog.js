const IS_DEV = import.meta.env?.DEV;

export function logClienteProfile(event, payload = {}) {
  if (!IS_DEV) return;
  console.info('[cliente-profile]', event, payload);
}
