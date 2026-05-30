"use client";

import { useQuery } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { StatCard } from "@/components/ui/StatCard";
import { StatusBadge } from "@/components/ui/Badge";
import { dashboardApi } from "@/lib/api";
import { formatDateTime, formatRelative } from "@/lib/utils";
import { DashboardStats } from "@/types";
import {
  BookOpen, Users, Calendar, TrendingUp, Video,
  Bell, ChevronRight, Clock, ExternalLink,
} from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function DashboardPage() {
  const { data, isLoading } = useQuery<DashboardStats>({
    queryKey: ["dashboard-stats"],
    queryFn: () => dashboardApi.getStats().then((r) => r.data),
    refetchInterval: 30_000,
  });

  return (
    <DashboardLayout>
      <div className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="text-white/40 text-sm mt-1">Overview of Exyra Technologies</p>
        </div>
        <Link href="/schedule" className="btn-primary">
          <Calendar size={14} />
          New Class
        </Link>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Active Batches"
          value={isLoading ? "—" : data?.total_batches ?? 0}
          icon={BookOpen}
          color="indigo"
          subtitle="Running courses"
        />
        <StatCard
          title="Total Students"
          value={isLoading ? "—" : data?.total_students ?? 0}
          icon={Users}
          color="purple"
          subtitle="Enrolled & active"
        />
        <StatCard
          title="Today's Classes"
          value={isLoading ? "—" : data?.todays_classes ?? 0}
          icon={Calendar}
          color="blue"
          subtitle="Scheduled today"
        />
        <StatCard
          title="Attendance Rate"
          value={isLoading ? "—" : `${data?.attendance_rate ?? 0}%`}
          icon={TrendingUp}
          color="green"
          subtitle="This week"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Upcoming Classes */}
        <div className="xl:col-span-2 surface">
          <div className="px-6 py-5 border-b border-white/5 flex items-center justify-between">
            <h2 className="section-title mb-0">Upcoming Classes</h2>
            <Link href="/schedule" className="text-indigo-400 hover:text-indigo-300 text-xs flex items-center gap-1">
              View all <ChevronRight size={12} />
            </Link>
          </div>
          <div className="p-4 space-y-2">
            {isLoading && (
              <div className="space-y-2">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-16 bg-white/5 rounded-xl animate-pulse" />
                ))}
              </div>
            )}
            {!isLoading && (!data?.upcoming_classes || data.upcoming_classes.length === 0) && (
              <div className="py-12 text-center">
                <Calendar size={32} className="text-white/10 mx-auto mb-3" />
                <p className="text-white/30 text-sm">No upcoming classes scheduled</p>
                <Link href="/schedule" className="btn-primary mt-4 inline-flex">
                  Schedule a class
                </Link>
              </div>
            )}
            {data?.upcoming_classes?.map((cls) => (
              <motion.div
                key={cls.id}
                whileHover={{ x: 2 }}
                className="flex items-center gap-4 p-3 rounded-xl hover:bg-white/3 transition-colors group"
              >
                <div
                  className="w-1 h-10 rounded-full flex-shrink-0"
                  style={{ backgroundColor: cls.batch_color }}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm font-medium truncate">{cls.batch_name}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <Clock size={11} className="text-white/30" />
                    <p className="text-white/40 text-xs">{formatDateTime(cls.scheduled_at)}</p>
                    {cls.topic && <span className="text-white/20">·</span>}
                    {cls.topic && <p className="text-white/30 text-xs truncate">{cls.topic}</p>}
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span className="text-white/20 text-xs">{cls.duration_minutes}m</span>
                  {cls.meet_link && (
                    <a
                      href={cls.meet_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-indigo-400 hover:text-indigo-300 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <ExternalLink size={13} />
                    </a>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Batch Breakdown */}
          <div className="surface">
            <div className="px-6 py-5 border-b border-white/5 flex items-center justify-between">
              <h2 className="section-title mb-0">Batches</h2>
              <Link href="/batches" className="text-indigo-400 text-xs flex items-center gap-1">
                Manage <ChevronRight size={12} />
              </Link>
            </div>
            <div className="p-4 space-y-2">
              {data?.batch_breakdown?.map((batch) => (
                <Link key={batch.id} href={`/batches/${batch.id}`}>
                  <div className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/3 transition-colors">
                    <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: batch.color }} />
                    <div className="flex-1 min-w-0">
                      <p className="text-white text-sm font-medium truncate">{batch.name}</p>
                      <p className="text-white/30 text-xs">{batch.course}</p>
                    </div>
                    <span className="text-white/30 text-xs bg-white/5 px-2 py-0.5 rounded-full">
                      {batch.student_count}
                    </span>
                  </div>
                </Link>
              ))}
              {!isLoading && (!data?.batch_breakdown || data.batch_breakdown.length === 0) && (
                <div className="py-6 text-center">
                  <p className="text-white/30 text-xs">No batches yet</p>
                  <Link href="/batches" className="text-indigo-400 text-xs mt-2 inline-block">Create batch →</Link>
                </div>
              )}
            </div>
          </div>

          {/* Recent Notifications */}
          <div className="surface">
            <div className="px-6 py-5 border-b border-white/5 flex items-center justify-between">
              <h2 className="section-title mb-0">Recent Alerts</h2>
              <Link href="/notifications" className="text-indigo-400 text-xs flex items-center gap-1">
                View all <ChevronRight size={12} />
              </Link>
            </div>
            <div className="p-4 space-y-2">
              {data?.recent_notifications?.map((n) => (
                <div key={n.id} className="flex items-start gap-3 p-2 rounded-lg">
                  <div className={`w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0 ${n.status === "sent" ? "bg-green-400" : n.status === "failed" ? "bg-red-400" : "bg-yellow-400"}`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-white/60 text-xs capitalize">{n.category.replace("_", " ")}</p>
                    <p className="text-white/25 text-[10px] mt-0.5">{n.sent_at ? formatRelative(n.sent_at) : "Pending"}</p>
                  </div>
                  <StatusBadge status={n.status} className="text-[10px]" />
                </div>
              ))}
              {!isLoading && (!data?.recent_notifications || data.recent_notifications.length === 0) && (
                <p className="text-white/20 text-xs text-center py-4">No notifications yet</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
