"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Modal } from "@/components/ui/Modal";
import { StatusBadge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { batchApi } from "@/lib/api";
import { Batch } from "@/types";
import { BATCH_COLORS, TIMEZONES } from "@/lib/utils";
import toast from "react-hot-toast";
import { Plus, BookOpen, Users, Edit2, Trash2, Video, Calendar, Copy } from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

const WEEK_DAYS_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function BatchForm({ initial, onSave, onClose }: { initial?: Partial<Batch>; onSave: (d: object) => void; onClose: () => void }) {
  const [form, setForm] = useState({
    name: initial?.name || "",
    course: initial?.course || "",
    description: initial?.description || "",
    color: initial?.color || "#6366f1",
    timezone: initial?.timezone || "Asia/Kolkata",
    default_duration_minutes: initial?.default_duration_minutes || 90,
    max_students: initial?.max_students || 30,
    recurrence_type: (initial?.recurrence_type || "weekly") as "daily" | "weekly" | "custom",
    recurrence_days: (Array.isArray(initial?.recurrence_days) ? initial.recurrence_days.join(",") : initial?.recurrence_days) || "",
  });

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSave(form); }} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2">
          <label className="text-white/50 text-xs font-medium block mb-1.5">Batch Name *</label>
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="input" placeholder="e.g. AI Batch - Morning" required />
        </div>
        <div className="col-span-2">
          <label className="text-white/50 text-xs font-medium block mb-1.5">Course *</label>
          <input value={form.course} onChange={(e) => setForm({ ...form, course: e.target.value })} className="input" placeholder="e.g. Artificial Intelligence" required />
        </div>
        <div className="col-span-2">
          <label className="text-white/50 text-xs font-medium block mb-1.5">Description</label>
          <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="input" rows={2} placeholder="Optional batch description" />
        </div>
        <div>
          <label className="text-white/50 text-xs font-medium block mb-1.5">Timezone</label>
          <select value={form.timezone} onChange={(e) => setForm({ ...form, timezone: e.target.value })} className="input">
            {TIMEZONES.map((tz) => <option key={tz} value={tz}>{tz}</option>)}
          </select>
        </div>
        <div>
          <label className="text-white/50 text-xs font-medium block mb-1.5">Duration (minutes)</label>
          <input type="number" value={form.default_duration_minutes} onChange={(e) => setForm({ ...form, default_duration_minutes: +e.target.value })} className="input" min={30} max={480} />
        </div>
        <div>
          <label className="text-white/50 text-xs font-medium block mb-1.5">Max Students</label>
          <input type="number" value={form.max_students} onChange={(e) => setForm({ ...form, max_students: +e.target.value })} className="input" min={1} />
        </div>
        <div>
          <label className="text-white/50 text-xs font-medium block mb-1.5">Recurrence</label>
          <select value={form.recurrence_type} onChange={(e) => setForm({ ...form, recurrence_type: e.target.value as "daily" | "weekly" | "custom" })} className="input">
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        <div className="col-span-2">
          <label className="text-white/50 text-xs font-medium block mb-1.5">Class Days (comma-sep: 0=Mon … 6=Sun)</label>
          <input value={form.recurrence_days} onChange={(e) => setForm({ ...form, recurrence_days: e.target.value })} className="input" placeholder="e.g. 0,2,4 for Mon/Wed/Fri" />
        </div>
        <div className="col-span-2">
          <label className="text-white/50 text-xs font-medium block mb-2">Color</label>
          <div className="flex gap-2 flex-wrap">
            {BATCH_COLORS.map((c) => (
              <button key={c} type="button" onClick={() => setForm({ ...form, color: c })}
                className={`w-7 h-7 rounded-lg transition-all ${form.color === c ? "ring-2 ring-white ring-offset-2 ring-offset-[#12121f] scale-110" : "hover:scale-105"}`}
                style={{ backgroundColor: c }}
              />
            ))}
          </div>
        </div>
      </div>
      <div className="flex gap-3 pt-2">
        <button type="button" onClick={onClose} className="btn-secondary flex-1 justify-center">Cancel</button>
        <button type="submit" className="btn-primary flex-1 justify-center">
          {initial?.id ? "Save changes" : "Create batch"}
        </button>
      </div>
    </form>
  );
}

