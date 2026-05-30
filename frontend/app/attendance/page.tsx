"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { StatusBadge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { attendanceApi, scheduleApi, batchApi } from "@/lib/api";
import { Schedule, Batch, Attendance } from "@/types";
import { formatDateTime, getInitials } from "@/lib/utils";
import toast from "react-hot-toast";
import { ClipboardList, CheckCircle2, XCircle, Clock, Filter, Save } from "lucide-react";

export default function AttendancePage() {
  const qc = useQueryClient();
  const [batchId, setBatchId] = useState("");
  const [scheduleId, setScheduleId] = useState("");
  const [attendanceMap, setAttendanceMap] = useState<Record<string, string>>({});

  const { data: batches = [] } = useQuery<Batch[]>({
    queryKey: ["batches"],
    queryFn: () => batchApi.list().then((r) => r.data),
  });

  const { data: schedules = [] } = useQuery<Schedule[]>({
    queryKey: ["schedules", batchId],
    queryFn: () => scheduleApi.list({ batch_id: batchId || undefined }).then((r) => r.data),
    enabled: true,
  });

  const { data: attendance = [], isLoading: loadingAttendance } = useQuery<Attendance[]>({
    queryKey: ["attendance", scheduleId],
    queryFn: () => attendanceApi.getForSchedule(scheduleId).then((r) => r.data),
    enabled: !!scheduleId,
  });

  useEffect(() => {
    if (attendance.length > 0) {
      const map: Record<string, string> = {};
      attendance.forEach((a) => { map[a.student_id] = a.status; });
      setAttendanceMap(map);
    }
  }, [attendance]);

  const saveMutation = useMutation({
    mutationFn: () => {
      const records = Object.entries(attendanceMap).map(([student_id, status]) => ({ student_id, status }));
      return attendanceApi.markAttendance(scheduleId, records);
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["attendance"] }); toast.success("Attendance saved!"); },
    onError: () => toast.error("Failed to save attendance"),
  });

  const toggleStatus = (studentId: string, current: string) => {
    const cycle: Record<string, string> = { present: "absent", absent: "late", late: "excused", excused: "present" };
    setAttendanceMap((prev) => ({ ...prev, [studentId]: cycle[current] || "present" }));
  };

  const statusIcon: Record<string, React.ReactNode> = {
    present: <CheckCircle2 size={16} className="text-green-400" />,
    absent: <XCircle size={16} className="text-red-400" />,
    late: <Clock size={16} className="text-yellow-400" />,
    excused: <CheckCircle2 size={16} className="text-blue-400" />,
  };

  const selectedSchedule = schedules.find((s) => s.id === scheduleId);
  const presentCount = Object.values(attendanceMap).filter((s) => s === "present").length;
  const total = attendance.length;

  return (
    <DashboardLayout>
      <div className="page-header">
        <div>
          <h1 className="page-title">Attendance</h1>
          <p className="text-white/40 text-sm mt-1">Track student attendance per class</p>
        </div>
        {scheduleId && attendance.length > 0 && (
          <button onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending} className="btn-primary">
            <Save size={14} /> {saveMutation.isPending ? "Saving..." : "Save Attendance"}
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-6 flex-wrap">
        <div className="relative min-w-[200px]">
          <Filter size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-white/30" />
          <select value={batchId} onChange={(e) => { setBatchId(e.target.value); setScheduleId(""); }} className="input pl-10">
            <option value="">All batches</option>
            {batches.map((b) => <option key={b.id} value={b.id}>{b.name}</option>)}
          </select>
        </div>
        <div className="relative flex-1 min-w-[250px]">
          <ClipboardList size={14} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-white/30" />
          <select value={scheduleId} onChange={(e) => setScheduleId(e.target.value)} className="input pl-10">
            <option value="">Select a class session...</option>
            {schedules.map((s) => (
              <option key={s.id} value={s.id}>
                {formatDateTime(s.scheduled_at)} — {s.title || "Class"}
              </option>
            ))}
          </select>
        </div>
      </div>

      {!scheduleId && (
        <EmptyState icon={ClipboardList} title="Select a class" description="Choose a batch and class session to mark attendance." />
      )}

      {scheduleId && !loadingAttendance && attendance.length === 0 && (
        <EmptyState icon={ClipboardList} title="No students in this class" description="Assign students to this batch first." />
      )}

      {scheduleId && attendance.length > 0 && (
        <>
          {/* Summary */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            {[
              { label: "Total", value: total, color: "text-white" },
              { label: "Present", value: Object.values(attendanceMap).filter((s) => s === "present").length, color: "text-green-400" },
              { label: "Absent", value: Object.values(attendanceMap).filter((s) => s === "absent").length, color: "text-red-400" },
              { label: "Late", value: Object.values(attendanceMap).filter((s) => s === "late").length, color: "text-yellow-400" },
            ].map((s) => (
              <div key={s.label} className="surface p-4 text-center">
                <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
                <p className="text-white/40 text-xs mt-0.5">{s.label}</p>
              </div>
            ))}
          </div>

          {/* Attendance rate bar */}
          {total > 0 && (
            <div className="surface p-4 mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white/50 text-xs">Attendance rate</span>
                <span className="text-white font-semibold text-sm">{Math.round(presentCount / total * 100)}%</span>
              </div>
              <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-indigo-500 to-green-500 rounded-full transition-all duration-500" style={{ width: `${presentCount / total * 100}%` }} />
              </div>
            </div>
          )}

          <div className="surface overflow-hidden">
            {attendance.map((a, i) => {
              const status = attendanceMap[a.student_id] || a.status || "absent";
              return (
                <div key={a.student_id} className={`flex items-center gap-4 px-6 py-4 border-b border-white/5 last:border-0 hover:bg-white/3 transition-colors ${i % 2 === 0 ? "" : "bg-white/1"}`}>
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-semibold text-xs flex-shrink-0">
                    {getInitials(a.name)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm font-medium">{a.name}</p>
                    <p className="text-white/30 text-xs">{a.email}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <StatusBadge status={status} />
                    <button
                      onClick={() => toggleStatus(a.student_id, status)}
                      className="p-2 rounded-lg hover:bg-white/5 transition-colors"
                      title="Click to cycle status"
                    >
                      {statusIcon[status]}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          <p className="text-white/20 text-xs mt-3 text-center">Click the icon next to each student to cycle: Present → Absent → Late → Excused</p>
        </>
      )}
    </DashboardLayout>
  );
}
