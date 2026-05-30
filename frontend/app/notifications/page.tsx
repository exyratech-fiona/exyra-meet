"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { StatusBadge } from "@/components/ui/Badge";
import { notificationApi, batchApi } from "@/lib/api";
import { NotificationLog, Batch } from "@/types";
import { formatRelative, formatDateTime } from "@/lib/utils";
import toast from "react-hot-toast";
import { Send, Bell, Mail, MessageCircle, Users, Filter } from "lucide-react";
import { motion } from "framer-motion";

const CATEGORIES = [
  { value: "schedule_reminder", label: "Schedule Reminder" },
  { value: "meet_link", label: "Meet Link" },
  { value: "reschedule", label: "Reschedule Notice" },
  { value: "cancellation", label: "Cancellation" },
  { value: "welcome", label: "Welcome" },
  { value: "custom", label: "Custom Message" },
];

export default function NotificationsPage() {
  const [batchId, setBatchId] = useState("");
  const [type, setType] = useState("both");
  const [category, setCategory] = useState("custom");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [filterBatch, setFilterBatch] = useState("");

  const { data: logs = [], isLoading, refetch } = useQuery<NotificationLog[]>({
    queryKey: ["notification-logs", filterBatch],
    queryFn: () => notificationApi.getLogs({ batch_id: filterBatch || undefined, limit: 100 }).then((r) => r.data),
  });

  const { data: batches = [] } = useQuery<Batch[]>({
    queryKey: ["batches"],
    queryFn: () => batchApi.list().then((r) => r.data),
  });

  const sendMutation = useMutation({
    mutationFn: () =>
      notificationApi.send({ batch_id: batchId || undefined, notification_type: type, category, subject, message }),
    onSuccess: (res) => {
      toast.success(res.data.message || "Notifications sent!");
      refetch();
      setMessage("");
      setSubject("");
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || "Failed to send"),
  });

  const stats = {
    total: logs.length,
    sent: logs.filter((l) => l.status === "sent").length,
    failed: logs.filter((l) => l.status === "failed").length,
    whatsapp: logs.filter((l) => l.notification_type === "whatsapp" || l.notification_type === "both").length,
    email: logs.filter((l) => l.notification_type === "email" || l.notification_type === "both").length,
  };

  return (
    <DashboardLayout>
      <div className="page-header">
        <div>
          <h1 className="page-title">Notifications</h1>
          <p className="text-white/40 text-sm mt-1">Send messages & view history</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Total Sent", value: stats.total, icon: Bell, color: "text-indigo-400" },
          { label: "Delivered", value: stats.sent, icon: Send, color: "text-green-400" },
          { label: "WhatsApp", value: stats.whatsapp, icon: MessageCircle, color: "text-green-400" },
          { label: "Email", value: stats.email, icon: Mail, color: "text-blue-400" },
        ].map((s) => (
          <div key={s.label} className="surface p-5">
            <s.icon size={16} className={s.color + " mb-3"} />
            <p className="text-2xl font-bold text-white">{s.value}</p>
            <p className="text-white/40 text-xs mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Compose */}
        <div className="xl:col-span-1 surface p-6">
          <h2 className="section-title">Send Notification</h2>
          <div className="space-y-4">
            <div>
              <label className="text-white/50 text-xs font-medium block mb-1.5">Send to Batch</label>
              <select value={batchId} onChange={(e) => setBatchId(e.target.value)} className="input">
                <option value="">All active students</option>
                {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
            </div>
            <div>
              <label className="text-white/50 text-xs font-medium block mb-1.5">Channel</label>
              <div className="grid grid-cols-3 gap-2">
                {[{ v: "both", label: "Both" }, { v: "whatsapp", label: "WhatsApp" }, { v: "email", label: "Email" }].map((ch) => (
                  <button key={ch.v} type="button" onClick={() => setType(ch.v)}
                    className={`py-2 rounded-xl text-xs font-medium border transition-all ${type === ch.v ? "bg-indigo-600/20 text-indigo-300 border-indigo-500/30" : "bg-white/5 text-white/40 border-white/5 hover:bg-white/8"}`}>
                    {ch.label}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-white/50 text-xs font-medium block mb-1.5">Category</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)} className="input">
                {CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
              </select>
            </div>
            <div>
              <label className="text-white/50 text-xs font-medium block mb-1.5">Subject (email)</label>
              <input value={subject} onChange={(e) => setSubject(e.target.value)} className="input" placeholder="Email subject..." />
            </div>
            <div>
              <label className="text-white/50 text-xs font-medium block mb-1.5">Message *</label>
              <textarea value={message} onChange={(e) => setMessage(e.target.value)} className="input" rows={5} placeholder="Write your message here..." />
              <p className="text-white/20 text-[10px] mt-1">{message.length} characters</p>
            </div>
            <button
              onClick={() => sendMutation.mutate()}
              disabled={!message.trim() || sendMutation.isPending}
              className="btn-primary w-full justify-center py-3"
            >
              {sendMutation.isPending ? (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <><Send size={14} /> Send Notification</>
              )}
            </button>
          </div>
        </div>

        {/* Log */}
        <div className="xl:col-span-2 surface">
          <div className="px-6 py-5 border-b border-white/5 flex items-center justify-between">
            <h2 className="section-title mb-0">Notification History</h2>
            <div className="relative">
              <Filter size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" />
              <select value={filterBatch} onChange={(e) => setFilterBatch(e.target.value)} className="input pl-8 text-xs py-1.5">
                <option value="">All batches</option>
                {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
            </div>
          </div>
          <div className="divide-y divide-white/5 max-h-[600px] overflow-y-auto">
            {isLoading && (
              <div className="p-6 space-y-3">
                {[...Array(5)].map((_, i) => <div key={i} className="h-12 bg-white/5 rounded-xl animate-pulse" />)}
              </div>
            )}
            {!isLoading && logs.length === 0 && (
              <div className="py-16 text-center">
                <Bell size={28} className="text-white/10 mx-auto mb-3" />
                <p className="text-white/30 text-sm">No notifications sent yet</p>
              </div>
            )}
            {logs.map((log) => (
              <motion.div key={log.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="px-6 py-4 hover:bg-white/2 transition-colors">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <div className="mt-0.5">
                      {log.notification_type === "whatsapp" ? (
                        <MessageCircle size={13} className="text-green-400" />
                      ) : log.notification_type === "email" ? (
                        <Mail size={13} className="text-blue-400" />
                      ) : (
                        <div className="flex gap-0.5">
                          <MessageCircle size={11} className="text-green-400" />
                          <Mail size={11} className="text-blue-400" />
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="text-white/70 text-xs font-medium capitalize">{log.category.replace(/_/g, " ")}</p>
                        <StatusBadge status={log.status} className="text-[10px]" />
                      </div>
                      {log.recipient_name && <p className="text-white/40 text-xs mt-0.5">To: {log.recipient_name}</p>}
                      {log.subject && <p className="text-white/30 text-xs truncate mt-0.5">{log.subject}</p>}
                    </div>
                  </div>
                  <p className="text-white/20 text-[10px] flex-shrink-0">{log.sent_at ? formatRelative(log.sent_at) : formatRelative(log.created_at)}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
