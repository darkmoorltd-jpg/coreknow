import Constants from "expo-constants";

const BASE =
  (Constants.expoConfig?.extra?.apiUrl as string) ||
  "https://coreknow.onrender.com";

async function get(path: string) {
  const r = await fetch(BASE + path);
  return r.json();
}

async function post(path: string, body: any) {
  const r = await fetch(BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return r.json();
}

export const admin = {
  listLessons: (adminId: string) =>
    get('/api/admin/lessons?admin_id=' + adminId),
  saveLesson: (data: any) => post('/api/admin/lesson/save', data),
  bulkImport: (data: any) => post('/api/admin/bulk-import', data),
  versions: (lessonId: number, adminId: string) =>
    get('/api/admin/lesson/' + lessonId + '/versions?admin_id=' + adminId),
  rollback: (lessonId: number, adminId: string, version: number) =>
    post('/api/admin/lesson/' + lessonId + '/rollback', { admin_id: adminId, version }),
  schedule: (adminId: string, lessonId: number, publishAt: string) =>
    post('/api/admin/schedule', { admin_id: adminId, lesson_id: lessonId, publish_at: publishAt }),
  schedules: (adminId: string) =>
    get('/api/admin/schedules?admin_id=' + adminId),
  analytics: (adminId: string) =>
    get('/api/admin/analytics?admin_id=' + adminId),
  trackRead: (userId: string, lessonId: number, seconds: number, completed: boolean) =>
    post('/api/lesson/read', { user_id: userId, lesson_id: lessonId, seconds_spent: seconds, completed }),
};
