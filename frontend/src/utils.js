export function formatUnixTime(ts, opts = {}) {
  return new Date(ts * 1000).toLocaleTimeString(undefined, opts);
}