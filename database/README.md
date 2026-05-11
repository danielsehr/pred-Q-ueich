## SQL Alchemy -> ORM = Object Relational Mapper

Instead of 

````SQL
INSERT INTO forecast VALUES (...)
SELECT * FROM forecast
````

we can write now:

````cpp
Forecast()
session.query(Forecast)
````

much cleaner.

## Mental concept:

Python World | Database World   |
-------------|------------------|
classes      |      tables      |
objects	     |      rows        |
attributes   |  	columns     |

SQLAlchemy connects them.

## Complete flow

````

db.py
    ↓
Create database engine & session
    ↓
models.py
    ↓
defines table blueprint
    ↓
init_db.py
    ↓
creates real SQL tables from both
    ↓
jobs/api
    ↓
use sessions to read/write rows
````