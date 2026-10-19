# NC Plus One

A REST API for an events platform. It allows users to register, browse events, RSVP, and manage their attendance. Organisers will be able to create and manage events, and view statistics about their audience.

## Setup
1. Clone the repo
    ```shell
    git clone https://github.com/hytang04/py-nc-plus-one.git
    cd py-nc-plus-one
    ```

### Database Setup
1. Create a local PostgreSQL database
    ```shell
    createdb nc_plus_one
    ```

2. Setup the database
    ```
    psql -d nc_plus_one -f db/setup.sql
    ```
