/** Health check. The run-verification endpoint (Phase 4) will live next to this. */
export function GET() {
  return Response.json({ status: 'ok' });
}
