## 🔹 Coding Assignment

**Build a Book Inventory API**

**Acceptance criteria:**
- `GET /books` — returns all books as a list
- `GET /books/{book_id}` — returns one book or 404
- `POST /books` — creates a book with `title`, `author`, `year` fields; returns 201
- `DELETE /books/{book_id}` — deletes a book or 404
- Use an in-memory dict as your "database"
- Use a Pydantic model for the POST request body
- Validate that `year` is a positive integer (hint: Pydantic can enforce this with `Field(gt=0)`)

**Edge cases to handle:**
- GET/DELETE on a non-existent ID → 404
- POST with missing fields → FastAPI/Pydantic handles this automatically — verify it returns 422

**Test requirements:**
- At least one test per endpoint
- At least one test for the 404 case
- At least one test verifying the `year` validation rejects a negative value

---

## 🔹 Quick Quiz

**1. Multiple choice:** Which HTTP method is used to *partially update* a resource?
- a) GET
- b) POST
- c) PATCH ✓
- d) PUT

**2. Short answer:** What is the difference between a 401 and a 403 status code?

**3. Multiple choice:** A URL `/getUserById?id=5` violates REST because:
- a) It uses a query parameter
- b) It uses a verb in the URL ✓
- c) It doesn't use JSON
- d) It uses GET

**4. Scenario:** Your API receives a POST request to create a user but the email field is missing. What status code should you return and why?

**5. Short answer:** What does "stateless" mean in HTTP? Why does it matter for scalability?

**6. Multiple choice:** What does HTTP/REST mean by "resource"?
- a) A server file on disk
- b) A database row
- c) Any named piece of data your API exposes ✓
- d) A JavaScript object

---

## 🔹 Architecture Homework (Brainstorm)

**Design a URL shortener API (no code needed yet).**

Think through:
- What resources does it have? (`/links`, `/links/{short_code}`)
- What HTTP methods map to what actions?
- What does a POST request body look like?
- What does a GET to `/r/{short_code}` return? (Hint: what status code signals a redirect?)
- What happens if the short code doesn't exist?
- What if someone tries to create a link with an invalid URL?

Write your design as a simple list of endpoints with methods, request/response shapes, and status codes. No code. This is how real API design starts.

---

## 🔹 Interview Questions

**Q1: "Explain the HTTP request/response cycle."**

Talking points: DNS resolution → TCP connection → client sends method/URL/headers/body → server parses, routes, processes → server returns status code/headers/body → connection closed or kept alive. Mention statelessness.

**Q2: "What's the difference between PUT and PATCH?"**

Talking points: PUT replaces the *entire* resource (idempotent — same result if called multiple times). PATCH applies a *partial update* (semantically idempotent but not required to be). In practice many teams just use PUT for simplicity; knowing the distinction signals REST literacy.

**Q3: "Why do we use 201 instead of 200 for resource creation?"**

Talking points: Status codes carry semantic meaning — 200 means "here's what you asked for," 201 means "a new resource was created and here it is." Clients and API gateways can behave differently based on codes (e.g., caching GET 200 responses). Following the spec makes your API predictable and professional.

---