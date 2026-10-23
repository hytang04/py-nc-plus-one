# NC Plus One

A REST API for an events platform. It allows users to register, browse events, RSVP, and manage their attendance. Organisers will be able to create and manage events, and view statistics about their audience.

## Requirements
- Python
- PostgreSQL
- Git

## Setup
1. Clone the repository:
    ```shell
    git clone https://github.com/hytang04/py-nc-plus-one.git
    cd py-nc-plus-one
    ```

2. Create and activate a virtual environment:
    ```shell
    python -m venv .venv
    source .venv/bin/activate
    ```

3. Install the Python dependencies:
    ```shell
    pip install -r requirements.txt
    ```

4. Create the PostgreSQL database:
    ```shell
    createdb nc_plus_one
    ```

5. Create a `.env` file from the example in the project root:
    ```shell
    cp .env.example .env
    ```
    Set `DATABASE_URL` to your local PostgreSQL connection string, for example:
    ```text
    DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/nc_plus_one
    ```

6. Setup the database:
    ```
    psql -d nc_plus_one -f db/setup.sql
    ```

7. Connect to and seed the database:
    ```shell
    python -m db.connection
    python -m db.seed
    ```

8. Run the server:
    ```shell
    uvicorn main:app --reload
    ```

### Testing
To test, create a separate test database `nc_plus_one_test` and point the new `DATABASE_URL` at it when seeding the database and running `pytest`.
```shell
createdb nc_plus_one_test
DATABASE_URL='postgresql://USERNAME:PASSWORD@localhost:5432/nc_plus_one_test' python -m db.seed
DATABASE_URL='postgresql://USERNAME:PASSWORD@localhost:5432/nc_plus_one_test' pytest
```