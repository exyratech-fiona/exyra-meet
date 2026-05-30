"use client";

import { useState, Suspense } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Modal } from "@/components/ui/Modal";
import { StatusBadge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { studentApi, batchApi } from "@/lib/api";
import { Student, Batch } from "@/types";
import { getInitials } from "@/lib/utils";
import toast from "react-hot-toast";
import { Plus, Users, Search, Edit2, Trash2, Mail, MessageCircle, Filter } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

function StudentForm({ initial, batches, onSave, onClose }: { initial?: Partial<Student>; batches: Batch[]; onSave: (d: object) => void; onClose: () => void }) {
  const [form, setForm] = useState({
    full_name: initial?.full_name || "",
    email: initial?.email || "",
    whatsapp_number: initial?.whatsapp_number || "+91",
    phone_number: initial?.phone_number || "+91",
    batch_id: initial?.batch_id || "",
    notes: initial?.notes || "",
    fee_amount: initial?.fee_amount || "",
    whatsapp_notifications: initial?.whatsapp_notifications ?? true,
    email_notifications: initial?.email_notifications ?? true,
    fee_paid: initial?.fee_paid ?? false,
  });

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSave(form); }} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-2">
          <label className="text-white/50 text-xs font-medium block mb-1.5">Full Name *</label>
          <input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} className="input" placeholder="Student full name" required />
        </div>
        <div>
          <label className="text-white/50 text-xs font-medium block mb-1.5">Email *</label>
          <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} className="input" placeholder="student@email.com" required />
        </div>
        <div>
          <label className="text-white/50 text-xs font-medium block mb-1.5">WhatsApp Number</label>
          <input value={form.whatsapp_number} onChange={(e) => setForm({ ...form, whatsapp_number: e.target.value })} className="input" placeholder="+91 98765 43210" />
        </div>
        <div>
          <label className="text-white/50 text-xs font-medium block mb-1.5">Phone</label>
          <input value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} className="input" placeholder="+91 98765 43210" />
        </div>
        <div>
          <label className="text-white/50 text-xs font-medium block mb-1.5">Assign Batch</label>
          <select value={form.batch_id} onChange={(e) => setForm({ ...form, batch_id: e.target.value })} className="input">
            <option value="">No batch assigned</option>
            {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
        </div>
        <div>
          <label className="text-white/50 text-xs font-medium block mb-1.5">Fee Amount</label>
          <input value={form.fee_amount} onChange={(e) => setForm({ ...form, fee_amount: e.target.value })} className="input" placeholder="₹5000" />
        </div>
        <div className="col-span-2">
          <label className="text-white/50 text-xs font-medium block mb-1.5">Notes</label>
          <textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} className="input" rows={2} placeholder="Optional notes about the student" />
        </div>
        <div className="col-span-2 flex items-center gap-6">
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.whatsapp_notifications} onChange={(e) => setForm({ ...form, whatsapp_notifications: e.target.checked })} className="w-4 h-4 rounded accent-indigo-600" />
            <span className="text-white/60 text-sm">WhatsApp notifications</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.email_notifications} onChange={(e) => setForm({ ...form, email_notifications: e.target.checked })} className="w-4 h-4 rounded accent-indigo-600" />
            <span className="text-white/60 text-sm">Email notifications</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.fee_paid} onChange={(e) => setForm({ ...form, fee_paid: e.target.checked })} className="w-4 h-4 rounded accent-indigo-600" />
            <span className="text-white/60 text-sm">Fee paid</span>
          </label>
        </div>
      </div>
      <div className="flex gap-3 pt-2">
        <button type="button" onClick={onClose} className="btn-secondary flex-1 justify-center">Cancel</button>
        <button type="submit" className="btn-primary flex-1 justify-center">{initial?.id ? "Save changes" : "Add student"}</button>
      </div>
    </form>
  );
}

