// Cache để chơi được khi không có mạng (chỉ chạy khi web ở https). Lấy mạng trước, mất mạng thì dùng bản đã lưu.
const C='banchim-v4';
const FILES=['./','index.html','icon.png','manifest.json','audio/index.json','audio/silence.mp3'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(FILES)));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))));self.clients.claim()});
self.addEventListener('fetch',e=>{
  if(new URL(e.request.url).origin!==location.origin)return; // giọng đọc online: để trình duyệt tự xử lý
  e.respondWith(fetch(e.request).then(r=>{const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp));return r}).catch(()=>caches.match(e.request)))});
