
# Basics
Using PostgreSQL for a Python app, especially one deployed on Heroku, is a common choice due to PostgreSQL's reliability and robust features. For Python applications, `psycopg2` is a popular PostgreSQL database adapter, enabling you to interact with PostgreSQL databases in an efficient and Pythonic way. Let's go through the basics of setting up and using `psycopg2` in the context of storing configurations for different chats for a Telegram bot written with the Telebot library.

### Prerequisites

Before diving into code examples, ensure you have:

- A PostgreSQL database set up. On Heroku, you can add a Postgres addon to your application from the Heroku dashboard.
- The `psycopg2` package installed in your Python environment. If you're deploying on Heroku, also add it to your `requirements.txt` file.
- Basic knowledge of SQL for creating tables and performing CRUD operations.

### Setting Up `psycopg2`

1. **Install psycopg2**: Install the package using pip. If you're working in a local development environment, run:

   ```sh
   pip install psycopg2-binary
   ```

   For Heroku deployment, add `psycopg2-binary` to your `requirements.txt` file.

2. **Database Connection**: Use the DATABASE_URL from your Heroku Postgres addon to connect to your database. Heroku automatically adds this environment variable when you add a Postgres database.

   ```python
   import psycopg2
   import os

   DATABASE_URL = os.environ['DATABASE_URL']

   conn = psycopg2.connect(DATABASE_URL, sslmode='require')
   ```

### Basic Operations with `psycopg2`

#### Creating a Table

To store configurations for different chats, you'll need a table. Here's an example SQL statement to create a table:

```sql
CREATE TABLE chat_configs (
    chat_id BIGINT PRIMARY KEY,
    config JSONB
);
```

And here's how you can execute it with `psycopg2`:

```python
def create_table():
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_configs (
                chat_id BIGINT PRIMARY KEY,
                config JSONB
            );
        """)
        conn.commit()
```

#### Inserting Data

To insert or update a chat's configuration:

```python
def upsert_chat_config(chat_id, config):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO chat_configs (chat_id, config)
            VALUES (%s, %s)
            ON CONFLICT (chat_id) DO UPDATE
            SET config = EXCLUDED.config;
        """, (chat_id, config))
        conn.commit()
```

#### Retrieving Data

To retrieve a chat's configuration:

```python
def get_chat_config(chat_id):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT config FROM chat_configs WHERE chat_id = %s;
        """, (chat_id,))
        config = cursor.fetchone()
        return config[0] if config else None
```

#### Closing the Connection

It's important to close the connection when your application stops:

```python
conn.close()
```

### Notes

- When deploying on Heroku, manage database connections carefully. Heroku limits the number of connections based on your database plan.
- Always use environment variables (like `DATABASE_URL`) for sensitive information and avoid hard-coding credentials in your source code.
- Consider using connection pooling (e.g., with `psycopg2.pool.SimpleConnectionPool`) for more efficient use of database connections, especially important for web applications or bots serving multiple users.

This introduction covers the basics of using `psycopg2` to manage chat configurations for a Telegram bot. Adjust the SQL and Python code as necessary to fit your application's specific needs.