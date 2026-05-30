"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Modal } from "@/components/ui/Modal";
import { StatusBadge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { scheduleApi, batchApi } from "@/lib/api";
import { Schedule, Batch } from "@/types";
import { formatDateTime } from "@/lib/utils";
import toast from "react-hot-toast";
import { Plus, Calendar, Clock, ExternalLink, Send, RefreshCw, XCircle, Video, Filter } from "lucide-react";
import { motion } from "framer-motion";

function ScheduleForm({ batches, onSave, onClose }: { batches: Batch[]; onSave: (d: object) => void; onClose: () => void }) {
  const [form, setForm] = useState({
    batch_id: batches[0]?.id || "",
    title: "",
    topic: "",
    scheduled_at: new Date(Date.now() + 86400000).toISOString().slice(0, 16),
    duration_minutes: 90,
    timezone: "Asia/Kolkata",
    auto_create_meet: false,
    meet_link: "",
  });

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSave(form); }} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2">
          <label className="text-white/50 text-xs font-medium block mb-1.5">Batch *</label>
          <select value={form.batch_id} onChange={(e) => setForm({ ...form, batch_id: e.target.value })} className="input" required>
            <option value="">Select batch...</option>
            {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
        </div>
        <div>
          <label className="text-white/50 text-xs font-medium block mb-1.5">Title</label>
          <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="input" placeholder="e.g. Week 3 Session" />
        </div>
        <div>
          <label className="text-white/50 text-xs font-medium block mb-1.5">Topic</label>
          <input value={form.topic} onChange={(e) => setForm({ ...form, topic: e.target.value })} className="input" placeholder="e.g. Neural Networks" />
        </div>
        <div>
          <label className="text-white/50 text-xs font-medium block mb-1.5">Scheduled At *</label>
          <input type="datetime-local" value={form.scheduled_at} onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })} className="input" required />
        </div>
        <div>
          <label className="text-white/50 text-xs font-medium block mb-1.5">Duration (minutes)</label>
          <input type="number" value={form.duration_minutes} onChange={(e) => setForm({ ...form, duration_minutes: +e.target.value })} className="input" min={30} />
        </div>
        <div className="col-span-2">
          <label className="text-white/50 text-xs font-medium block mb-1.5">Custom Meet Link (optional)</label>
          <input value={form.meet_link} onChange={(e) => setForm({ ...form, meet_link: e.target.value })} className="input" placeholder="https://meet.google.com/..." />
        </div>
        <div className="col-span-2 flex items-center gap-2">
          <input type="checkbox" id="auto_meet" checked={form.auto_create_meet} onChange={(e) => setForm({ ...form, auto_create_meet: e.target.checked })} className="w-4 h-4 accent-indigo-600" />
          <label htmlFor="auto_meet" className="text-white/60 text-sm cursor-pointer">Auto-create Google Meet (requires Calendar API)</label>
        </div>
      </div>
      <div className="flex gap-3 pt-2">
        <button type="button" onClick={onClose} className="btn-secondary flex-1 justify-center">Cancel</button>
        <button type="submit" className="btn-primary flex-1 justify-center">Schedule Class</button>
      </div>
    </form>
  );
}

function RescheduleForm({ schedule, onSave, onClose }: { schedule: Schedule; onSave: (d: object) => void; onClose: () => void }) {
  const [form, setForm] = useState({
    new_scheduled_at: new Date(schedule.scheduled_at).toISOString().slice(0, 16),
    reason: "",
    notify_students: true,
  });

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSave(form); }} className="space-y-4">
      <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 mb-2">
        <p className="text-yellow-400 text-sm font-medium">Rescheduling class</p>
        <p className="text-white/40 text-xs mt-1">Students will be notified via WhatsApp & Email</p>
      </div>
      <div>
        <label className="text-white/50 text-xs font-medium block mb-1.5">New Date & Time *</label>
        <input type="datetime-local" value={form.new_scheduled_at} onChange={(e) => setForm({ ...form, new_scheduled_at: e.target.value })} className="input" required />
      </div>
      <div>
        <label className="text-white/50 text-xs font-medium block mb-1.5">Reason (optional)</label>
        <textarea value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} className="input" rows={2} placeholder="Reason for rescheduling..." />
      </div>
      <label className="flex items-center gap-2 cursor-pointer">
        <input type="checkbox" checked={form.notify_students} onChange={(e) => setForm({ ...form, notify_students: e.target.checked })} className="w-4 h-4 accent-indigo-600" />
        <span className="text-white/60 text-sm">Notify students immediately</span>
      </label>
      <div className="flex gap-3 pt-2">
        <button type="button" onClick={onClose} className="btn-secondary flex-1 justify-center">Cancel</button>
        <button type="submit" className="btn-primary flex-1 justify-center">Reschedule</button>
      </div>
    </form>
  );
}

