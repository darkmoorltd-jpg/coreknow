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

export const api = {
  touchStreak: (uid: string) => post('/api/streaks/touch/' + uid, {}),
  getStreak: (uid: string) => get('/api/streaks/' + uid),
  toggleBookmark: (uid: string, lid: number) => post('/api/bookmarks/toggle', { user_id: uid, lesson_id: lid }),
  getBookmarks: (uid: string) => get('/api/bookmarks/' + uid),
  saveNote: (uid: string, lid: number, content: string) => post('/api/notes/save', { user_id: uid, lesson_id: lid, content }),
  getNote: (uid: string, lid: number) => get('/api/notes/' + uid + '/' + lid),
  getMcqs: (subject: string, topic: number = 0, limit: number = 10) =>
    get('/api/mcqs?subject=' + subject + '&topic=' + topic + '&limit=' + limit),
  saveReminder: (uid: string, enabled: boolean, hour: number) =>
    post('/api/reminders/save', { user_id: uid, enabled, hour }),
  getReminder: (uid: string) => get('/api/reminders/' + uid),
  getBadges: (uid: string) => get('/api/badges/' + uid),
  awardBadge: (uid: string, key: string) => post('/api/badges/award', { user_id: uid, badge_key: key }),
  linkParent: (parentId: string, childEmail: string) => post('/api/parent/link', { parent_id: parentId, child_email: childEmail }),
  getParentDashboard: (parentId: string) => get('/api/parent/dashboard/' + parentId),
};