


# Basics;
PostgreSQL, often simply Postgres, is an advanced, open-source object-relational database system known for its reliability, robustness, and performance. It supports both SQL (relational) and JSON (non-relational) querying. PostgreSQL is highly extensible with features such as custom functions and data types, and it supports a wide variety of programming languages and frameworks. Here are some of the basics to get you started with PostgreSQL:

### Key Features

1. **ACID Compliance**: PostgreSQL guarantees atomicity, consistency, isolation, and durability (ACID), ensuring reliable transactions and data integrity.
2. **Rich Data Types**: Supports a wide range of data types including primitive types (integer, numeric, string), structured (date/time, array, range), document (JSON/JSONB, XML, key-value), geometric, and custom types.
3. **Extensibility**: Users can define their own data types, custom functions, and more. It also supports the creation of extensions to add new functionalities.
4. **Concurrency**: Uses Multi-Version Concurrency Control (MVCC) to handle concurrent data access, providing high levels of performance and scalability.
5. **Full-Text Search**: Offers powerful full-text search capabilities that are easy to use.
6. **Security**: Provides strong security features, including robust access control system, column and row-level security, SSL support, and more.

### Basic Operations

#### Installation

PostgreSQL can be installed on various operating systems. On Ubuntu, you can install it using:

```sh
sudo apt update
sudo apt install postgresql postgresql-contrib
```

On macOS, using Homebrew:

```sh
brew install postgresql
```

#### Starting and Stopping the Server

On Ubuntu:

```sh
sudo service postgresql start
sudo service postgresql stop
```

On macOS (using Homebrew):

```sh
brew services start postgresql
brew services stop postgresql
```

#### Using the PostgreSQL Command Line Interface

After installation, you can interact with PostgreSQL using the `psql` command-line interface. To start `psql` under the default PostgreSQL user:

```sh
sudo -u postgres psql
```

#### Basic SQL Operations

- **Create a Database**:

```sql
CREATE DATABASE mydatabase;
```

- **Switch Connection to a Database**:

```sql
\c mydatabase
```

- **Create a Table**:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

- **Insert Data**:

```sql
INSERT INTO users (username) VALUES ('john_doe');
```

- **Query Data**:

```sql
SELECT * FROM users;
```

- **Update Data**:

```sql
UPDATE users SET username = 'jane_doe' WHERE id = 1;
```

- **Delete Data**:

```sql
DELETE FROM users WHERE id = 1;
```

#### Connecting to PostgreSQL from an Application

Connecting to PostgreSQL from a programming language or framework typically involves using a database driver or an ORM (Object-Relational Mapping) tool specific to your language or framework of choice, such as psycopg2 for Python, pg for Node.js, or ActiveRecord for Ruby on Rails.

### Documentation and Learning

PostgreSQL has comprehensive documentation that covers all aspects of the database, from basic usage to advanced features. The official PostgreSQL documentation is a great place to start learning in depth: [PostgreSQL Documentation](https://www.postgresql.org/docs/).

As you grow more comfortable with PostgreSQL, you'll discover its powerful features that make it suitable for a wide range of applications, from small projects to large-scale enterprise systems.




















# CRUD basics:
SQL (Structured Query Language) is the standard language for managing and manipulating databases. Below, you'll find an overview of the basics of SQL, focusing on creating tables and performing CRUD (Create, Read, Update, Delete) operations. These operations are fundamental for managing data in any relational database management system (RDBMS) like PostgreSQL, MySQL, SQL Server, etc.

### Creating Tables

To store data in a database, you first need to create a table. A table is defined with a specific set of columns, each with its own data type and possibly constraints (e.g., primary key, unique, not null).

#### Example

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

In this example, `SERIAL` is a PostgreSQL data type that automatically increments. `VARCHAR(n)` is a variable-length character string with a maximum length of `n`. `TIMESTAMP` stores date and time.

### Inserting Data (Create)

To add a new row to a table, use the `INSERT` statement.

#### Example

```sql
INSERT INTO users (username, email, password) VALUES ('john_doe', 'john@example.com', 'secret');
```

### Reading Data (Read)

To retrieve data from a table, use the `SELECT` statement. You can specify conditions with the `WHERE` clause and sort the result set with the `ORDER BY` clause.

#### Example

```sql
SELECT * FROM users; -- Retrieves all columns for all rows
SELECT username, email FROM users WHERE id = 1; -- Retrieves specific columns for rows matching the condition
SELECT * FROM users ORDER BY created_at DESC; -- Retrieves all columns for all rows, sorted by the created_at column
```

### Updating Data (Update)

To modify existing rows in a table, use the `UPDATE` statement with a `WHERE` clause to specify which rows should be updated.

#### Example

```sql
UPDATE users SET password = 'new_secret' WHERE id = 1;
```

### Deleting Data (Delete)

To remove rows from a table, use the `DELETE` statement, typically with a `WHERE` clause to avoid deleting all rows.

#### Example

```sql
DELETE FROM users WHERE id = 1;
```

### Additional Concepts

- **Primary Key**: A column or a set of columns used to uniquely identify each row in a table.
- **Foreign Key**: A field (or collection of fields) in one table that uniquely identifies a row of another table. It's used to establish a link between the data in two tables.
- **Indexes**: Used to speed up the search queries by essentially allowing the database to skip scanning every row in a table.
- **Transactions**: Allow multiple SQL statements to be executed as a single atomic operation, ensuring data integrity.
- **Joins**: Used to combine rows from two or more tables, based on a related column between them.

Remember, SQL syntax can vary slightly between different RDBMS, so always check the documentation for the specific database you're working with.




















# Using Postgres with a python app;
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