export default function SchedulePage() {
  const qc = useQueryClient();
  const [createOpen, setCreateOpen] = useState(false);
  const [rescheduleTarget, setRescheduleTarget] = useState<Schedule | null>(null);
  const [batchFilter, setBatchFilter] = useState("");

  const { data: schedules = [], isLoading } = useQuery<Schedule[]>({
    queryKey: ["schedules", batchFilter],
    queryFn: () => scheduleApi.list({ batch_id: batchFilter || undefined }).then((r) => r.data),
    refetchInterval: 30_000,
  });

  const { data: batches = [] } = useQuery<Batch[]>({
    queryKey: ["batches"],
    queryFn: () => batchApi.list().then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (d: object) => scheduleApi.create(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["schedules"] }); toast.success("Class scheduled!"); setCreateOpen(false); },
    onError: (e: any) => toast.error(e?.response?.data?.detail || "Failed to schedule"),
  });

  const rescheduleMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: object }) => scheduleApi.reschedule(id, data as any),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["schedules"] }); toast.success("Class rescheduled + students notified!"); setRescheduleTarget(null); },
    onError: () => toast.error("Reschedule failed"),
  });

  const cancelMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) => scheduleApi.cancel(id, { reason, notify_students: true }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["schedules"] }); toast.success("Class cancelled, students notified"); },
  });

  const sendLinkMutation = useMutation({
    mutationFn: (id: string) => scheduleApi.sendLink(id),
    onSuccess: (res) => toast.success(res.data.message || "Meet link sent!"),
    onError: (e: any) => toast.error(e?.response?.data?.detail || "Send failed"),
  });

  const getBatch = (id: string) => batches.find((b) => b.id === id);

  return (
    <DashboardLayout>
      <div className="page-header">
        <div>
          <h1 className="page-title">Schedule</h1>
          <p className="text-white/40 text-sm mt-1">{schedules.length} class{schedules.length !== 1 ? "es" : ""} scheduled</p>
        </div>
        <button onClick={() => setCreateOpen(true)} className="btn-primary">
          <Plus size={14} /> New Class
        </button>
      </div>

      {/* Filter */}
      <div className="flex gap-3 mb-6">
        <div className="relative min-w-[200px]">
          <Filter size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-white/30" />
          <select value={batchFilter} onChange={(e) => setBatchFilter(e.target.value)} className="input pl-10">
            <option value="">All batches</option>
            {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
        </div>
      </div>

      {isLoading && <div className="space-y-3">{[...Array(4)].map((_, i) => <div key={i} className="h-20 bg-white/5 rounded-xl animate-pulse" />)}</div>}

      {!isLoading && schedules.length === 0 && (
        <EmptyState icon={Calendar} title="No classes scheduled" description="Schedule your first class to get started." action={<button onClick={() => setCreateOpen(true)} className="btn-primary">Schedule a class</button>} />
      )}

      <div className="space-y-3">
        {schedules.map((sched) => {
          const batch = getBatch(sched.batch_id);
          const isPast = new Date(sched.scheduled_at) < new Date();
          return (
            <motion.div key={sched.id} whileHover={{ x: 2 }} className="surface flex items-center gap-4 p-5 group">
              {/* Color + status bar */}
              <div className="flex flex-col items-center gap-1 flex-shrink-0">
                <div className="w-1 h-8 rounded-full" style={{ backgroundColor: batch?.color || "#6366f1" }} />
              </div>

              {/* Main info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <p className="text-white font-medium text-sm">{sched.title || `${batch?.name || "Class"} Session`}</p>
                  <StatusBadge status={sched.status} />
                  {sched.notifications_sent && <span className="badge bg-green-500/10 text-green-400 border-green-500/20 text-[10px]">Notified</span>}
                </div>
                <div className="flex items-center gap-4 flex-wrap">
                  <span className="text-white/40 text-xs flex items-center gap-1">
                    <Calendar size={11} />{formatDateTime(sched.scheduled_at)}
                  </span>
                  <span className="text-white/40 text-xs flex items-center gap-1">
                    <Clock size={11} />{sched.duration_minutes}m
                  </span>
                  {batch && (
                    <span className="text-white/30 text-xs flex items-center gap-1.5">
                      <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: batch.color }} />
                      {batch.name}
                    </span>
                  )}
                  {sched.topic && <span className="text-white/30 text-xs">· {sched.topic}</span>}
                </div>
              </div>

              {/* Meet link */}
              {sched.meet_link && (
                <a href={sched.meet_link} target="_blank" rel="noreferrer" className="flex items-center gap-1.5 text-indigo-400 hover:text-indigo-300 text-xs bg-indigo-500/10 rounded-lg px-3 py-2 flex-shrink-0 transition-colors">
                  <Video size={12} /> Join
                </a>
              )}

              {/* Actions */}
              <div className="flex gap-2 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                {sched.meet_link && sched.status === "scheduled" && (
                  <button onClick={() => sendLinkMutation.mutate(sched.id)} title="Send link to students" className="btn-primary py-1.5 px-2.5 text-xs">
                    <Send size={11} />
                  </button>
                )}
                {sched.status === "scheduled" && !isPast && (
                  <button onClick={() => setRescheduleTarget(sched)} title="Reschedule" className="btn-secondary py-1.5 px-2.5 text-xs">
                    <RefreshCw size={11} />
                  </button>
                )}
                {sched.status === "scheduled" && (
                  <button onClick={() => { if (confirm("Cancel this class?")) cancelMutation.mutate({ id: sched.id }); }} title="Cancel class" className="btn-danger py-1.5 px-2.5 text-xs">
                    <XCircle size={11} />
                  </button>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      <Modal open={createOpen} onClose={() => setCreateOpen(false)} title="Schedule New Class" size="lg">
        <ScheduleForm batches={batches} onSave={(d) => createMutation.mutate(d)} onClose={() => setCreateOpen(false)} />
      </Modal>

      <Modal open={!!rescheduleTarget} onClose={() => setRescheduleTarget(null)} title="Reschedule Class" size="md">
        {rescheduleTarget && (
          <RescheduleForm schedule={rescheduleTarget} onSave={(d) => rescheduleMutation.mutate({ id: rescheduleTarget.id, data: d })} onClose={() => setRescheduleTarget(null)} />
        )}
      </Modal>
    </DashboardLayout>
  );
}
