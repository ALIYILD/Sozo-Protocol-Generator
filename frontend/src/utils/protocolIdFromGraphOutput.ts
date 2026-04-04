/**
 * When the graph persists a protocol row, the status payload may include
 * `output.protocol_id` for `GET /protocols/:id/audit`.
 */
export function protocolIdFromGraphOutput(
  output: Record<string, unknown> | undefined,
): string | undefined {
  const raw = output?.protocol_id;
  return typeof raw === 'string' && raw.trim().length > 0 ? raw.trim() : undefined;
}
