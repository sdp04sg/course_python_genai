from app.content._build import lesson, question, section

CONTENT = {
    "sd-approach": lesson(
        "System design interviews and real design reviews follow the same path: clarify requirements, estimate scale, sketch a simple design, then go deeper on the riskiest parts and explain the trade-offs.",
        [
            section(
                "A repeatable framework",
                "Work in steps and say them out loud. Start with **requirements**: functional (what users can do) and non-functional (scale, latency, availability, consistency, cost). Ask questions instead of assuming. Then **estimate** the load, define the **API** and the **data model**, and draw a **high-level design** that works end to end. Only then **deep-dive** into the bottlenecks and failure cases, and finish with the **trade-offs**: what you chose, what you gave up and what you'd change at ten times the scale. Here is the framework applied to a URL shortener:",
                r'''
                1. Requirements   functional: shorten a URL, redirect, custom alias, expiry
                                  non-functional: 100M new links/month, redirects < 50 ms at p99, 99.99% available
                2. Estimates      ~40 writes/s, ~4,000 redirects/s (100 reads per write), ~6 TB over 10 years
                3. API            POST /v1/links {long_url} -> {short_url};  GET /{code} -> 302 redirect
                4. Data model     links(code PK, long_url, owner_id, created_at, expires_at)
                5. High level     client -> load balancer -> stateless app servers -> cache -> database
                6. Deep dives     generating codes, cache hit ratio, very popular links, abuse and rate limits
                7. Trade-offs     302 vs 301, SQL vs key-value store, how fresh click analytics must be
                ''',
                "text",
            ),
            section(
                "Requirements drive everything",
                "The same product needs very different designs at different scales. Ten thousand users fit on one server with PostgreSQL; a hundred million need caching, replicas and partitioning. Non-functional requirements decide the hard choices: strong consistency for money, availability and low latency for social feeds. Write down your assumptions, design the simplest thing that meets them, then evolve it. Interviewers care more about your reasoning and trade-offs than about one 'right' answer.",
            ),
        ],
        [
            "Clarify functional and non-functional requirements before drawing any boxes.",
            "Estimate the scale early; it decides which components you need at all.",
            "Start with a simple design that works end to end, then scale the bottlenecks.",
            "Always state trade-offs: what you gained and what you gave up.",
        ],
        r'''
        PASTEBIN: one-page design

        Functional
          - Create a paste (text up to 1 MB), get a short link, optional expiry (10 minutes to never)
          - Read a paste by its link; raw view; no editing
        Non-functional
          - 1M new pastes a day, 10 reads per write, reads < 100 ms at p99, 99.9% available
          - Pastes never change, so they're easy to cache; durability matters (no lost pastes)

        Estimates
          writes:  1M / 86,400 s ≈ 12/s   (peak x5 ≈ 60/s)
          reads:   ≈ 120/s                (peak ≈ 600/s)
          storage: 1M x 10 KB average = 10 GB/day ≈ 3.6 TB/year of content, plus small metadata

        API
          POST /v1/pastes {content, expires_in}  -> 201 {id, url}
          GET  /v1/pastes/{id}                   -> 200 {content, created_at} | 404 | 410 (expired)

        Data
          metadata (PostgreSQL): pastes(id PK, object_key, size, created_at, expires_at)
          content (object storage such as S3): key = id, immutable blobs

        High-level design
          client -> CDN -> load balancer -> stateless API servers -> Redis cache (hot pastes)
                                                                  -> PostgreSQL (metadata)
                                                                  -> object storage (content)
          background job: delete expired pastes every hour

        Trade-offs
          - Content in object storage keeps the database small, at the cost of one extra hop on a cache miss
          - Random 8-character base62 ids (≈ 218 trillion) can't be guessed; check for the rare collision on insert
          - CDN caching of immutable pastes cuts read load, but deleting one early needs a CDN purge
        ''',
        [
            question("What should you do first in a system design discussion?",
                     ["Pick a database", "Clarify requirements and constraints", "Draw microservices", "Write code"], 1,
                     "Designs only make sense against requirements; jumping to components is the most common mistake."),
            question("Which is a non-functional requirement?",
                     ["Users can upload photos", "Redirects return within 50 ms at p99", "Users can follow each other", "Admins can delete posts"], 1,
                     "Non-functional requirements describe how well the system works: speed, scale, availability, cost."),
            question("Why estimate scale early?",
                     ["Interviewers require arithmetic", "Scale decides which components (caches, replicas, shards) are needed at all",
                      "To choose a programming language", "It isn't useful"], 1,
                     "A design for 100 requests a second looks nothing like one for 100,000."),
        ],
        "text",
    ),
    "sd-estimation": lesson(
        "Back-of-the-envelope estimates turn vague scale into numbers you can design for: requests per second, storage, bandwidth and the number of machines.",
        [
            section(
                "Useful numbers",
                "Round aggressively: the goal is the right order of magnitude. A day has 86,400 seconds (call it 100,000), so 1 million requests a day is only about 12 a second. Memory is roughly 1,000 times faster than an SSD read, and an SSD read is roughly 1,000 times faster than a round trip across an ocean. A single well-tuned app server handles thousands of simple requests per second; a single PostgreSQL primary handles thousands to tens of thousands of simple queries per second.",
                r'''
                Powers of ten            Latency (rough)                     Per day
                thousand = 10^3          main memory read      100 ns        86,400 s ≈ 10^5 s
                million  = 10^6          SSD random read       100 µs        1M requests/day   ≈ 12/s
                billion  = 10^9          same-datacentre trip  0.5 ms        100M requests/day ≈ 1,200/s
                1 KB = 10^3 bytes        disk seek             10 ms
                1 GB = 10^9 bytes        US <-> Europe trip    80-150 ms
                1 TB = 10^12 bytes
                ''',
                "text",
            ),
            section(
                "Estimate with code",
                "Write an estimate as a few lines of arithmetic, so the assumptions are visible and easy to change. Average load isn't enough: multiply by a peak factor (often 2 to 5 times), and keep headroom so losing one server doesn't overload the rest.",
                r'''
                DAILY_USERS = 10_000_000
                READS_PER_USER = 50            # feed views, profile views
                WRITES_PER_USER = 2            # posts, comments
                PEAK_FACTOR = 3
                SECONDS_PER_DAY = 86_400

                read_qps = DAILY_USERS * READS_PER_USER / SECONDS_PER_DAY
                write_qps = DAILY_USERS * WRITES_PER_USER / SECONDS_PER_DAY
                print(f"reads:  {read_qps:,.0f}/s average, {read_qps * PEAK_FACTOR:,.0f}/s at peak")
                print(f"writes: {write_qps:,.0f}/s average, {write_qps * PEAK_FACTOR:,.0f}/s at peak")

                SERVER_CAPACITY = 2_000        # requests per second one app server handles comfortably
                servers = (read_qps + write_qps) * PEAK_FACTOR / SERVER_CAPACITY
                print(f"app servers at peak: {servers:.0f}, plus 1 or 2 spares for failures")
                ''',
            ),
        ],
        [
            "Aim for the right order of magnitude, not precision; round freely.",
            "1 million requests a day is only about 12 per second on average.",
            "Plan for peak load (2 to 5 times the average) plus headroom for failures.",
            "Memory is about 1,000 times faster than an SSD read, which is about 1,000 times faster than crossing an ocean.",
        ],
        r'''
        """Back-of-the-envelope estimate for a photo-sharing app."""

        DAILY_ACTIVE_USERS = 20_000_000
        UPLOADS_PER_USER_PER_DAY = 0.5          # one photo every other day
        VIEWS_PER_USER_PER_DAY = 100
        PHOTO_SIZE_MB = 2                       # the original; thumbnails add about 10%
        THUMBNAIL_OVERHEAD = 1.1
        REPLICATION = 3                         # copies kept for durability
        PEAK_FACTOR = 3
        YEARS = 5
        SECONDS_PER_DAY = 86_400

        uploads_per_day = DAILY_ACTIVE_USERS * UPLOADS_PER_USER_PER_DAY
        views_per_day = DAILY_ACTIVE_USERS * VIEWS_PER_USER_PER_DAY

        upload_qps = uploads_per_day / SECONDS_PER_DAY
        view_qps = views_per_day / SECONDS_PER_DAY
        print(f"uploads: {upload_qps:,.0f}/s average, {upload_qps * PEAK_FACTOR:,.0f}/s at peak")
        print(f"views:   {view_qps:,.0f}/s average, {view_qps * PEAK_FACTOR:,.0f}/s at peak")
        print(f"read:write ratio = {views_per_day / uploads_per_day:.0f}:1")

        storage_per_day_tb = uploads_per_day * PHOTO_SIZE_MB * THUMBNAIL_OVERHEAD / 1_000_000
        total_pb = storage_per_day_tb * 365 * YEARS * REPLICATION / 1_000
        print(f"new storage: {storage_per_day_tb:,.0f} TB/day; {YEARS} years with {REPLICATION} copies: {total_pb:,.0f} PB")

        # Most views load a ~200 KB feed-sized image, not the original.
        egress_gbps = view_qps * PEAK_FACTOR * 200_000 * 8 / 1e9
        print(f"peak egress for 200 KB images: {egress_gbps:,.0f} Gbit/s, so serve images from a CDN")
        ''',
        [
            question("About how many requests per second is 1 million requests per day?", ["1", "12", "1,000", "86,400"], 1,
                     "1,000,000 / 86,400 ≈ 11.6."),
            question("Why multiply the average load by a peak factor?",
                     ["To impress interviewers", "Traffic isn't flat; systems must survive daily peaks and big events", "Servers are slower at night", "To account for logging"], 1,
                     "Evening peaks, launches and live events can be several times the daily average."),
            question("Which is fastest?",
                     ["Reading from main memory", "A random SSD read", "A round trip within a data centre", "A transatlantic round trip"], 0,
                     "Roughly 100 ns, 100 µs, 0.5 ms and 100 ms respectively."),
        ],
    ),
    "sd-load-balancing": lesson(
        "Horizontal scaling adds more servers behind a load balancer. It works when servers are stateless, and the balancing algorithm decides how evenly the load spreads.",
        [
            section(
                "Scale up or scale out",
                "**Vertical scaling** (a bigger machine) is simple but has a ceiling and leaves a single point of failure. **Horizontal scaling** (more machines) has no hard ceiling and survives failures, but it needs a load balancer and **stateless** servers: keep sessions, uploads and caches in shared stores such as Redis, a database or object storage, so any server can handle any request.\n\nLoad balancers work at layer 4 (TCP: fast, but unaware of HTTP) or layer 7 (HTTP: they can route by path or header, terminate TLS and retry). Both run health checks and stop sending traffic to servers that fail them.",
                r'''
                                  +--> app-1 (stateless) --+
                client --> LB ----+--> app-2 (stateless) --+--> Redis (sessions, cache)
                (TLS ends here)   +--> app-3 (stateless) --+--> PostgreSQL (data)

                health check: GET /health every 5 s; failing servers are taken out of rotation
                ''',
                "text",
            ),
            section(
                "Balancing algorithms",
                "**Round robin** cycles through the servers: simple, but blind to how busy each one is. **Weighted round robin** sends more traffic to bigger servers. **Least connections** picks the server with the fewest requests in progress, which copes with slow requests. **Hashing** (by client IP or user ID) sends a client to the same server each time, which helps caching. **Power of two choices** picks two servers at random and uses the less busy one: nearly as good as least connections, with far less coordination. This simulation shows why being load-aware matters when some requests are slow:",
                r'''
                import itertools
                import random
                import statistics

                random.seed(42)
                SERVERS = ["app-1", "app-2", "app-3"]
                # One request arrives every millisecond. Most take 2 ms; 1 in 50 is a slow report taking 40 ms.
                COSTS = [40 if random.random() < 0.02 else 2 for _ in range(20_000)]


                def simulate(choose) -> list[int]:
                    free_at = {server: 0 for server in SERVERS}     # when each server finishes its queued work
                    waits = []
                    for now, cost in enumerate(COSTS):
                        server = choose(free_at)
                        start = max(free_at[server], now)
                        waits.append(start - now)
                        free_at[server] = start + cost
                    return waits


                def report(name: str, waits: list[int]) -> None:
                    p99 = statistics.quantiles(waits, n=100)[98]
                    print(f"{name:12} average wait {statistics.mean(waits):5.1f} ms, p99 wait {p99:5.1f} ms")


                rotation = itertools.cycle(SERVERS)
                report("round robin", simulate(lambda free_at: next(rotation)))
                report("least loaded", simulate(lambda free_at: min(SERVERS, key=free_at.get)))
                ''',
            ),
        ],
        [
            "Scale out with stateless servers behind a load balancer; keep state in shared stores.",
            "Layer 7 balancers understand HTTP; layer 4 balancers are faster but blind to it.",
            "Load-aware algorithms (least connections, power of two choices) cut tail latency when request costs vary.",
            "Health checks take failed servers out of rotation automatically.",
        ],
        r'''
        import itertools
        import random
        import statistics

        SERVERS = [f"app-{i}" for i in range(1, 6)]
        rng = random.Random(1)
        # 5 servers, one request every 0.8 ms; most take 2 ms, 1 in 50 takes 40 ms (about 70% busy).
        ARRIVALS = [i * 0.8 for i in range(40_000)]
        COSTS = [40 if rng.random() < 0.02 else 2 for _ in ARRIVALS]


        def simulate(choose) -> list[float]:
            free_at = {server: 0.0 for server in SERVERS}
            waits = []
            for now, cost in zip(ARRIVALS, COSTS):
                server = choose(free_at)
                start = max(free_at[server], now)
                waits.append(start - now)
                free_at[server] = start + cost
            return waits


        rotation = itertools.cycle(SERVERS)
        picker = random.Random(7)
        strategies = {
            "round robin": lambda free_at: next(rotation),
            "random": lambda free_at: picker.choice(SERVERS),
            "power of two": lambda free_at: min(picker.sample(SERVERS, 2), key=free_at.get),
            "least loaded": lambda free_at: min(SERVERS, key=free_at.get),
        }

        print(f"{'strategy':14}{'avg wait':>10}{'p99 wait':>10}")
        for name, choose in strategies.items():
            waits = simulate(choose)
            p99 = statistics.quantiles(waits, n=100)[98]
            print(f"{name:14}{statistics.mean(waits):9.1f}ms{p99:9.1f}ms")
        # Round robin and random queue requests behind slow reports. Load-aware strategies route around
        # them, and power of two gets most of the benefit while looking at only two servers.
        ''',
        [
            question("Why must servers be stateless to scale horizontally?",
                     ["Stateless servers are faster", "Any server must be able to handle any request, so state lives in shared stores",
                      "Load balancers can't route to stateful servers", "It saves memory"], 1,
                     "If a session lives in one server's memory, losing or bypassing that server logs the user out."),
            question("Request costs vary a lot. Which algorithm usually gives lower tail latency?",
                     ["Round robin", "Least connections", "Alphabetical order", "Always the first server"], 1,
                     "Least connections avoids piling new requests behind a server that's busy with slow ones."),
            question("What can a layer 7 load balancer do that a layer 4 one can't?",
                     ["Forward TCP connections", "Route by URL path or HTTP header", "Use IP addresses", "Run health checks"], 1,
                     "Both can run health checks; only a layer 7 balancer reads HTTP."),
        ],
    ),
    "sd-caching": lesson(
        "Caching keeps frequently used data in fast storage close to where it's needed. It's the most effective way to scale reads, as long as you handle expiry and invalidation.",
        [
            section(
                "Where and how to cache",
                "Caches exist at every layer: the browser, a **CDN** at the network edge, an in-process cache, a shared cache such as Redis or Memcached, and the database's own buffer cache. The most common pattern is **cache-aside**: read from the cache; on a miss, read the database and store the result with a TTL (time to live). **Write-through** writes the cache and the database together; **write-back** writes the cache first and the database later, which is fast but can lose data. Track the **hit ratio**: at 90%, only 10% of reads reach the database.",
                r'''
                import time

                cache: dict[str, tuple[float, dict]] = {}
                TTL_SECONDS = 60
                database_reads = 0


                def load_user_from_db(user_id: str) -> dict:
                    global database_reads
                    database_reads += 1
                    return {"id": user_id, "name": f"User {user_id}"}


                def get_user(user_id: str) -> dict:
                    entry = cache.get(user_id)
                    if entry and entry[0] > time.monotonic():          # fresh cache hit
                        return entry[1]
                    user = load_user_from_db(user_id)                  # miss: go to the database
                    cache[user_id] = (time.monotonic() + TTL_SECONDS, user)
                    return user


                for _ in range(1_000):
                    get_user("42")
                print("database reads for 1,000 requests:", database_reads)   # 1
                ''',
            ),
            section(
                "Eviction and invalidation",
                "Memory is limited, so caches **evict** entries: LRU (least recently used) is the usual default, and LFU keeps frequently used items. Stale data is the hard part. Use TTLs as a safety net, and **delete** (rather than update) the cache key when the data changes. Watch out for a **cache stampede**: when a hot key expires, thousands of requests hit the database at once. Prevent it with a lock so only one request refreshes the value, by refreshing early, or by adding random jitter to TTLs.",
                r'''
                from collections import OrderedDict


                class LRUCache:
                    def __init__(self, capacity: int):
                        self.capacity = capacity
                        self.items: OrderedDict[str, object] = OrderedDict()

                    def get(self, key: str):
                        if key not in self.items:
                            return None
                        self.items.move_to_end(key)              # mark as most recently used
                        return self.items[key]

                    def put(self, key: str, value) -> None:
                        self.items[key] = value
                        self.items.move_to_end(key)
                        if len(self.items) > self.capacity:
                            self.items.popitem(last=False)       # evict the least recently used


                cache = LRUCache(2)
                cache.put("a", 1)
                cache.put("b", 2)
                cache.get("a")              # "a" is now the most recently used
                cache.put("c", 3)           # evicts "b"
                print(list(cache.items))    # ['a', 'c']
                ''',
            ),
            section(
                "CDNs",
                "A content delivery network caches responses in data centres close to users, which cuts latency and offloads your servers. Serve static assets with long cache lifetimes and content-hashed file names, and let the CDN cache public API responses for short periods. Never cache personalised responses in shared caches: mark them `Cache-Control: private` or `no-store`.",
            ),
        ],
        [
            "Cache-aside: check the cache, fall back to the database, store the result with a TTL.",
            "Delete cache keys when data changes, and keep TTLs as a safety net against stale data.",
            "LRU eviction keeps the recently used items when memory runs out.",
            "Protect hot keys from stampedes with locking, early refresh or TTL jitter.",
        ],
        r'''
        from collections import OrderedDict


        class TTLLRUCache:
            """An LRU cache whose entries also expire after `ttl` seconds. `clock` is injectable for tests."""

            def __init__(self, capacity: int, ttl: float, clock):
                self.capacity, self.ttl, self.clock = capacity, ttl, clock
                self.items: OrderedDict[str, tuple[float, object]] = OrderedDict()
                self.hits = self.misses = 0

            def get(self, key: str):
                entry = self.items.get(key)
                if entry is None or entry[0] <= self.clock():
                    self.items.pop(key, None)        # missing or expired
                    self.misses += 1
                    return None
                self.items.move_to_end(key)
                self.hits += 1
                return entry[1]

            def put(self, key: str, value) -> None:
                self.items[key] = (self.clock() + self.ttl, value)
                self.items.move_to_end(key)
                while len(self.items) > self.capacity:
                    self.items.popitem(last=False)

            def delete(self, key: str) -> None:
                self.items.pop(key, None)


        now = [0.0]
        database = {"course:1": "Python", "course:2": "SQL", "course:3": "Docker"}
        db_reads: list[str] = []
        cache = TTLLRUCache(capacity=2, ttl=30, clock=lambda: now[0])


        def get_course(key: str) -> str:
            value = cache.get(key)
            if value is None:
                db_reads.append(key)
                value = database[key]
                cache.put(key, value)
            return value


        def rename_course(key: str, title: str) -> None:
            database[key] = title
            cache.delete(key)                    # invalidate: the next read loads fresh data


        for key in ["course:1", "course:1", "course:2", "course:1", "course:3", "course:2"]:
            get_course(key)
        print("db reads:", db_reads)             # course:2 was evicted by course:3, so it's read twice

        rename_course("course:2", "PostgreSQL and SQL")
        print(get_course("course:2"))           # PostgreSQL and SQL: not stale

        now[0] += 31                             # time passes beyond the TTL
        get_course("course:2")                   # expired, so it's loaded again
        print("hits:", cache.hits, "misses:", cache.misses, "db reads:", len(db_reads))
        ''',
        [
            question("In cache-aside, what happens on a cache miss?",
                     ["Return an error", "Read the database, store the result in the cache and return it", "Wait for the cache to fill", "Write to the database"], 1,
                     "The application fills the cache lazily, so only data that's actually requested gets cached."),
            question("Which eviction policy removes the item that has gone unused the longest?", ["FIFO", "LRU", "Random", "LFU"], 1,
                     "Least recently used assumes recently used data is likely to be used again soon."),
            question("A popular key expires and 10,000 requests hit the database at once. What is this called?",
                     ["Cache warming", "A cache stampede (thundering herd)", "Write-back", "Sharding"], 1,
                     "Let one request refresh the value while the others wait or get the old one."),
        ],
    ),
    "sd-rate-limiting": lesson(
        "Rate limiting protects services from abuse and overload by capping how many requests each client can make. The token bucket is the classic algorithm.",
        [
            section(
                "Why and where",
                "Rate limits stop abuse (password guessing, scraping), stop one noisy client from hurting everyone else, and control cost (AI model calls are expensive). Apply global rules at the API gateway or load balancer and finer rules inside services. Key limits by API key, user or IP address. When a client goes over its limit, return `429 Too Many Requests` with a `Retry-After` header so well-behaved clients know when to try again.",
                r'''
                HTTP/1.1 429 Too Many Requests
                Retry-After: 12
                RateLimit-Limit: 100
                RateLimit-Remaining: 0
                Content-Type: application/problem+json

                {"title": "Too many requests", "status": 429, "detail": "The limit is 100 requests per minute."}
                ''',
                "http",
            ),
            section(
                "Algorithms",
                "A **fixed window** counts requests per clock minute: simple, but a client can send double the limit around a window boundary. A **sliding window log** stores every timestamp: exact but memory-hungry. A **sliding window counter** blends the current and previous window counts: accurate enough and cheap. A **token bucket** refills tokens at a steady rate up to a capacity, and each request spends one, so it allows short bursts while enforcing an average rate. With many servers, keep counters in a shared store such as Redis and update them atomically.",
                r'''
                class TokenBucket:
                    def __init__(self, rate: float, capacity: int, clock):
                        self.rate, self.capacity, self.clock = rate, capacity, clock
                        self.tokens = float(capacity)
                        self.updated = clock()

                    def allow(self) -> bool:
                        now = self.clock()
                        self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
                        self.updated = now
                        if self.tokens >= 1:
                            self.tokens -= 1
                            return True
                        return False


                now = [0.0]
                bucket = TokenBucket(rate=2, capacity=5, clock=lambda: now[0])   # 2 requests/s, bursts of 5
                print([bucket.allow() for _ in range(7)])   # five True, then False, False
                now[0] += 1.0                               # one second later: 2 new tokens
                print([bucket.allow() for _ in range(3)])   # True, True, False
                ''',
            ),
        ],
        [
            "Rate limits prevent abuse, protect capacity and control cost.",
            "Return 429 with Retry-After so well-behaved clients back off.",
            "A token bucket allows short bursts while enforcing an average rate.",
            "Distributed limiters keep counters in a shared store and update them atomically.",
        ],
        r'''
        from collections import defaultdict


        class TokenBucket:
            def __init__(self, rate: float, capacity: int, clock):
                self.rate, self.capacity, self.clock = rate, capacity, clock
                self.tokens, self.updated = float(capacity), clock()

            def allow(self) -> bool:
                now = self.clock()
                self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
                self.updated = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
                return False

            def retry_after(self) -> float:
                return max(0.0, (1 - self.tokens) / self.rate)


        class SlidingWindowCounter:
            """Estimates the last `window` seconds by weighting the previous fixed window's count."""

            def __init__(self, limit: int, window: float, clock):
                self.limit, self.window, self.clock = limit, window, clock
                self.counts: dict[int, int] = defaultdict(int)

            def allow(self) -> bool:
                now = self.clock()
                current = int(now // self.window)
                elapsed_fraction = (now % self.window) / self.window
                estimated = self.counts[current] + self.counts[current - 1] * (1 - elapsed_fraction)
                if estimated >= self.limit:
                    return False
                self.counts[current] += 1
                return True


        now = [0.0]


        def clock() -> float:
            return now[0]                # a fake clock keeps the test instant and repeatable


        limiters = defaultdict(lambda: TokenBucket(rate=1, capacity=3, clock=clock))
        assert [limiters["alice"].allow() for _ in range(4)] == [True, True, True, False]   # burst of 3
        assert limiters["bob"].allow()                       # each client has its own bucket
        print(f"alice should retry after {limiters['alice'].retry_after():.1f}s")           # 1.0s
        now[0] += 1
        assert limiters["alice"].allow()                     # one token has refilled

        window = SlidingWindowCounter(limit=10, window=60, clock=clock)
        now[0] = 50
        assert sum(window.allow() for _ in range(15)) == 10  # 10 allowed in the first minute
        now[0] = 70                                          # 10 s into the next minute
        # The estimate starts at 10 x (50/60) ≈ 8.3, so two more requests fit before it reaches 10.
        assert sum(window.allow() for _ in range(5)) == 2
        print("All rate-limiter checks passed.")
        ''',
        [
            question("Which status code tells a client it has been rate limited?", ["403", "429", "503", "409"], 1,
                     "429 Too Many Requests, ideally with a Retry-After header."),
            question("What is the weakness of a fixed-window counter?",
                     ["It uses too much memory", "Clients can send up to twice the limit around a window boundary", "It can't be distributed", "It never resets"], 1,
                     "A client can use the full limit at 0:59 and again at 1:00."),
            question("A token bucket has capacity 10 and refills 1 token per second. What does it allow?",
                     ["Exactly 1 request per second, never more", "Bursts of up to 10, with an average of 1 per second", "10 requests per second", "Unlimited requests"], 1,
                     "Saved-up tokens allow a burst; the refill rate sets the long-run average."),
        ],
    ),
    "sd-databases": lesson(
        "Replication copies data to several servers for availability and read capacity. It forces a choice between consistency and availability when the network fails, which is what the CAP theorem describes.",
        [
            section(
                "Leader-follower replication",
                "The most common setup has one **leader** (primary) that accepts writes and several **followers** (replicas) that copy its changes. Reads can go to replicas, which scales reads and keeps the data available if the leader fails, because a follower can be promoted. Replication is usually asynchronous, so replicas lag slightly: a user who just saved a change may read the old value from a replica. Fix that with **read-your-writes**: send a user's reads to the leader for a short time after they write.",
                r'''
                writes --> leader --(asynchronous replication, lag of a few ms)--> replica 1 --> reads
                                  \--------------------------------------------> replica 2 --> reads
                ''',
                "text",
            ),
            section(
                "CAP and consistency models",
                "The **CAP theorem** says that during a network partition a distributed store must choose between **consistency** (every read sees the latest write, or fails) and **availability** (every request gets an answer, possibly a stale one). Partitions do happen, so the real choice is how to behave during one. **PACELC** adds that even without a partition you trade latency against consistency. Consistency is a spectrum: strong (linearizable), read-your-writes, monotonic reads, causal and eventual consistency. This simulation shows replication lag:",
                r'''
                class ReplicatedStore:
                    def __init__(self, lag: float, clock):
                        self.lag, self.clock = lag, clock
                        self.leader: dict[str, str] = {}
                        self.log: list[tuple[float, str, str]] = []     # (time, key, value) to replicate

                    def write(self, key: str, value: str) -> None:
                        self.leader[key] = value
                        self.log.append((self.clock(), key, value))

                    def read_replica(self, key: str) -> str | None:
                        visible = [value for at, k, value in self.log if k == key and at + self.lag <= self.clock()]
                        return visible[-1] if visible else None

                    def read_leader(self, key: str) -> str | None:
                        return self.leader.get(key)


                now = [0.0]
                store = ReplicatedStore(lag=0.5, clock=lambda: now[0])
                store.write("bio:ada", "Loves algorithms")
                print("replica:", store.read_replica("bio:ada"))   # None: not replicated yet
                print("leader: ", store.read_leader("bio:ada"))    # Loves algorithms
                now[0] += 1
                print("replica:", store.read_replica("bio:ada"))   # Loves algorithms: caught up
                ''',
            ),
        ],
        [
            "Replicas scale reads and provide failover; the leader handles writes.",
            "Asynchronous replication means replicas lag, so recent writes may not be visible yet.",
            "Read-your-writes: route a user's reads to the leader for a short time after they write.",
            "During a partition you choose consistency or availability (CAP); decide per feature.",
        ],
        r'''
        class ReplicatedStore:
            """A leader plus one asynchronous replica that applies each write `lag` seconds later."""

            def __init__(self, lag: float, clock):
                self.lag, self.clock = lag, clock
                self.leader: dict[str, str] = {}
                self.log: list[tuple[float, str, str]] = []

            def write(self, key: str, value: str) -> None:
                self.leader[key] = value
                self.log.append((self.clock(), key, value))

            def read_leader(self, key: str) -> str | None:
                return self.leader.get(key)

            def read_replica(self, key: str) -> str | None:
                visible = [value for at, k, value in self.log if k == key and at + self.lag <= self.clock()]
                return visible[-1] if visible else None


        class Router:
            """Sends reads to the replica, except for users who wrote within the last `window` seconds."""

            def __init__(self, store: ReplicatedStore, window: float, clock):
                self.store, self.window, self.clock = store, window, clock
                self.last_write: dict[str, float] = {}
                self.replica_reads = self.leader_reads = 0

            def write(self, user: str, key: str, value: str) -> None:
                self.store.write(key, value)
                self.last_write[user] = self.clock()

            def read(self, user: str, key: str) -> str | None:
                if self.clock() - self.last_write.get(user, float("-inf")) < self.window:
                    self.leader_reads += 1
                    return self.store.read_leader(key)
                self.replica_reads += 1
                return self.store.read_replica(key)


        now = [0.0]


        def clock() -> float:
            return now[0]


        store = ReplicatedStore(lag=2.0, clock=clock)
        router = Router(store, window=5.0, clock=clock)

        router.write("ada", "profile:ada", "v1")
        now[0] = 10
        router.write("ada", "profile:ada", "v2")
        assert router.read("ada", "profile:ada") == "v2"      # Ada sees her own write immediately
        assert router.read("bob", "profile:ada") == "v1"      # Bob may briefly see the old value
        now[0] = 13
        assert router.read("bob", "profile:ada") == "v2"      # the replica has caught up
        now[0] = 20
        assert router.read("ada", "profile:ada") == "v2"      # Ada's window has ended; the replica serves her
        print(f"leader reads: {router.leader_reads}, replica reads: {router.replica_reads}")   # 1 and 3
        ''',
        [
            question("Why might a user not see their own update right after saving it?",
                     ["The write failed", "Their read went to a replica that hasn't received the write yet", "Caches never update", "HTTP is stateless"], 1,
                     "This is replication lag; read-your-writes routing hides it from the user who wrote."),
            question("According to the CAP theorem, what must a distributed store choose between during a network partition?",
                     ["Speed and cost", "Consistency and availability", "SQL and NoSQL", "Reads and writes"], 1,
                     "It can refuse requests to stay correct (CP) or answer with possibly stale data (AP)."),
            question("What do read replicas mainly scale?", ["Writes", "Reads", "The size of each row", "Write bandwidth"], 1,
                     "Every replica still applies every write, so replicas don't add write capacity; sharding does."),
        ],
    ),
    "sd-sharding": lesson(
        "When one database server can't hold the data or keep up with the writes, partition (shard) the data across several. Consistent hashing keeps the data movement small when servers are added or removed.",
        [
            section(
                "Partitioning strategies",
                "**Range partitioning** assigns key ranges to shards (A to F, G to M, and so on). It's good for range scans but creates hot spots, such as every new order landing on the shard with the newest dates. **Hash partitioning** assigns `hash(key) mod N`: load spreads evenly, but range queries hit every shard, and changing N moves almost every key. **Directory-based** partitioning keeps a lookup table, which is flexible but adds a component to run. Choose a partition key that appears in most queries and spreads the load, because joins and transactions across shards are expensive.",
                r'''
                import hashlib


                def shard_for(key: str, shards: int) -> int:
                    return int(hashlib.md5(key.encode()).hexdigest(), 16) % shards


                keys = [f"user:{i}" for i in range(10_000)]
                moved = sum(shard_for(k, 4) != shard_for(k, 5) for k in keys)
                print(f"adding a 5th shard with mod-N hashing moves {moved / len(keys):.0%} of keys")   # about 80%
                ''',
            ),
            section(
                "Consistent hashing",
                "**Consistent hashing** places servers and keys on a ring of hash values; each key belongs to the next server clockwise. Adding a server only takes keys from its neighbours, so about 1/N of the keys move instead of nearly all of them. Each server gets many **virtual nodes** on the ring, which evens out the load and spreads a failed server's keys across all the others. DynamoDB, Cassandra and many distributed caches use this idea.",
                r'''
                import bisect
                import hashlib


                def ring_hash(value: str) -> int:
                    return int(hashlib.md5(value.encode()).hexdigest(), 16)


                class HashRing:
                    def __init__(self, nodes: list[str], vnodes: int = 100):
                        self.vnodes = vnodes
                        self.ring: list[tuple[int, str]] = []
                        for node in nodes:
                            self.add(node)

                    def add(self, node: str) -> None:
                        for i in range(self.vnodes):
                            bisect.insort(self.ring, (ring_hash(f"{node}#{i}"), node))

                    def node_for(self, key: str) -> str:
                        index = bisect.bisect(self.ring, (ring_hash(key), ""))
                        return self.ring[index % len(self.ring)][1]      # wrap around the ring


                ring = HashRing(["db-a", "db-b", "db-c"])
                print(ring.node_for("user:42"))
                ''',
            ),
        ],
        [
            "Shard when one server can't handle the data size or the write load.",
            "Range partitioning helps range scans but risks hot spots; hash partitioning spreads load.",
            "With mod-N hashing, changing N moves most keys; consistent hashing moves about 1/N.",
            "Choose a partition key that's in most queries, and avoid cross-shard joins and transactions.",
        ],
        r'''
        import bisect
        import hashlib
        from collections import Counter


        def ring_hash(value: str) -> int:
            return int(hashlib.md5(value.encode()).hexdigest(), 16)


        class HashRing:
            def __init__(self, nodes: list[str], vnodes: int = 100):
                self.vnodes = vnodes
                self.ring: list[tuple[int, str]] = []
                for node in nodes:
                    self.add(node)

            def add(self, node: str) -> None:
                for i in range(self.vnodes):
                    bisect.insort(self.ring, (ring_hash(f"{node}#{i}"), node))

            def remove(self, node: str) -> None:
                self.ring = [entry for entry in self.ring if entry[1] != node]

            def node_for(self, key: str) -> str:
                index = bisect.bisect(self.ring, (ring_hash(key), ""))
                return self.ring[index % len(self.ring)][1]


        keys = [f"user:{i}" for i in range(50_000)]

        for vnodes in (1, 100):
            ring = HashRing(["db-a", "db-b", "db-c", "db-d"], vnodes=vnodes)
            before = {key: ring.node_for(key) for key in keys}
            print(f"vnodes={vnodes:<3} keys per node: {sorted(Counter(before.values()).values())}")
            ring.add("db-e")
            moved = sum(before[key] != ring.node_for(key) for key in keys)
            print(f"           adding db-e moved {moved / len(keys):.0%} of keys (ideal: 20%)")

        ring.remove("db-e")
        assert all(before[key] == ring.node_for(key) for key in keys)   # removing it restores the old layout

        mod_moved = sum(ring_hash(key) % 4 != ring_hash(key) % 5 for key in keys)
        print(f"mod-N hashing, 4 -> 5 nodes, moved {mod_moved / len(keys):.0%} of keys")
        ''',
        [
            question("With hash(key) mod N, roughly what share of keys move when N goes from 4 to 5?", ["20%", "50%", "80%", "0%"], 2,
                     "A key stays put only if hash mod 4 equals hash mod 5, which is true for about 1 key in 5."),
            question("Why do consistent hashing rings use virtual nodes?",
                     ["To encrypt keys", "To spread load evenly and share a failed node's keys among many nodes", "To make hashing faster", "To support SQL"], 1,
                     "With one position per node, the arcs between nodes are very uneven; many positions average that out."),
            question("Orders are range-partitioned by creation date. What problem appears?",
                     ["Range queries are slow", "All new orders hit one shard (a hot spot)", "Keys can't be found", "There are too many shards"], 1,
                     "The newest range takes every insert while the other shards sit idle."),
        ],
    ),
    "sd-queues": lesson(
        "Message queues decouple services: producers hand off work and carry on, while consumers process it at their own pace. Because messages can be delivered more than once, consumers must be idempotent.",
        [
            section(
                "Queues, pub/sub and logs",
                "A **queue** (RabbitMQ, Amazon SQS) delivers each message to one consumer, which suits background jobs such as sending emails or resizing images. **Publish/subscribe** delivers each message to every subscribed service. A **log** (Kafka) keeps an ordered, replayable stream that many consumer groups read at their own pace. Queues absorb traffic spikes, let services fail independently and make retries easy. The cost is eventual consistency and more moving parts to monitor, such as queue depth and consumer lag.",
                r'''
                                                   +--> email-service     (sends the receipt)
                order-service --> "order.created" -+--> analytics-service (updates dashboards)
                (returns 201 at once)              +--> warehouse-service (reserves stock)
                ''',
                "text",
            ),
            section(
                "Delivery guarantees and idempotency",
                "Most systems give **at-least-once** delivery: if a consumer crashes before acknowledging a message, it's delivered again, so duplicates happen. **At-most-once** never duplicates but can lose messages. In practice, 'exactly once' means at-least-once delivery plus **idempotent** consumers: record each processed message ID, in the same transaction as the side effect, and skip duplicates. Messages that keep failing go to a **dead-letter queue** after a few attempts, so one bad message doesn't block the rest. To publish events reliably alongside a database write, use the **outbox pattern**: write the event to an outbox table in the same transaction, and let a relay publish it.",
                r'''
                import random
                from collections import deque

                random.seed(3)
                queue = deque({"id": f"msg-{i}", "amount": 10} for i in range(5))
                processed_ids: set[str] = set()
                balance = 0

                while queue:
                    message = queue.popleft()
                    if message["id"] in processed_ids:
                        continue                              # a duplicate delivery: skip it
                    balance += message["amount"]              # the side effect
                    processed_ids.add(message["id"])          # in real code: in the same transaction
                    if random.random() < 0.4:                 # crash before acknowledging: redelivered later
                        queue.append(message)

                print("balance:", balance)   # always 50, however many duplicates arrived
                ''',
            ),
        ],
        [
            "Queues decouple producers from consumers and absorb traffic spikes.",
            "At-least-once delivery is the norm, so design consumers to be idempotent.",
            "Retry with backoff, then move poison messages to a dead-letter queue.",
            "The outbox pattern publishes events reliably alongside database writes.",
        ],
        r'''
        import json
        import sqlite3
        from collections import deque

        db = sqlite3.connect(":memory:")
        db.executescript("""
            CREATE TABLE orders (id TEXT PRIMARY KEY, total REAL);
            CREATE TABLE processed_messages (message_id TEXT PRIMARY KEY);
        """)

        MAX_ATTEMPTS = 3
        queue: deque = deque()
        dead_letters: list[tuple[str, str]] = []


        def publish(message_id: str, payload: dict) -> None:
            queue.append({"id": message_id, "body": json.dumps(payload), "attempts": 0})


        def handle(message: dict) -> None:
            order = json.loads(message["body"])
            if order["total"] < 0:
                raise ValueError("negative total")
            with db:   # one transaction: the order and the "processed" marker commit together
                seen = db.execute("SELECT 1 FROM processed_messages WHERE message_id = ?", (message["id"],)).fetchone()
                if seen:
                    return
                db.execute("INSERT INTO orders VALUES (?, ?)", (order["order_id"], order["total"]))
                db.execute("INSERT INTO processed_messages VALUES (?)", (message["id"],))


        def run_worker() -> None:
            while queue:
                message = queue.popleft()
                try:
                    handle(message)
                except Exception as error:
                    message["attempts"] += 1
                    if message["attempts"] >= MAX_ATTEMPTS:
                        dead_letters.append((message["id"], str(error)))
                    else:
                        queue.append(message)            # retry later (real queues add a backoff delay)


        publish("m1", {"order_id": "A-1", "total": 30.0})
        publish("m2", {"order_id": "A-2", "total": 12.5})
        publish("m1", {"order_id": "A-1", "total": 30.0})    # a duplicate delivery of m1
        publish("m3", {"order_id": "A-3", "total": -5})      # a poison message
        run_worker()

        print(db.execute("SELECT id, total FROM orders ORDER BY id").fetchall())   # [('A-1', 30.0), ('A-2', 12.5)]
        print("dead letters:", dead_letters)                                       # [('m3', 'negative total')]
        ''',
        [
            question("With at-least-once delivery, what must consumers handle?",
                     ["Lost messages", "Duplicate messages", "Out-of-memory errors", "Encryption"], 1,
                     "A message is redelivered whenever its acknowledgement doesn't arrive, even if it was processed."),
            question("What makes a consumer idempotent?",
                     ["Processing messages faster", "Processing the same message twice has the same effect as processing it once", "Using Kafka", "Acknowledging before processing"], 1,
                     "Usually by recording processed message IDs or using naturally idempotent writes such as upserts."),
            question("What is a dead-letter queue for?",
                     ["Deleted users", "Messages that keep failing, so they don't block the rest", "High-priority messages", "Encrypted messages"], 1,
                     "Engineers inspect dead letters, fix the cause, and replay them."),
        ],
    ),
    "sd-reliability": lesson(
        "Everything fails eventually. Reliable systems expect it: they set timeouts, retry carefully, stop calling broken dependencies, degrade gracefully, and measure reliability against clear targets.",
        [
            section(
                "Availability, redundancy and SLOs",
                "Availability is the share of time a service works: 99.9% allows about 8.8 hours of downtime a year, and 99.99% about 53 minutes. Components in series multiply, so three 99.9% services in a chain give about 99.7%, while redundant copies in parallel fail only if all of them fail. An **SLI** is a measurement (the share of requests faster than 300 ms), an **SLO** is the target for it (99.9% over 30 days), and the **error budget** is the failure you're allowed (0.1%). While budget remains, teams ship faster; when it's spent, they focus on reliability.",
                r'''
                HOURS_PER_YEAR = 365 * 24

                for target in (0.99, 0.999, 0.9999):
                    print(f"{target:.2%} available -> {(1 - target) * HOURS_PER_YEAR:6.2f} hours of downtime a year")

                series = 0.999 * 0.999 * 0.999            # load balancer, app and database are all required
                parallel = 1 - (1 - 0.99) ** 2            # either of two redundant 99% replicas will do
                print(f"three 99.9% services in series: {series:.2%}")
                print(f"two 99% replicas in parallel:   {parallel:.2%}")
                ''',
            ),
            section(
                "Timeouts, retries and circuit breakers",
                "Every network call needs a **timeout**, or one slow dependency ties up all your workers. **Retry** only temporary failures and idempotent operations, a limited number of times, with **exponential backoff and jitter** so clients don't retry in synchronised waves. A **circuit breaker** stops calling a dependency that keeps failing: after several failures it **opens** and fails fast; after a cool-down it goes **half-open** and lets a trial request through, closing again if that succeeds. **Bulkheads** give each dependency its own connection pool so one can't exhaust everything, and **graceful degradation** serves something useful, such as cached or default content, instead of an error.",
                r'''
                import random


                def backoff_delays(attempts: int, base: float = 0.1, cap: float = 5.0) -> list[float]:
                    """'Full jitter': a random delay between 0 and an exponentially growing ceiling."""
                    return [random.uniform(0, min(cap, base * 2 ** attempt)) for attempt in range(attempts)]


                random.seed(1)
                print([round(delay, 2) for delay in backoff_delays(6)])   # ceilings: 0.1, 0.2, 0.4, 0.8, 1.6, 3.2 s
                ''',
            ),
        ],
        [
            "Each extra nine of availability cuts the allowed downtime tenfold; dependencies in series multiply.",
            "Set a timeout on every remote call.",
            "Retry only temporary failures of idempotent operations, with exponential backoff and jitter.",
            "Circuit breakers fail fast while a dependency is down, and test its recovery with trial requests.",
        ],
        r'''
        import random


        class CircuitOpenError(Exception):
            pass


        class CircuitBreaker:
            def __init__(self, failure_threshold: int, reset_timeout: float, clock):
                self.failure_threshold, self.reset_timeout, self.clock = failure_threshold, reset_timeout, clock
                self.failures = 0
                self.opened_at: float | None = None

            @property
            def state(self) -> str:
                if self.opened_at is None:
                    return "closed"
                return "half-open" if self.clock() - self.opened_at >= self.reset_timeout else "open"

            def call(self, func):
                if self.state == "open":
                    raise CircuitOpenError("failing fast: the dependency is unhealthy")
                try:
                    result = func()
                except Exception:
                    self.failures += 1
                    if self.state == "half-open" or self.failures >= self.failure_threshold:
                        self.opened_at = self.clock()      # open, or re-open after a failed trial
                    raise
                self.failures, self.opened_at = 0, None    # success closes the circuit
                return result


        def call_with_retries(breaker: CircuitBreaker, func, attempts: int = 3, sleep=lambda seconds: None):
            for attempt in range(attempts):
                try:
                    return breaker.call(func)
                except CircuitOpenError:
                    raise                                  # don't retry into an open circuit
                except ConnectionError:
                    if attempt == attempts - 1:
                        raise
                    sleep(random.uniform(0, 0.1 * 2 ** attempt))   # exponential backoff with full jitter


        now = [0.0]
        healthy = [False]


        def inventory_service() -> dict:
            if not healthy[0]:
                raise ConnectionError("inventory timed out")
            return {"sku": "BOOK-1", "in_stock": 12}


        breaker = CircuitBreaker(failure_threshold=3, reset_timeout=30, clock=lambda: now[0])

        for request in range(3):
            try:
                call_with_retries(breaker, inventory_service)
            except (ConnectionError, CircuitOpenError) as error:
                print(f"request {request}: {type(error).__name__}, circuit {breaker.state}")
        # request 0: ConnectionError, circuit open    (three failed attempts opened it)
        # requests 1 and 2: CircuitOpenError          (failed fast, adding no load to the service)

        now[0] += 31
        healthy[0] = True                                  # the service has recovered
        print(call_with_retries(breaker, inventory_service), breaker.state)   # the trial succeeds -> closed
        ''',
        [
            question("Roughly how much downtime a year does 99.9% availability allow?", ["53 minutes", "8.8 hours", "3.7 days", "5 minutes"], 1,
                     "0.1% of 8,760 hours is 8.76 hours; 99.99% allows about 53 minutes."),
            question("Why add jitter to retry backoff?",
                     ["To make retries faster", "So many clients don't retry at the same moment and overload the recovering service", "To encrypt requests", "HTTP requires it"], 1,
                     "Without jitter, clients that failed together retry together, in waves."),
            question("What does an open circuit breaker do?",
                     ["Sends every request twice", "Fails fast without calling the unhealthy dependency", "Restarts the server", "Logs the request"], 1,
                     "Failing fast protects your own threads and gives the dependency room to recover."),
        ],
    ),
    "sd-microservices": lesson(
        "Microservices split a system into independently deployable services. They solve team-scaling problems but add distributed-systems complexity, so start with a well-structured monolith and split when there's a clear reason.",
        [
            section(
                "Monolith first, then split by business capability",
                "A **monolith** is one deployable application: simple to develop, test, deploy and debug, with local function calls and one database. **Microservices** split the system by business capability (orders, payments, catalog); each owns its data and is deployed independently, so teams can ship and scale separately. The costs are network calls that fail, distributed data and transactions, harder debugging and much more infrastructure. A **modular monolith**, with clear internal boundaries, gets most of the structure without the network, and makes extracting a service later much easier.",
                r'''
                Modular monolith                         Microservices
                +-------------------------------+        gateway -> orders-svc   -> orders DB
                | orders | payments | catalog   |                -> payments-svc -> payments DB
                |  (modules with clear APIs)    |                -> catalog-svc  -> catalog DB
                +---------------+---------------+        events between services: order.created, ...
                                |
                          one database
                ''',
                "text",
            ),
            section(
                "Communication and distributed transactions",
                "Services talk **synchronously** (REST or gRPC: simple, but the caller waits, and fails when the callee fails) or **asynchronously** through events on a broker (decoupled and resilient, but eventually consistent). An **API gateway** gives clients one entry point and handles authentication, rate limits and routing. Each service owns its database, so a business transaction spanning services can't use one ACID transaction. A **saga** splits it into local steps, each with a **compensating action** that undoes it if a later step fails. A central orchestrator can run the steps, or services can react to each other's events (choreography).",
                r'''
                def run_saga(steps) -> bool:
                    completed = []
                    for name, action, compensate in steps:
                        try:
                            action()
                        except Exception as error:
                            print(f"{name} failed: {error}. Compensating...")
                            for done_name, undo in reversed(completed):
                                undo()
                                print(f"  undid {done_name}")
                            return False
                        completed.append((name, compensate))
                    return True


                def charge_card():
                    raise RuntimeError("card declined")


                ok = run_saga([
                    ("reserve stock", lambda: print("stock reserved"), lambda: print("stock released")),
                    ("charge card", charge_card, lambda: print("refund issued")),
                    ("book courier", lambda: print("courier booked"), lambda: print("courier cancelled")),
                ])
                print("order confirmed" if ok else "order cancelled")
                ''',
            ),
        ],
        [
            "Start with a modular monolith; split out services for clear team or scaling reasons.",
            "Each microservice owns its data: no shared database.",
            "Prefer asynchronous events between services where eventual consistency is acceptable.",
            "Sagas replace distributed transactions with local steps and compensating actions.",
        ],
        r'''
        class Inventory:
            def __init__(self, stock: dict[str, int]):
                self.stock = stock

            def reserve(self, sku: str, qty: int) -> None:
                if self.stock.get(sku, 0) < qty:
                    raise RuntimeError(f"not enough {sku}")
                self.stock[sku] -= qty

            def release(self, sku: str, qty: int) -> None:
                self.stock[sku] += qty


        class Payments:
            def __init__(self, declined_cards: set[str]):
                self.declined = declined_cards
                self.charges: dict[str, float] = {}

            def charge(self, order_id: str, card: str, amount: float) -> None:
                if card in self.declined:
                    raise RuntimeError("card declined")
                self.charges[order_id] = amount

            def refund(self, order_id: str) -> None:
                self.charges.pop(order_id, None)


        class Shipping:
            def __init__(self, available: bool = True):
                self.available = available
                self.bookings: set[str] = set()

            def book(self, order_id: str) -> None:
                if not self.available:
                    raise RuntimeError("no couriers available")
                self.bookings.add(order_id)

            def cancel(self, order_id: str) -> None:
                self.bookings.discard(order_id)


        def place_order(order: dict, inventory: Inventory, payments: Payments, shipping: Shipping) -> str:
            steps = [
                ("reserve stock",
                 lambda: inventory.reserve(order["sku"], order["qty"]),
                 lambda: inventory.release(order["sku"], order["qty"])),
                ("charge card",
                 lambda: payments.charge(order["id"], order["card"], order["amount"]),
                 lambda: payments.refund(order["id"])),
                ("book courier",
                 lambda: shipping.book(order["id"]),
                 lambda: shipping.cancel(order["id"])),
            ]
            completed = []
            for name, action, compensate in steps:
                try:
                    action()
                except RuntimeError as error:
                    for undo in reversed(completed):
                        undo()
                    return f"cancelled at '{name}': {error}"
                completed.append(compensate)
            return "confirmed"


        inventory, payments = Inventory({"BOOK-1": 5}), Payments(declined_cards={"4000-0000"})
        order = {"id": "o-1", "sku": "BOOK-1", "qty": 2, "card": "4242-4242", "amount": 19.98}
        print(place_order(order, inventory, payments, Shipping()))                                # confirmed
        print(place_order({**order, "id": "o-2", "card": "4000-0000"}, inventory, payments, Shipping()))
        print(place_order({**order, "id": "o-3"}, inventory, payments, Shipping(available=False)))

        assert inventory.stock["BOOK-1"] == 3       # only o-1's reservation remains
        assert set(payments.charges) == {"o-1"}     # o-3's charge was refunded
        ''',
        [
            question("What is a good default architecture for a new product built by one small team?",
                     ["Dozens of microservices", "A modular monolith", "A serverless function for every endpoint", "One service per database table"], 1,
                     "It keeps development fast and leaves the door open to extracting services later."),
            question("Why shouldn't microservices share one database?",
                     ["Databases can't handle it", "Shared tables couple the services, so they can't change or deploy independently", "It's slower", "It's against the law"], 1,
                     "A schema change for one service could break all the others."),
            question("How does a saga handle a failure in step 3 of 4?",
                     ["It rolls back a database transaction", "It runs the compensating actions for steps 2 and 1", "It retries forever", "It ignores the failure"], 1,
                     "Compensations run in reverse order, undoing the work already committed."),
        ],
    ),
    "sd-url-shortener": lesson(
        "A URL shortener is the classic first system design problem: simple features, very high read traffic and an interesting ID-generation problem.",
        [
            section(
                "Requirements and estimates",
                "Functional: create a short link for a long URL (optionally with a custom alias and an expiry date) and redirect visitors. Non-functional: very fast redirects, high availability, codes that can't be guessed in sequence, and read-heavy traffic. Assume 100 million new links a month and 100 reads per write: about 40 writes and 4,000 redirects per second on average, and about 6 TB of data over 10 years at 500 bytes per link. Seven base62 characters give 62^7 ≈ 3.5 trillion codes, far more than the 12 billion links needed.",
                r'''
                POST /v1/links  {"long_url": "https://example.com/a/very/long/path", "alias": null, "expires_at": null}
                     -> 201 {"code": "aZ3k9Qx", "short_url": "https://sho.rt/aZ3k9Qx"}

                GET  /aZ3k9Qx   -> 302 Found, Location: https://example.com/a/very/long/path
                                -> 404 if unknown, 410 Gone if expired

                links table: code (primary key) | long_url | owner_id | created_at | expires_at
                ''',
                "text",
            ),
            section(
                "Generating short codes",
                "Options: **hash the URL** and keep the first 7 base62 characters (you must check for collisions); **encode a unique counter** in base62 (no collisions, but sequential codes are guessable, so scramble the number first); or pre-generate **random codes** in a key-generation service. A single global counter is a bottleneck and a single point of failure, so give each server a block of IDs (for example 1,000 at a time), or use Snowflake-style IDs built from a timestamp, a machine ID and a sequence number.",
                r'''
                import string

                ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase   # 62 characters


                def encode(number: int) -> str:
                    if number == 0:
                        return ALPHABET[0]
                    chars = []
                    while number:
                        number, remainder = divmod(number, 62)
                        chars.append(ALPHABET[remainder])
                    return "".join(reversed(chars))


                def decode(code: str) -> int:
                    number = 0
                    for char in code:
                        number = number * 62 + ALPHABET.index(char)
                    return number


                print(encode(125), encode(62**7 - 1))     # 21 ZZZZZZZ
                assert decode(encode(987_654_321)) == 987_654_321
                ''',
            ),
            section(
                "Redirects, caching and scale",
                "Redirects dominate the traffic, so cache `code -> long URL` in Redis or at the CDN, where a small set of popular links serves most requests. A **301** (permanent) redirect is cached by browsers, which saves load but hides repeat clicks from your analytics; a **302** (temporary) sends every click through your service. Record clicks asynchronously through a queue so redirects stay fast. The data is a simple lookup by code, so it shards easily by code. Add rate limits and malicious-URL checks to stop abuse.",
            ),
        ],
        [
            "Estimate first: about 100 reads per write makes caching the core of the design.",
            "Seven base62 characters give about 3.5 trillion codes.",
            "Counter-based codes never collide but need distributing and scrambling; hashed codes need collision checks.",
            "302 keeps analytics accurate; 301 lets browsers cache the redirect.",
        ],
        r'''
        import math
        import string
        import time
        from collections import OrderedDict

        ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase
        MODULUS = 62 ** 7                      # every 7-character code
        MULTIPLIER = 2_305_843_009_213         # coprime with MODULUS, so the scrambling is reversible
        assert math.gcd(MULTIPLIER, MODULUS) == 1


        def encode(number: int, width: int = 7) -> str:
            chars = []
            for _ in range(width):
                number, remainder = divmod(number, 62)
                chars.append(ALPHABET[remainder])
            return "".join(reversed(chars))


        class IdAllocator:
            """Hands out ids in blocks, so app servers rarely touch the shared counter."""

            def __init__(self, block_size: int = 1000):
                self.shared_counter = 1            # in production: a database sequence or Redis INCRBY
                self.block_size = block_size
                self.next_id = self.block_end = 0

            def allocate(self) -> int:
                if self.next_id == self.block_end:
                    self.next_id = self.shared_counter
                    self.shared_counter += self.block_size
                    self.block_end = self.next_id + self.block_size
                self.next_id += 1
                return self.next_id - 1


        class Shortener:
            def __init__(self, cache_size: int = 10_000):
                self.ids = IdAllocator()
                self.links: dict[str, dict] = {}                     # stands in for the database
                self.cache: OrderedDict[str, dict] = OrderedDict()   # stands in for Redis (LRU)
                self.cache_size = cache_size
                self.db_reads = 0

            def create(self, long_url: str, alias: str | None = None, ttl: float | None = None) -> str:
                if not long_url.startswith(("https://", "http://")):
                    raise ValueError("only http(s) URLs can be shortened")
                if alias:
                    if alias in self.links:
                        raise ValueError("alias already taken")
                    code = alias
                else:
                    # Scrambling the counter makes consecutive codes look random and hard to enumerate.
                    code = encode(self.ids.allocate() * MULTIPLIER % MODULUS)
                expires_at = time.time() + ttl if ttl is not None else None
                self.links[code] = {"long_url": long_url, "expires_at": expires_at, "clicks": 0}
                return code

            def resolve(self, code: str) -> tuple[int, str | None]:
                row = self.cache.get(code)
                if row is None:
                    self.db_reads += 1
                    row = self.links.get(code)
                    if row is None:
                        return 404, None
                    self.cache[code] = row
                    if len(self.cache) > self.cache_size:
                        self.cache.popitem(last=False)
                self.cache.move_to_end(code)
                if row["expires_at"] is not None and row["expires_at"] < time.time():
                    return 410, None
                row["clicks"] += 1                  # in production: send a click event to a queue instead
                return 302, row["long_url"]


        service = Shortener()
        codes = [service.create(f"https://example.com/articles/{i}") for i in range(3)]
        print(codes)                                         # three 7-character codes that don't look sequential
        service.create("https://example.com/sale", alias="sale")
        expired = service.create("https://example.com/flash", ttl=-1)   # already expired, for the demo

        for _ in range(1_000):
            service.resolve(codes[0])
        print(service.resolve(codes[0]))                    # (302, 'https://example.com/articles/0')
        print(service.resolve("sale"))                       # (302, 'https://example.com/sale')
        print(service.resolve("nope123"))                    # (404, None)
        print(service.resolve(expired))                      # (410, None)
        print("database reads for 1,004 lookups:", service.db_reads)   # 4: the cache served the rest
        ''',
        [
            question("How many codes do 7 base62 characters give?", ["About 3.5 million", "About 3.5 trillion", "About 62 thousand", "About 7 billion"], 1,
                     "62^7 = 3,521,614,606,208."),
            question("Why might a URL shortener return 302 rather than 301?",
                     ["302 is faster", "Browsers cache 301s, so repeat clicks skip the service and analytics miss them", "301 is deprecated", "302 is more secure"], 1,
                     "301 saves load; 302 keeps every click visible. It's a business trade-off."),
            question("Why scramble a sequential counter before encoding it?",
                     ["To save space", "So codes can't be guessed or listed in order", "Because base62 requires it", "To avoid collisions"], 1,
                     "Counters never collide anyway; a reversible scramble just hides the sequence."),
        ],
    ),
    "sd-news-feed": lesson(
        "A news feed shows each user recent posts from the accounts they follow. The key decision is when to build each feed: when posts are written, when feeds are read, or a mix of both.",
        [
            section(
                "Fan-out on write or on read",
                "**Fan-out on write (push)**: when someone posts, write the post ID into every follower's precomputed feed, for example a Redis list. Reading a feed is then one fast lookup, but a celebrity with 50 million followers triggers 50 million writes, and feeds of inactive users are wasted work. **Fan-out on read (pull)**: when a user opens the feed, fetch recent posts from everyone they follow and merge them. Writes are cheap, but reads are slow for users who follow many accounts. Most large systems use a **hybrid**: push for normal accounts, and pull celebrity posts at read time and merge them in.",
                r'''
                followers = {"ada": ["bob", "cy"], "celebrity": [f"fan{i}" for i in range(1_000_000)]}

                writes_per_post = {author: len(fans) for author, fans in followers.items()}
                print("feed writes per post with fan-out on write:", writes_per_post)
                # {'ada': 2, 'celebrity': 1000000}: one celebrity post means a million feed updates
                ''',
            ),
            section(
                "Storing, ranking and paging feeds",
                "Store posts in a sharded database (by post ID or author) and feeds as capped lists of post IDs in a cache, keeping only the newest few hundred per user. Turn IDs into full posts with one batched cache lookup. Many feeds are ranked by a model (relationship, engagement, recency) rather than by time alone. Page with a cursor (the last post ID or score seen), not an offset, because new posts keep arriving at the top. Serve images and video from object storage through a CDN.",
            ),
        ],
        [
            "Fan-out on write makes reads fast but writes expensive for accounts with many followers.",
            "Fan-out on read makes writes cheap but reads slow.",
            "Hybrid: push for most accounts, and pull celebrity posts at read time.",
            "Keep feeds as capped lists of IDs in a cache, and page with cursors.",
        ],
        r'''
        import heapq
        import itertools
        from collections import defaultdict, deque

        CELEBRITY_THRESHOLD = 1_000          # accounts with more followers are pulled at read time
        FEED_LENGTH = 500

        post_ids = itertools.count(1)        # increasing ids double as timestamps
        followers: dict[str, set[str]] = defaultdict(set)
        following: dict[str, set[str]] = defaultdict(set)
        posts_by_author: dict[str, list[tuple[int, str]]] = defaultdict(list)
        feeds: dict[str, deque] = defaultdict(lambda: deque(maxlen=FEED_LENGTH))
        feed_writes = 0


        def follow(user: str, author: str) -> None:
            followers[author].add(user)
            following[user].add(author)


        def is_celebrity(author: str) -> bool:
            return len(followers[author]) > CELEBRITY_THRESHOLD


        def post(author: str, text: str) -> None:
            global feed_writes
            entry = (next(post_ids), f"{author}: {text}")
            posts_by_author[author].append(entry)
            if not is_celebrity(author):                 # fan-out on write
                for user in followers[author]:
                    feeds[user].appendleft(entry)
                    feed_writes += 1


        def read_feed(user: str, limit: int = 5) -> list[str]:
            pushed = list(feeds[user])[:limit]
            pulled = [                                   # fan-out on read for celebrities
                entry
                for author in following[user] if is_celebrity(author)
                for entry in posts_by_author[author][-limit:]
            ]
            return [text for _, text in heapq.nlargest(limit, pushed + pulled)]


        follow("bob", "ada")
        follow("bob", "grace")
        for i in range(5_000):
            follow(f"fan{i}", "star")
        follow("bob", "star")

        post("ada", "Learning consistent hashing")
        post("star", "New album out!")                  # 5,001 followers: no fan-out
        post("grace", "Shipped the compiler")
        post("ada", "Wrote a rate limiter")

        print(read_feed("bob"))   # newest first, with star's post merged in at read time
        print("feed writes:", feed_writes)              # 3 (one per normal post), not 5,004
        ''',
        [
            question("What is the main drawback of fan-out on write?",
                     ["Slow feed reads", "Posts by accounts with millions of followers cause millions of writes", "It can't rank posts", "It needs SQL"], 1,
                     "Write amplification grows with follower count; this is the celebrity problem."),
            question("How do hybrid feed systems treat celebrity accounts?",
                     ["They ban them", "They pull celebrity posts at read time instead of pushing them to every follower", "They push their posts twice", "They store their posts in SQL only"], 1,
                     "Few accounts are celebrities, so merging their posts at read time is cheap."),
            question("Why page feeds with a cursor rather than an offset?",
                     ["Cursors are shorter", "New posts arriving at the top shift offsets, causing duplicates or skipped posts", "Redis doesn't support offsets", "Cursors are encrypted"], 1,
                     "A cursor says 'older than this post', which stays correct as new posts arrive."),
        ],
    ),
    "sd-chat": lesson(
        "A chat system delivers messages in real time, keeps them in order, works across devices and catches users up when they come back online.",
        [
            section(
                "Real-time connections",
                "HTTP is request-response, but chat needs the server to push messages. The options are **polling** (simple but wasteful), **long polling** (the server holds the request open until there's news), **Server-Sent Events** (one-way server push) and **WebSockets** (a persistent two-way connection), which is the usual choice. Each user connects to one chat server, and a **session service** records which server holds each user's connection, so a message for Ada can be routed to her server. Chat servers talk to each other through a pub/sub system such as Redis or Kafka.",
                r'''
                ada (WebSocket) --> chat-server-1 --> message service: 1. assign the next message id
                                                                       2. store the message
                                                                       3. look up bob's server (session service)
                bob (WebSocket) <-- chat-server-2 <-- pub/sub <-------/
                                                  \-> push notification service, if bob is offline
                ''',
                "text",
            ),
            section(
                "Ordering, delivery and storage",
                "Give every message an ID that increases within its conversation (a per-conversation sequence number, or a time-ordered Snowflake ID), so clients can order messages and notice gaps. Store a message before acknowledging it, keyed by conversation and message ID, in a store built for heavy writes such as Cassandra or a sharded database. Each device remembers the last message ID it has seen and, when it reconnects, asks for everything newer, so offline users catch up. Clients attach their own ID to each message they send, so a retry over a flaky connection doesn't create a duplicate. Delivery and read receipts are just small messages flowing back.",
                r'''
                from collections import defaultdict

                sequences: dict[str, int] = defaultdict(int)
                messages: dict[str, list[dict]] = defaultdict(list)
                seen_client_ids: set[str] = set()


                def send(conversation: str, sender: str, text: str, client_id: str) -> dict | None:
                    if client_id in seen_client_ids:          # a retry of a message we already stored
                        return None
                    seen_client_ids.add(client_id)
                    sequences[conversation] += 1
                    message = {"seq": sequences[conversation], "from": sender, "text": text}
                    messages[conversation].append(message)
                    return message


                def sync(conversation: str, last_seen: int) -> list[dict]:
                    return [m for m in messages[conversation] if m["seq"] > last_seen]


                send("ada-bob", "ada", "Hi Bob!", client_id="ada-1")
                send("ada-bob", "ada", "Hi Bob!", client_id="ada-1")      # a network retry: ignored
                send("ada-bob", "bob", "Hey Ada", client_id="bob-1")
                print(sync("ada-bob", last_seen=0))                     # two messages, numbered 1 and 2
                ''',
            ),
        ],
        [
            "WebSockets keep a two-way connection open so the server can push messages instantly.",
            "A session service maps each user to the chat server holding their connection.",
            "Per-conversation sequence numbers order messages and reveal gaps.",
            "Devices sync from their last seen ID after reconnecting; client IDs make sends safe to retry.",
        ],
        r'''
        import asyncio
        from collections import defaultdict


        class ChatServer:
            """In-memory chat core: rooms, ordered message ids, live delivery and offline catch-up."""

            def __init__(self):
                self.members: dict[str, set[str]] = defaultdict(set)
                self.history: dict[str, list[dict]] = defaultdict(list)
                self.connections: dict[str, asyncio.Queue] = {}   # online users -> their socket's queue
                self.client_ids: set[tuple[str, str]] = set()
                self.notifications: list[str] = []

            def join(self, room: str, user: str) -> None:
                self.members[room].add(user)

            def connect(self, user: str) -> asyncio.Queue:
                self.connections[user] = asyncio.Queue()
                return self.connections[user]

            def disconnect(self, user: str) -> None:
                self.connections.pop(user, None)

            async def send(self, room: str, sender: str, text: str, client_id: str) -> int | None:
                if (sender, client_id) in self.client_ids:
                    return None                                   # a duplicate retry
                self.client_ids.add((sender, client_id))
                message = {"room": room, "seq": len(self.history[room]) + 1, "from": sender, "text": text}
                self.history[room].append(message)                # store first, then deliver
                for member in sorted(self.members[room] - {sender}):
                    if member in self.connections:
                        await self.connections[member].put(message)
                    else:
                        self.notifications.append(f"push to {member}: {sender} says {text!r}")
                return message["seq"]

            def sync(self, room: str, last_seen: int) -> list[dict]:
                return self.history[room][last_seen:]


        async def main() -> None:
            server = ChatServer()
            for user in ("ada", "bob", "cy"):
                server.join("study-group", user)
            bob_inbox = server.connect("bob")
            server.connect("ada")                                 # cy is offline

            await server.send("study-group", "ada", "Who wants to practise system design?", client_id="a1")
            await server.send("study-group", "ada", "Who wants to practise system design?", client_id="a1")  # retry
            await server.send("study-group", "bob", "Me! Let's design a chat app.", client_id="b1")

            live = await bob_inbox.get()
            print("bob received live:", live["seq"], live["text"])
            print("notifications:", server.notifications)        # two pushes to cy

            server.connect("cy")                                  # cy comes online, last seen = 0
            for message in server.sync("study-group", last_seen=0):
                print("cy catches up:", message["seq"], message["from"], message["text"])


        asyncio.run(main())
        ''',
        [
            question("Why do chat apps use WebSockets?",
                     ["They're encrypted by default", "They keep a two-way connection open so the server can push messages instantly", "They replace databases", "They're simpler than HTTP"], 1,
                     "Plain HTTP can only answer requests; WebSockets let the server send whenever a message arrives."),
            question("A phone was offline for an hour. How does it get the messages it missed?",
                     ["They're lost", "It asks the server for messages newer than the last ID it saw", "The server resends every message ever sent", "Other phones forward them"], 1,
                     "Stored messages plus a 'last seen' cursor per device make catch-up a simple range query."),
            question("Why does a client attach its own ID to each message it sends?",
                     ["For encryption", "So the server can ignore duplicates when the client retries", "To sort messages", "To choose a chat server"], 1,
                     "It makes sending idempotent, which matters on flaky mobile networks."),
        ],
    ),
}
