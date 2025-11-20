-- 1. Clean setup (drop + create)
DROP TABLE IF EXISTS projects;

CREATE TABLE
    projects (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        budget REAL
    );

-- 2. Seed data (single INSERT per statement)
INSERT INTO
    projects (name, status, budget)
VALUES
    ('Alpha', 'active', 120000.50);

INSERT INTO
    projects (name, status, budget)
VALUES
    ('Beta', 'pending', NULL);

INSERT INTO
    projects (name, status, budget)
VALUES
    ('Gamma', 'cancelled', 50000);

-- 3. Multi-row insert script (tests multi-statement handling)
INSERT INTO
    projects (name, status, budget)
VALUES
    ('Delta', 'active', 75000);

;

-- intentional blank statement to ensure filter works
INSERT INTO
    projects (name, status, budget)
VALUES
    ('Epsilon', 'pending', 21000);

-- 4. Update statements
UPDATE projects
SET
    budget = budget * 1.1
WHERE
    status = 'active';

UPDATE projects
SET
    status = 'archived'
WHERE
    name = 'Gamma';

-- 5. Delete and truncate-style cleanup
DELETE FROM projects
WHERE
    budget IS NULL;

-- 6. Simple select (should return rows)
SELECT
    id,
    name,
    status,
    budget
FROM
    projects
ORDER BY
    id;

-- 7. Select with comment noise to test sanitizer
SELECT
    COUNT(*) AS total_active
FROM
    projects
WHERE
    status = 'active';

-- should ignore everything after this comment
-- 8. Intentional incomplete statement (should trigger warning)
SELECT
    *
FROM
    projects;

-- INDEX tests
-- create tables to target
DROP TABLE IF EXISTS customers;

CREATE TABLE
    IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        email TEXT,
        city TEXT,
        created_at TEXT
    );

DROP TABLE IF EXISTS orders;

CREATE TABLE
    IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        total REAL,
        created_at TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers (id)
    );

-- basic single-column index
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers (email);

-- unique index to test constraint handling
CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_city_email ON customers (city, email);

-- index on orders for foreign key lookups
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders (customer_id);

-- composite index with different order
CREATE INDEX IF NOT EXISTS idx_orders_created_total ON orders (created_at, total);

-- check that the indexes exist
PRAGMA index_list ('customers');

PRAGMA index_list ('orders');

-- snapshot schema info for verification
SELECT
    name,
    tbl_name,
    sql
FROM
    sqlite_master
WHERE
    type = 'index';

-- remove one to test DROP behavior
DROP INDEX IF EXISTS idx_orders_created_total;

-- final PRAGMA to confirm deletion
PRAGMA index_list ('orders');