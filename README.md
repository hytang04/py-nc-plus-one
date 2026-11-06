# NC Plus One

A REST API for an events platform. It allows users to register, browse events,
RSVP, and manage their attendance. Organisers will be able to create and manage
events, and view statistics about their audience.

## Requirements

- Python 3.11+
- PostgreSQL (make sure it is running)
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

   Provide the username, password, host, port (default 5432) and database name
   for the PostgresQL connection, for example:

   ```shell
   PGUSER=postgres
   PGPASSWORD=password
   PGHOST=localhost
   PGPORT=5432
   PGDATABASE=nc_plus_one
   ```

   `JWT_SECRET` should be generated randomly:

   ```shell
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

6. Setup the database:

   ```shell
   psql -d postgres -f db/setup.sql
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

To test, create a separate test database `nc_plus_one_test` and point the new
`PGDATABASE` at it when seeding the database and running `pytest`.

```shell
createdb nc_plus_one_test
PGDATABASE='nc_plus_one_test' python -m db.seed
PGDATABASE='nc_plus_one_test' pytest
```

## Terraform setup

### Prerequisites
- [AWS CLI](https://aws.amazon.com/cli/) installed and configured with valid credentials (`aws configure`).
- [Terraform](https://developer.hashicorp.com/terraform/install) (version `>= 1.5.0`) installed.

1. Export AWS credentials:
   ```shell
   export AWS_ACCESS_KEY_ID="example-id"
   export AWS_SECRET_ACCESS_KEY="example-key"
   export AWS_SESSION_TOKEN="example-token"
   ```

2. Make a copy of `terraform-setup.sh.example` and enter your unique suffix for the S3 bucket name:
   ```shell
   cp terraform-setup.sh.example terraform-setup.sh
   ```

3. Run `terraform-setup.sh`:
   ```shell
   ./terraform-setup.sh
   ```