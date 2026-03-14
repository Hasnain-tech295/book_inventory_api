## ⚠️ Common Pitfalls

**Forgetting `exclude_unset=True` on PATCH** — if you call `model_dump()` without it, every Optional field defaults to `None`, silently wiping data the client didn't intend to change. This is one of the most common PATCH bugs.

**Putting filters in path params instead of query params** — `/books/tolkien` to filter by author is wrong. Path params identify a *specific resource*. Filters, sorting, and pagination always go in query params.

**No pagination** — returning every row in a table with no `limit` is a production disaster waiting to happen. A table with 10M rows will crash your API and your database. Always paginate collection endpoints.

**Trusting client-supplied IDs on creation** — the server assigns IDs, not the client. Never accept an `id` field in a POST request body.

**Sharing one model for input and output** — your `BookCreate` (what comes in) and `BookResponse` (what goes out) should be separate models. They have different fields. Conflating them causes either security leaks or validation errors.

**Loose string fields with no length limits** — `title: str` with no `max_length` means a client can send a 50MB string and your API will happily process it. Always set `max_length` on user-supplied strings.

---