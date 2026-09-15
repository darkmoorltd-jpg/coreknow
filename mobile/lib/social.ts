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

export const social = {
  // Groups
  createGroup: (data: any) => post('/api/groups/create', data),
  listGroups: (userId: string) => get('/api/groups/list?user_id=' + userId),
  joinGroup: (userId: string, fullName: string, groupId: number = 0, joinCode: string = '') =>
    post('/api/groups/join', { group_id: groupId, join_code: joinCode, user_id: userId, full_name: fullName }),
  groupDetail: (groupId: number) => get('/api/groups/' + groupId),
  // Forum
  createThread: (data: any) => post('/api/forum/thread/create', data),
  listThreads: (subject: string = '') =>
    get('/api/forum/threads' + (subject ? '?subject=' + encodeURIComponent(subject) : '')),
  threadDetail: (threadId: number) => get('/api/forum/thread/' + threadId),
  createReply: (threadId: number, userId: string, authorName: string, body: string) =>
    post('/api/forum/reply/create', { thread_id: threadId, user_id: userId, author_name: authorName, body }),
  vote: (targetType: string, targetId: number, userId: string) =>
    post('/api/forum/vote', { target_type: targetType, target_id: targetId, user_id: userId }),
  // Friends
  requestFriend: (userId: string, friendEmail: string) =>
    post('/api/friends/request', { user_id: userId, friend_email: friendEmail }),
  listFriends: (userId: string) => get('/api/friends/' + userId),
  respondFriend: (userId: string, friendId: string, accept: boolean) =>
    post('/api/friends/respond', { user_id: userId, friend_id: friendId, accept }),
  // Challenges
  listChallenges: (userId: string) => get('/api/challenges?user_id=' + userId),
  joinChallenge: (challengeId: number, userId: string) =>
    post('/api/challenges/join', { challenge_id: challengeId, user_id: userId }),
  updateProgress: (challengeId: number, userId: string, progress: number) =>
    post('/api/challenges/progress', { challenge_id: challengeId, user_id: userId, progress }),
  challengeLeaderboard: (challengeId: number) =>
    get('/api/challenges/' + challengeId + '/leaderboard'),
};
