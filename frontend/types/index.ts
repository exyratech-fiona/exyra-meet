export type UserRole = "admin" | "trainer" | "student";

export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface Batch {
  id: string;
  name: string;
  description?: string;
  course: string;
  trainer_id?: string;
  status: "active" | "paused" | "completed" | "cancelled";
  timezone: string;
  default_start_time?: string;
  default_duration_minutes: number;
  recurrence_type: "daily" | "weekly" | "custom";
  recurrence_days?: number[];
  color: string;
  max_students: number;
  student_count?: number;
  google_meet_link?: string;
  custom_meet_link?: string;
  start_date?: string;
  end_date?: string;
  created_at: string;
}

export interface Student {
  id: string;
  full_name: string;
  email: string;
  whatsapp_number?: string;
  phone_number?: string;
  batch_id?: string;
  status: "active" | "inactive" | "on_hold" | "completed";
  avatar_url?: string;
  fee_paid: boolean;
  fee_amount?: string;
  notes?: string;
  whatsapp_notifications: boolean;
  email_notifications: boolean;
  enrolled_at: string;
  created_at: string;
}

export interface Schedule {
  id: string;
  batch_id: string;
  title?: string;
  topic?: string;
  scheduled_at: string;
  duration_minutes: number;
  timezone: string;
  meet_link?: string;
  google_calendar_event_id?: string;
  status: "scheduled" | "ongoing" | "completed" | "cancelled" | "rescheduled";
  is_recurring: boolean;
  original_scheduled_at?: string;
  reschedule_reason?: string;
  reminder_sent_24h: boolean;
  reminder_sent_1h: boolean;
  notifications_sent: boolean;
  created_at: string;
}

export interface Attendance {
  student_id: string;
  name: string;
  email: string;
  status: "present" | "absent" | "late" | "excused";
  joined_at?: string;
}

export interface NotificationLog {
  id: string;
  batch_id?: string;
  schedule_id?: string;
  notification_type: "whatsapp" | "email" | "both";
  category: string;
  status: "pending" | "sent" | "failed" | "partial";
  recipient_name?: string;
  recipient_email?: string;
  subject?: string;
  message_body?: string;
  is_bulk: boolean;
  total_recipients?: string;
  success_count?: string;
  sent_at?: string;
  created_at: string;
}

export interface DashboardStats {
  total_batches: number;
  total_students: number;
  todays_classes: number;
  upcoming_classes: UpcomingClass[];
  recent_notifications: RecentNotification[];
  attendance_rate: number;
  batch_breakdown: BatchBreakdown[];
}

export interface UpcomingClass {
  id: string;
  batch_name: string;
  batch_color: string;
  scheduled_at: string;
  topic?: string;
  meet_link?: string;
  duration_minutes: number;
}

export interface RecentNotification {
  id: string;
  category: string;
  type: string;
  status: string;
  recipient_name?: string;
  sent_at?: string;
}

export interface BatchBreakdown {
  id: string;
  name: string;
  course: string;
  color: string;
  student_count: number;
}
