/**
 * Next.js muestra este segmento automáticamente mientras carga /dashboard.
 */

export default function DashboardLoading() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white px-6 py-4">
        <div className="mx-auto max-w-5xl">
          <div className="h-5 w-32 rounded bg-gray-200 animate-pulse" />
          <div className="mt-1 h-3 w-48 rounded bg-gray-100 animate-pulse" />
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-8 flex flex-col gap-8">
        <div className="h-28 w-80 rounded-xl bg-gray-200 animate-pulse" />
        <div className="h-64 w-full rounded-xl bg-gray-200 animate-pulse" />
      </main>
    </div>
  );
}