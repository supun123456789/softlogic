const CACHE = "jobtracker-v1";
const ASSETS = ["./","./index.html","./manifest.json"];

self.addEventListener("install", e=>{
  e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)));
});
self.addEventListener("activate", e=>{
  e.waitUntil(
    caches.keys().then(keys=>Promise.all(keys.map(k=> k!==CACHE && caches.delete(k))))
  );
});
self.addEventListener("fetch", e=>{
  const url = new URL(e.request.url);
  // Cache-first for same-origin GETs
  if(e.request.method==="GET" && url.origin===location.origin){
    e.respondWith(
      caches.match(e.request).then(r=> r || fetch(e.request).then(res=>{
        const clone = res.clone();
        caches.open(CACHE).then(c=>c.put(e.request, clone));
        return res;
      }).catch(()=>caches.match("./index.html")))
    );
  }
});
