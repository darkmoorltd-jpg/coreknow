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

export const school = {
  createClass: (data: any) => post('/api/school/class/create', data),
  listClasses: (schoolLicenseId: number = 0, teacherId: string = '') =>
    get('/api/school/classes?school_license_id=' + schoolLicenseId + '&teacher_id=' + teacherId),
  joinClass: (joinCode: string, userId: string, fullName: string) =>
    post('/api/school/class/join', { join_code: joinCode, user_id: userId, full_name: fullName }),
  members: (classId: number) => get('/api/school/class/' + classId + '/members'),
  createAssignment: (data: any) => post('/api/school/assignment/create', data),
  listAssignments: (classId: number) => get('/api/school/assignments/' + classId),
  assignmentDetail: (assignmentId: number) => get('/api/school/assignment/' + assignmentId),
  submitAssignment: (assignmentId: number, studentId: string, text: string) =>
    post('/api/school/assignment/submit', { assignment_id: assignmentId, student_id: studentId, text }),
  manualGrade: (assignmentId: number, studentId: string, score: number, feedback: string) =>
    post('/api/school/assignment/manual-grade', { assignment_id: assignmentId, student_id: studentId, score, feedback }),
  analytics: (classId: number) => get('/api/school/analytics/' + classId),
  reportCard: (classId: number, studentId: string) =>
    get('/api/school/report/' + classId + '/' + studentId),
  scheduleExam: (data: any) => post('/api/school/exam/schedule', data),
  listExams: (classId: number) => get('/api/school/exams/' + classId),
};
