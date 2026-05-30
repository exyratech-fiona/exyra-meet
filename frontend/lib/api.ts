import axios from "axios";
import Cookies from "js-cookie";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = Cookies.get("token") || (typeof window !== "undefined" ? localStorage.getItem("token") : null);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      Cookies.remove("token");
      localStorage.removeItem("token");
      window.location.href = "/auth/login";
    }
    return Promise.reject(err);
  }
);

// Auth
export const authApi = {
  login: (email: string, password: string) =>
    api.post("/api/auth/login", new URLSearchParams({ username: email, password }), {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    }),
  googleLogin: (code: string, redirect_uri?: string) =>
    api.post("/api/auth/google", { code, redirect_uri }),
  register: (data: { email: string; full_name: string; password: string; role?: string }) =>
    api.post("/api/auth/register", data),
  me: () => api.get("/api/auth/me"),
};

// Dashboard
export const dashboardApi = {
  getStats: () => api.get("/api/dashboard/stats"),
};

// Batches
export const batchApi = {
  list: (params?: { status?: string }) => api.get("/api/batches", { params }),
  get: (id: string) => api.get(`/api/batches/${id}`),
  create: (data: object) => api.post("/api/batches", data),
  update: (id: string, data: object) => api.patch(`/api/batches/${id}`, data),
  delete: (id: string) => api.delete(`/api/batches/${id}`),
  getStudents: (id: string) => api.get(`/api/batches/${id}/students`),
};

// Students
export const studentApi = {
  list: (params?: { batch_id?: string; status?: string; search?: string }) =>
    api.get("/api/students", { params }),
  get: (id: string) => api.get(`/api/students/${id}`),
  create: (data: object) => api.post("/api/students", data),
  bulkCreate: (data: object) => api.post("/api/students/bulk", data),
  update: (id: string, data: object) => api.patch(`/api/students/${id}`, data),
  delete: (id: string) => api.delete(`/api/students/${id}`),
};

// Schedules
export const scheduleApi = {
  list: (params?: { batch_id?: string; from_date?: string; to_date?: string; status?: string }) =>
    api.get("/api/schedules", { params }),
  get: (id: string) => api.get(`/api/schedules/${id}`),
  create: (data: object) => api.post("/api/schedules", data),
  update: (id: string, data: object) => api.patch(`/api/schedules/${id}`, data),
  reschedule: (id: string, data: { new_scheduled_at: string; reason?: string; notify_students?: boolean }) =>
    api.post(`/api/schedules/${id}/reschedule`, data),
  cancel: (id: string, params?: { reason?: string; notify_students?: boolean }) =>
    api.post(`/api/schedules/${id}/cancel`, null, { params }),
  sendLink: (id: string) => api.post(`/api/schedules/${id}/send-link`),
};

// Notifications
export const notificationApi = {
  send: (data: object) => api.post("/api/notifications/send", data),
  getLogs: (params?: { batch_id?: string; limit?: number }) =>
    api.get("/api/notifications/logs", { params }),
};

// Attendance
export const attendanceApi = {
  getForSchedule: (scheduleId: string) => api.get(`/api/attendance/${scheduleId}`),
  markAttendance: (scheduleId: string, records: object[]) =>
    api.post(`/api/attendance/${scheduleId}/mark`, records),
  getStudentSummary: (studentId: string, batchId?: string) =>
    api.get(`/api/attendance/student/${studentId}/summary`, { params: { batch_id: batchId } }),
};
