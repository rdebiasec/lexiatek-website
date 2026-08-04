/**
 * Escape text for safe interpolation into HTML element content and quoted attributes.
 * OWASP XSS Prevention Cheat Sheet — Rule #1 (HTML context).
 */
export function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}
