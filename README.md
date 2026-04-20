# 📚 Book Inventory API

A RESTful API for managing a book inventory, built with **FastAPI** and **Pydantic**. Supports full CRUD operations, filtering, sorting, pagination, and full-text search.

---

## ✨ Features

- **List books** with filtering by genre, sorting by title or year, and pagination
- **Search books** by title or author with a single query parameter
- **Get a single book** by ID
- **Create, update, and delete** books with full input validation
- **ISBN-13 validation** via a custom Pydantic field validator
- **Auto-generated interactive docs** at `/docs` (Swagger UI) and `/redoc`

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) 0.136.0 |
| Validation | [Pydantic](https://docs.pydantic.dev/) v2 |
| Server | [Uvicorn](https://www.uvicorn.org/) |
| Python | 3.10+ |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- `pip`

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/book_inventory_api.git
   cd book_inventory_api
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

```bash
fastapi dev main.py
```

The API will be available at **http://127.0.0.1:8000**.

| URL | Description |
|---|---|
| `http://127.0.0.1:8000/docs` | Swagger UI (interactive docs) |
| `http://127.0.0.1:8000/redoc` | ReDoc documentation |

---

## 📖 API Reference

### Data Model

| Field | Type | Required | Constraints |
|---|---|---|---|
| `id` | `int` | Auto-generated | — |
| `title` | `str` | ✅ | 1–200 characters |
| `author` | `str` | ✅ | 1–200 characters |
| `year` | `int` | ✅ | > 0, ≤ current year |
| `price` | `float` | ✅ | > 0 |
| `genre` | `str` | ❌ | Max 50 characters |
| `isbn` | `str` | ❌ | 13 digits (ISBN-13) |

---

### Endpoints

#### `GET /books` — List Books

Returns a paginated, sorted list of books with optional genre filtering.

**Query Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `genre` | `string` | `null` | Filter by genre (case-insensitive) |
| `sort_by` | `"year"` \| `"title"` | `"year"` | Field to sort by |
| `order` | `"asc"` \| `"desc"` | `"asc"` | Sort direction |
| `limit` | `int` | `10` | Results per page (1–100) |
| `offset` | `int` | `0` | Number of results to skip |

**Example**
```
GET /books?genre=Novel&sort_by=title&order=asc&limit=5
```

---

#### `GET /books/search` — Search Books

Searches across both `title` and `author` fields using a single query string.

**Query Parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `q` | `string` | — | Search term (required, min length 1) |
| `limit` | `int` | `10` | Results per page (1–100) |
| `offset` | `int` | `0` | Number of results to skip |

**Example**
```
GET /books/search?q=orwell
```

---

#### `GET /books/{book_id}` — Get a Book

Returns a single book by its ID.

**Example**
```
GET /books/1
```

**Response: `200 OK`**
```json
{
  "id": 1,
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "year": 1925,
  "price": 10.99,
  "genre": "Novel",
  "isbn": "9780743273565"
}
```

**Response: `404 Not Found`**
```json
{
  "detail": "Book with id=99 not found"
}
```

---

#### `POST /books` — Create a Book

Adds a new book to the inventory.

**Request Body**
```json
{
  "title": "Brave New World",
  "author": "Aldous Huxley",
  "year": 1932,
  "price": 11.49,
  "genre": "Fiction",
  "isbn": "9780060850524"
}
```

**Response: `201 Created`**
```json
{
  "id": 4,
  "title": "Brave New World",
  "author": "Aldous Huxley",
  "year": 1932,
  "price": 11.49,
  "genre": "Fiction",
  "isbn": "9780060850524"
}
```

---

#### `PATCH /books/{book_id}` — Update a Book

Partially updates an existing book. Only include the fields you want to change.

**Request Body**
```json
{
  "price": 13.99
}
```

**Response: `200 OK`** — Returns the full updated book object.

---

#### `DELETE /books/{book_id}` — Delete a Book

Removes a book from the inventory.

**Response: `204 No Content`**

---

## 📁 Project Structure

```
book_inventory_api/
├── main.py           # FastAPI app, route definitions, in-memory database
├── schemas.py        # Pydantic models (BookCreate, BookResponse, BookUpdate)
├── requirements.txt  # Python dependencies
└── README.md
```

---

## 📝 Notes

- **In-memory storage**: All data is stored in a Python dictionary and will reset on every server restart. There is no persistent database.
- **ISBN validation**: Hyphens are stripped automatically before validation; the stored value is the raw 13-digit string.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
