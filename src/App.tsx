import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './layouts/AppShell'
import { AgentsPage } from './pages/AgentsPage'
import { CompliancePage } from './pages/CompliancePage'
import { CounterfactualsPage } from './pages/CounterfactualsPage'
import { DashboardPage } from './pages/DashboardPage'
import { DigitalTwinPage } from './pages/DigitalTwinPage'
import { TelemetryPage } from './pages/TelemetryPage'
import { CyrisProvider } from './state/CyrisContext'

export default function App() {
  return (
    <CyrisProvider>
      <AppShell>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/twin" element={<DigitalTwinPage />} />
          <Route path="/counterfactuals" element={<CounterfactualsPage />} />
          <Route path="/agents" element={<AgentsPage />} />
          <Route path="/compliance" element={<CompliancePage />} />
          <Route path="/telemetry" element={<TelemetryPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppShell>
    </CyrisProvider>
  )
}
