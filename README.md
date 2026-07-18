# Quiz Backend Management API

A backend API for a Data Science quiz application built with **FastAPI**. It provides CRUD operations for quiz questions and answer choices, JWT-based admin authentication, and uses **SQLite** with **SQLAlchemy ORM** for data storage.

---

## Features

* RESTful API built with FastAPI
* CRUD operations for questions and choices
* JWT-based admin authentication for write operations
* One-to-many relationship between Questions and Choices
* SQLite database using SQLAlchemy ORM
* Request and response validation with Pydantic
* Interactive API documentation using Swagger UI
* Streamlit frontend for quiz-taking and admin management

---

## Tech Stack

| Technology | Purpose                         |
| ---------- | ------------------------------- |
| FastAPI    | REST API framework              |
| SQLAlchemy | ORM and database models         |
| Pydantic   | Request and response validation |
| SQLite     | Database                        |
| Uvicorn    | ASGI server                     |
| Streamlit  | Frontend UI                     |

---

## Project Structure

```text
quiz-backend-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   ├── auth.py              # JWT authentication utilities
│   ├── create_admin.py      # Create an admin account locally
│   ├── seed_data.py         # Seed the database from CSV
│   └── routers/
│       ├── auth.py
│       ├── questions.py
│       └── choices.py
├── data/
│   └── questions.csv
├── ui/
│   ├── streamlit_app.py
│   └── requirements.txt
├── requirements.txt
├── .env.example
├── quiz.db
└── README.md
```

---

## Setup & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Seed the database (Optional)

```bash
python -m app.seed_data
```

The script checks whether the database already contains questions before inserting data.

### 3. Start the API

```bash
uvicorn app.main:app --reload
```

If `uvicorn` is not recognized, run:

```bash
python -m uvicorn app.main:app --reload
```

### 4. Open the API documentation

```
http://127.0.0.1:8000/docs
```

Swagger UI allows you to explore and test every endpoint directly from the browser.

The SQLite database (`quiz.db`) is created automatically when the application starts.

---

## Database Design

### Question

| Field         | Type    | Description       |
| ------------- | ------- | ----------------- |
| id            | Integer | Primary Key       |
| question_text | String  | Question text     |
| category      | String  | Question category |

### Choice

| Field       | Type    | Description                  |
| ----------- | ------- | ---------------------------- |
| id          | Integer | Primary Key                  |
| choice_text | String  | Answer choice                |
| is_correct  | Boolean | Indicates the correct answer |
| question_id | Integer | Foreign Key → Question.id    |

### Relationship

One **Question** can have multiple **Choices**.

Deleting a question automatically removes its associated choices using cascade delete.

---

## API Endpoints

### Authentication

| Method | Endpoint      | Description |
| ------ | ------------- | ----------- |
| POST   | `/auth/login` | Admin login |

---

### Questions

| Method | Endpoint          | Auth Required | Description                          |
| ------ | ----------------- | ------------- | ------------------------------------ |
| GET    | `/questions/`     | No            | List questions                       |
| GET    | `/questions/{id}` | No            | Retrieve a question with its choices |
| POST   | `/questions/`     | Yes           | Create a question                    |
| PUT    | `/questions/{id}` | Yes           | Update a question                    |
| DELETE | `/questions/{id}` | Yes           | Delete a question                    |

Supports:

* `skip`
* `limit`
* `category`
* `random_order`

---

### Choices

| Method | Endpoint        | Auth Required | Description     |
| ------ | --------------- | ------------- | --------------- |
| GET    | `/choices/`     | No            | List choices    |
| POST   | `/choices/`     | Yes           | Create a choice |
| PUT    | `/choices/{id}` | Yes           | Update a choice |
| DELETE | `/choices/{id}` | Yes           | Delete a choice |

Supports:

* `skip`
* `limit`

---

## Authentication

All **GET** endpoints are public.

Creating, updating, and deleting questions or choices requires a valid **JWT access token**.

There is no public registration endpoint. Admin accounts can be created in one of two ways.

### Option 1 — Local

```bash
python -m app.create_admin
```

The script prompts for a username, email, and password before storing the account in the database.

### Option 2 — Deployment

Set the following environment variables:

```text
ADMIN_USERNAME=your_username
ADMIN_EMAIL=your_email@example.com
ADMIN_PASSWORD=your_password
SECRET_KEY=your_secret_key
```

If no admin account exists when the application starts, one is created automatically using these values.

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}'
```

The API returns a JWT access token.

Include it in authenticated requests:

```
Authorization: Bearer <access_token>
```

---

## Streamlit UI

A Streamlit frontend is included in the `ui/` directory.

### Quiz Mode

* Choose a category or Mixed mode
* Select the number of questions
* Answer questions and submit
* View your score and correct answers

Questions are returned in random order to provide a different quiz experience each time.

### Admin Mode

* Secure login using JWT authentication
* Create, edit, and delete questions
* Manage answer choices

### Run the UI

```bash
pip install -r ui/requirements.txt
streamlit run ui/streamlit_app.py
```

By default, the UI connects to:

```
http://localhost:8000
```

To use a deployed backend, create:

```text
ui/.streamlit/secrets.toml
```

```toml
API_BASE_URL = "https://your-backend.onrender.com"
```

If not provided, the application uses the local backend.

The frontend and backend are independent applications and can be deployed separately.

---

## Dataset

The project includes a dataset of **62 Data Science quiz questions** covering:

* Python
* SQL
* Statistics
* Pandas & NumPy
* Machine Learning

The dataset is stored in:

```
data/questions.csv
```

and can be loaded into the database using the provided seed script.

---

## Future Improvements

* Add quiz score history
* Role-based access control
* PostgreSQL support
* Docker deployment
* Unit and integration tests
* API rate limiting
* Question import/export functionality

---

## License

This project is intended for learning and educational purposes.
