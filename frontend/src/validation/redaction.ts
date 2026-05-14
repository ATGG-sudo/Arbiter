const SECRET_PATTERN =
  /(sk-[A-Za-z0-9_-]+|api[_-]?key|password|bearer\s+[A-Za-z0-9._-]+)/gi

export function redactSecrets(text: string): string {
  return text.replace(SECRET_PATTERN, '[REDACTED]')
}

export function sanitizeTraceStep(label: string): string {
  return redactSecrets(label)
}

export function isPotentiallySensitive(text: string): boolean {
  return SECRET_PATTERN.test(text)
}