export default function BatchesPage() {
  const qc = useQueryClient();
  const [modal, setModal] = useState<"create" | "edit" | null>(null);
  const [editing, setEditing] = useState<Batch | null>(null);

  const { data: batches = [], isLoading } = useQuery<Batch[]>({
    queryKey: ["batches"],
    queryFn: () => batchApi.list().then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (d: object) => batchApi.create(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["batches"] }); toast.success("Batch created!"); setModal(null); },
    onError: () => toast.error("Failed to create batch"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: object }) => batchApi.update(id, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["batches"] }); toast.success("Batch updated!"); setModal(null); },
    onError: () => toast.error("Failed to update batch"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => batchApi.delete(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["batches"] }); toast.success("Batch deleted"); },
    onError: () => toast.error("Failed to delete batch"),
  });

  return (
    <DashboardLayout>
      <div className="page-header">
        <div>
          <h1 className="page-title">Batches</h1>
          <p className="text-white/40 text-sm mt-1">{batches.length} batch{batches.length !== 1 ? "es" : ""} total</p>
        </div>
        <button onClick={() => setModal("create")} className="btn-primary">
          <Plus size={14} /> New Batch
        </button>
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => <div key={i} className="h-48 bg-white/5 rounded-2xl animate-pulse" />)}
        </div>
      )}

      {!isLoading && batches.length === 0 && (
        <EmptyState icon={BookOpen} title="No batches yet" description="Create your first batch to start managing students and classes." action={<button onClick={() => setModal("create")} className="btn-primary">Create batch</button>} />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {batches.map((batch) => (
          <motion.div key={batch.id} whileHover={{ y: -2 }} className="surface group">
            {/* Color bar */}
            <div className="h-1 rounded-t-2xl" style={{ backgroundColor: batch.color }} />
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: batch.color + "20" }}>
                    <BookOpen size={16} style={{ color: batch.color }} />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold text-sm">{batch.name}</h3>
                    <p className="text-white/40 text-xs">{batch.course}</p>
                  </div>
                </div>
                <StatusBadge status={batch.status} />
              </div>

              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-white/5 rounded-xl p-3">
                  <div className="flex items-center gap-1.5 mb-1">
                    <Users size={11} className="text-white/30" />
                    <span className="text-white/30 text-[10px]">Students</span>
                  </div>
                  <p className="text-white font-semibold">{batch.student_count || 0}</p>
                </div>
                <div className="bg-white/5 rounded-xl p-3">
                  <div className="flex items-center gap-1.5 mb-1">
                    <Calendar size={11} className="text-white/30" />
                    <span className="text-white/30 text-[10px]">Duration</span>
                  </div>
                  <p className="text-white font-semibold">{batch.default_duration_minutes}m</p>
                </div>
              </div>

              {batch.google_meet_link || batch.custom_meet_link ? (
                <a href={batch.google_meet_link || batch.custom_meet_link!} target="_blank" rel="noreferrer"
                  className="flex items-center gap-2 text-xs text-indigo-400 hover:text-indigo-300 mb-4 bg-indigo-500/10 rounded-lg px-3 py-2 transition-colors">
                  <Video size={12} /> Join Meet Link
                </a>
              ) : null}

              <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <Link href={`/students?batch_id=${batch.id}`} className="btn-secondary flex-1 justify-center text-xs py-1.5">
                  <Users size={12} /> Students
                </Link>
                <button onClick={() => { setEditing(batch); setModal("edit"); }} className="btn-secondary px-3">
                  <Edit2 size={12} />
                </button>
                <button onClick={() => { if (confirm("Delete this batch?")) deleteMutation.mutate(batch.id); }} className="btn-danger px-3">
                  <Trash2 size={12} />
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <Modal open={modal !== null} onClose={() => { setModal(null); setEditing(null); }} title={modal === "edit" ? "Edit Batch" : "Create New Batch"} size="lg">
        <BatchForm
          initial={editing || undefined}
          onSave={(d) => modal === "edit" && editing ? updateMutation.mutate({ id: editing.id, data: d }) : createMutation.mutate(d)}
          onClose={() => { setModal(null); setEditing(null); }}
        />
      </Modal>
    </DashboardLayout>
  );
}
