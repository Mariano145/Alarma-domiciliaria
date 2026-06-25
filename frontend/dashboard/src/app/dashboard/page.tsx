import { AlarmStateBadge } from '@/components/widgets/AlarmStateBadge';
import { EventsTable } from '@/components/widgets/EventsTable';
import { AnalyticsPanel } from '@/components/widgets/AnalyticsPanel';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white px-6 py-4">
        <div className="mx-auto max-w-5xl flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-gray-900">Alarma IoT</h1>
            <p className="text-xs text-gray-400">Panel de monitoreo — esp32-alarma</p>
          </div>
          <span className="text-xs text-gray-400">Actualización automática cada 3 s</span>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-8 flex flex-col gap-8">
        {/* Estado actual */}
        <section>
          <h2 className="mb-3 text-xs font-semibold uppercase tracking-widest text-gray-400">
            Estado actual
          </h2>
          <div className="max-w-sm">
            <AlarmStateBadge />
          </div>
        </section>

        {/* Analytics */}
        <section>
          <h2 className="mb-3 text-xs font-semibold uppercase tracking-widest text-gray-400">
            Analytics
          </h2>
          <div className="max-w-sm">
            <AnalyticsPanel />
          </div>
        </section>

        {/* Historial */}
        <section>
          <EventsTable />
        </section>
      </main>
    </div>
  );
}