function StudentsInner() {
  const qc = useQueryClient();
  const searchParams = useSearchParams();
  const batchFilter = searchParams.get("batch_id") || "";
  const [modal, setModal] = useState<"create" | "edit" | null>(null);
  const [editing, setEditing] = useState<Student | null>(null);
  const [search, setSearch] = useState("");
  const [batchId, setBatchId] = useState(batchFilter);

  const { data: students = [], isLoading } = useQuery<Student[]>({
    queryKey: ["students", batchId, search],
    queryFn: () => studentApi.list({ batch_id: batchId || undefined, search: search || undefined }).then((r) => r.data),
  });

  const { data: batches = [] } = useQuery<Batch[]>({
    queryKey: ["batches"],
    queryFn: () => batchApi.list().then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (d: object) => studentApi.create(d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["students"] }); toast.success("Student added!"); setModal(null); },
    onError: () => toast.error("Failed to add student"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: object }) => studentApi.update(id, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["students"] }); toast.success("Student updated!"); setModal(null); },
    onError: () => toast.error("Failed to update student"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => studentApi.delete(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["students"] }); toast.success("Student removed"); },
  });

  const getBatch = (id?: string) => batches.find((b) => b.id === id);

  return (
    <DashboardLayout>
      <div className="page-header">
        <div>
          <h1 className="page-title">Students</h1>
          <p className="text-white/40 text-sm mt-1">{students.length} student{students.length !== 1 ? "s" : ""}</p>
        </div>
        <button onClick={() => setModal("create")} className="btn-primary">
          <Plus size={14} /> Add Student
        </button>
      </div>

      <div className="flex gap-3 mb-6 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-white/30" />
          <input value={search} onChange={(e) => setSearch(e.target.value)} className="input pl-10" placeholder="Search by name or email..." />
        </div>
        <div className="relative min-w-[180px]">
          <Filter size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-white/30" />
          <select value={batchId} onChange={(e) => setBatchId(e.target.value)} className="input pl-10">
            <option value="">All batches</option>
            {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
        </div>
      </div>

      {isLoading && <div className="space-y-2">{[...Array(5)].map((_, i) => <div key={i} className="h-16 bg-white/5 rounded-xl animate-pulse" />)}</div>}

      {!isLoading && students.length === 0 && (
        <EmptyState icon={Users} title="No students found" description={search ? "Try a different search term" : "Add your first student to get started."} action={!search ? <button onClick={() => setModal("create")} className="btn-primary">Add student</button> : undefined} />
      )}

      <div className="surface overflow-hidden">
        <AnimatePresence>
          {students.map((student, i) => {
            const batch = getBatch(student.batch_id);
            return (
              <motion.div
                key={student.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
                className="flex items-center gap-4 px-6 py-4 border-b border-white/5 last:border-0 hover:bg-white/3 group transition-colors"
              >
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-semibold text-sm flex-shrink-0">
                  {getInitials(student.full_name)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-white font-medium text-sm truncate">{student.full_name}</p>
                    <StatusBadge status={student.status} className="text-[10px]" />
                    {student.fee_paid && <span className="badge bg-green-500/10 text-green-400 border-green-500/20 text-[10px]">Paid</span>}
                  </div>
                  <div className="flex items-center gap-3 mt-0.5">
                    <span className="text-white/30 text-xs flex items-center gap-1"><Mail size={10} />{student.email}</span>
                    {student.whatsapp_number && <span className="text-white/30 text-xs flex items-center gap-1"><MessageCircle size={10} />{student.whatsapp_number}</span>}
                  </div>
                </div>
                {batch && (
                  <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: batch.color }} />
                    <span className="text-white/40 text-xs">{batch.name}</span>
                  </div>
                )}
                <div className="flex items-center gap-1 flex-shrink-0">
                  <span title="WhatsApp" className={`w-2 h-2 rounded-full ${student.whatsapp_notifications ? "bg-green-400" : "bg-white/10"}`} />
                  <span title="Email" className={`w-2 h-2 rounded-full ${student.email_notifications ? "bg-blue-400" : "bg-white/10"}`} />
                </div>
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
                  <button onClick={() => { setEditing(student); setModal("edit"); }} className="btn-secondary py-1.5 px-2.5 text-xs"><Edit2 size={11} /></button>
                  <button onClick={() => { if (confirm(`Remove ${student.full_name}?`)) deleteMutation.mutate(student.id); }} className="btn-danger py-1.5 px-2.5 text-xs"><Trash2 size={11} /></button>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      <Modal open={modal !== null} onClose={() => { setModal(null); setEditing(null); }} title={modal === "edit" ? "Edit Student" : "Add New Student"} size="lg">
        <StudentForm
          initial={editing || undefined}
          batches={batches}
          onSave={(d) => modal === "edit" && editing ? updateMutation.mutate({ id: editing.id, data: d }) : createMutation.mutate(d)}
          onClose={() => { setModal(null); setEditing(null); }}
        />
      </Modal>
    </DashboardLayout>
  );
}

export default function StudentsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#080818]" />}>
      <StudentsInner />
    </Suspense>
  );
}
