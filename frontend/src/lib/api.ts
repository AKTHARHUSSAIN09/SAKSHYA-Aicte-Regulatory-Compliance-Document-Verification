/**
 * The browser-visible API origin. Set NEXT_PUBLIC_API_BASE in .env.local when
 * the backend is hosted on a port other than the default 8000.
 */
export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000/api/v1";
