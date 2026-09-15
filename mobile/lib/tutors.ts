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

export const tutors = {
  apply: (data: any) => post('/api/tutors/apply', data),
  list: (subject: string = '') =>
    get('/api/tutors/list' + (subject ? '?subject=' + encodeURIComponent(subject) : '')),
  detail: (tutorId: number) => get('/api/tutors/' + tutorId),
  book: (data: any) => post('/api/tutors/book', data),
  confirmPayment: (bookingId: number, paymentRef: string) =>
    post('/api/tutors/booking/confirm', { booking_id: bookingId, payment_ref: paymentRef }),
  bookings: (userId: string, asTutor: boolean = false) =>
    get('/api/tutors/bookings/' + userId + '?as_tutor=' + (asTutor ? 'true' : 'false')),
  review: (bookingId: number, studentId: string, rating: number, comment: string) =>
    post('/api/tutors/review', { booking_id: bookingId, student_id: studentId, rating, comment }),
  verify: (adminId: string, tutorId: number, verified: boolean) =>
    post('/api/tutors/verify', { admin_id: adminId, tutor_id: tutorId, verified }),
  pending: (adminId: string) =>
    get('/api/tutors/pending?admin_id=' + adminId),
  // Live classes
  createLive: (data: any) => post('/api/live/create', data),
  listLive: (subject: string = '') =>
    get('/api/live/list' + (subject ? '?subject=' + encodeURIComponent(subject) : '')),
  enrollLive: (classId: number, studentId: string, paymentRef: string = '') =>
    post('/api/live/enroll', { class_id: classId, student_id: studentId, payment_ref: paymentRef }),
  liveDetail: (classId: number) => get('/api/live/' + classId),
};
