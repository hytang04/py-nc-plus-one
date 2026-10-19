# NC Plus One

A REST API for an events platform. It allows users to register, browse events, RSVP, and manage their attendance. Organisers will be able to create and manage events, and view statistics about their audience.

## Setup
1. Clone the repo
    ```shell
    git clone https://github.com/hytang04/py-nc-plus-one.git
    cd py-nc-plus-one
    ```

2. Create a virtual environment
    ```shell
    python -m venv .venv
    source .venv/bin/activate
    ```

3. Install the Python dependencies
    ```shell
    pip install -r requirements.txt
    ```

4. Create a `.env` file from the example and fill in your local PostgreSQL credentials
    ```shell
    cp .env.example .env
    ```

    Set `PGDATABASE` to `nc_plus_one`, and set `PGUSER`, `PGPASSWORD`, `PGHOST`, and `PGPORT` to the values for your local PostgreSQL instance.

5. Create a local PostgreSQL database
    ```shell
    createdb nc_plus_one
    ```

6. Setup the database
    ```
    psql -d nc_plus_one -f db/setup.sql
    ```

7. Run the seed function
    ```shell
    python db/seed.py
    ```
