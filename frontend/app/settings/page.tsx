"use client";

import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useAuthStore } from "@/lib/store";
import { Settings, User, Bell, Shield, Database, Link, Info } from "lucide-react";

function SettingSection({ title, icon: Icon, children }: { title: string; icon: any; children: React.ReactNode }) {
  return (
    <div className="surface p-6">
      <div className="flex items-center gap-2 mb-5 pb-4 border-b border-white/5">
        <Icon size={16} className="text-indigo-400" />
        <h2 className="text-white font-semibold text-sm">{title}</h2>
      </div>
      {children}
    </div>
  );
}

function SettingRow({ label, desc, children }: { label: string; desc?: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-white/5 last:border-0">
      <div>
        <p className="text-white/70 text-sm">{label}</p>
        {desc && <p className="text-white/30 text-xs mt-0.5">{desc}</p>}
      </div>
      <div className="flex-shrink-0 ml-4">{children}</div>
    </div>
  );
}

export default function SettingsPage() {
  const { user } = useAuthStore();

  return (
    <DashboardLayout>
      <div className="page-header">
        <div>
          <h1 className="page-title">Settings</h1>
          <p className="text-white/40 text-sm mt-1">Manage platform configuration</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <SettingSection title="Profile" icon={User}>
          <SettingRow label="Name" desc="Your display name">
            <p className="text-white/60 text-sm">{user?.full_name}</p>
          </SettingRow>
          <SettingRow label="Email" desc="Login email address">
            <p className="text-white/60 text-sm">{user?.email}</p>
          </SettingRow>
          <SettingRow label="Role" desc="Access level">
            <span className="badge bg-indigo-500/20 text-indigo-300 border-indigo-500/20 capitalize">{user?.role}</span>
          </SettingRow>
        </SettingSection>

        <SettingSection title="Integrations" icon={Link}>
          <SettingRow label="Google Calendar" desc="Auto-create Google Meet events">
            <span className="badge bg-yellow-500/10 text-yellow-400 border-yellow-500/20 text-xs">Needs setup</span>
          </SettingRow>
          <SettingRow label="WhatsApp Cloud API" desc="Send WhatsApp messages">
            <span className="badge bg-yellow-500/10 text-yellow-400 border-yellow-500/20 text-xs">Needs setup</span>
          </SettingRow>
          <SettingRow label="Gmail / SMTP" desc="Send email notifications">
            <span className="badge bg-yellow-500/10 text-yellow-400 border-yellow-500/20 text-xs">Needs setup</span>
          </SettingRow>
          <div className="mt-4 bg-indigo-500/5 border border-indigo-500/20 rounded-xl p-4">
            <p className="text-indigo-300 text-xs font-medium mb-1">How to set up integrations</p>
            <ol className="text-white/40 text-xs space-y-1 list-decimal list-inside">
              <li>Edit <code className="text-indigo-400">backend/.env</code> file</li>
              <li>Add your Google OAuth credentials</li>
              <li>Add WhatsApp Cloud API token</li>
              <li>Add Gmail App Password</li>
              <li>Restart the backend server</li>
            </ol>
          </div>
        </SettingSection>

        <SettingSection title="Notifications" icon={Bell}>
          <SettingRow label="24h reminder" desc="Send reminder 24 hours before class">
            <span className="badge bg-green-500/10 text-green-400 border-green-500/20 text-xs">Enabled</span>
          </SettingRow>
          <SettingRow label="1h reminder" desc="Send reminder 1 hour before class">
            <span className="badge bg-green-500/10 text-green-400 border-green-500/20 text-xs">Enabled</span>
          </SettingRow>
          <SettingRow label="Auto-notify on reschedule" desc="Notify all students when class is rescheduled">
            <span className="badge bg-green-500/10 text-green-400 border-green-500/20 text-xs">Enabled</span>
          </SettingRow>
        </SettingSection>

        <SettingSection title="Database" icon={Database}>
          <SettingRow label="Database" desc="Primary database">
            <p className="text-white/60 text-sm font-mono">MySQL 8.0</p>
          </SettingRow>
          <SettingRow label="Host" desc="Connection host">
            <p className="text-white/60 text-sm font-mono">localhost:3306</p>
          </SettingRow>
          <SettingRow label="Database name" desc="Active schema">
            <p className="text-white/60 text-sm font-mono">exyra_meet</p>
          </SettingRow>
        </SettingSection>

        <SettingSection title="System Info" icon={Info}>
          <SettingRow label="Backend" desc="API server">
            <p className="text-white/60 text-sm">FastAPI 0.111 · Python 3.12</p>
          </SettingRow>
          <SettingRow label="Frontend" desc="Web app">
            <p className="text-white/60 text-sm">Next.js 14 · React 18</p>
          </SettingRow>
          <SettingRow label="API Docs" desc="Interactive API documentation">
            <a href="http://localhost:8000/api/docs" target="_blank" rel="noreferrer" className="text-indigo-400 hover:text-indigo-300 text-sm">Open Swagger →</a>
          </SettingRow>
          <SettingRow label="Version" desc="Platform version">
            <span className="badge bg-white/5 text-white/40 border-white/5">v1.0.0</span>
          </SettingRow>
        </SettingSection>
      </div>
    </DashboardLayout>
  );
}
