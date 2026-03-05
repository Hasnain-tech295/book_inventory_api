## 🔹 Coding Assignment

**Extend your Book Inventory API with the following:**

**Acceptance criteria:**

1. Add a `genre` field to the Book model (string, optional, max 50 chars)
2. Add `GET /books?genre=fiction` filtering support
3. Add `GET /books?sort_by=year&order=asc` sorting support (`sort_by` accepts `year` or `title`, `order` accepts `asc` or `desc`)
4. Add a `GET /books/search?q=hobbit` endpoint that searches across `title` and `author` fields (case-insensitive substring match)
5. The search endpoint must also support `limit` and `offset`

**Constraints:**
- Validate that `sort_by` only accepts `"year"` or `"title"` — return 422 for anything else (hint: use Python `Literal` type or a validator)
- Validate that `order` only accepts `"asc"` or `"desc"`
- Search with an empty `q` string should return a 400 with a meaningful message

**Test requirements:**
- Test search finds results across both title and author
- Test search with empty `q` returns 400
- Test sorting by year ascending and descending
- Test invalid `sort_by` value returns 422

---

## 🔹 Reading

- Pydantic Field types and validators: https://docs.pydantic.dev/latest/concepts/fields/
- FastAPI Query parameters: https://fastapi.tiangolo.com/tutorial/query-params/
- FastAPI Response Model: https://fastapi.tiangolo.com/tutorial/response-model/

---

## 🔹 Quick Quiz

**1. Short answer:** What does `exclude_unset=True` do in `model_dump()` and why is it critical for PATCH endpoints?

**2. Multiple choice:** A client requests `GET /books?author=tolkien`. In FastAPI, `author` is a:
- a) Path parameter
- b) Request body field
- c) Query parameter ✓
- d) Header

**3. Scenario:** You have a `User` model with a `password_hash` field stored in your DB. A client calls `GET /users/1`. What is the correct way to ensure `password_hash` is never returned in the response?

**4. Multiple choice:** Which `Field()` constraint ensures a value is greater than 0 but also accepts 0?
- a) `gt=0`
- b) `ge=0` ✓
- c) `lt=0`
- d) `min=0`

**5. Short answer:** What HTTP status code does FastAPI return automatically when Pydantic validation fails, and what does the response body contain?

**6. Scenario:** Your `GET /products` endpoint returns all 2 million products in the database. What two things must you add to fix this?

---

## 🔹 Architecture Homework

**Design the API for a movie review platform.**

Think through:

- What are the resources? (`/movies`, `/reviews`, `/users`?)
- How do you get all reviews for a specific movie? Is it `/reviews?movie_id=5` or `/movies/5/reviews`? What are the tradeoffs of each?
- What query params does `GET /movies` need? (genre, release year, rating, pagination)
- What fields should be in the request body vs. the response model for a Review? (think: should the client send `user_id`? Or should the server derive it from the auth token?)
- What should the response model for a Movie include vs. exclude?

Write this as a table of endpoints: Method | Path | Query Params | Request Body | Response Shape | Status Codes.

---

## 🔹 Interview Questions

**Q1: "What is Pydantic and how does FastAPI use it?"**

Talking points: Runtime data validation via type annotations. FastAPI uses it for request bodies, query params, path params, and response serialization. Raises `ValidationError` with structured detail on failure. Mention `Field()` for constraints. Mention `response_model` strips fields not in the model — security implication.

**Q2: "What's the difference between a path parameter and a query parameter? When do you use each?"**

Talking points: Path params identify *which* resource (`/users/42`). Query params modify *how* you retrieve a collection — filtering, sorting, pagination (`/users?role=admin&limit=20`). Never put filters in the path. Never put resource identifiers in query params for REST.

**Q3: "How would you implement pagination on a collection endpoint?"**

Talking points: Two common patterns — offset/limit (`?limit=20&offset=40`) and cursor-based (`?after=<cursor_id>`). Offset pagination is simple but degrades at scale (DB must scan `offset` rows). Cursor-based is more performant for large datasets and is what Twitter, Facebook, and Stripe use. Always enforce a max `limit`. Apply pagination *after* filtering.

---

