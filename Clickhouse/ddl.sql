CREATE DATABASE IF NOT EXISTS data_warehouse ON CLUSTER default;

-- fact sales

CREATE TABLE IF NOT EXISTS data_warehouse.fact_sales_local ON CLUSTER default (
    id UUID,
    order_id UUID,
    user_id UUID,
    seller_id UUID,
    product_id UUID,
    is_paid UInt8,
    amount Float64,
    currency String,
    created_at Datetime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/fact_sales_local', '{replica}')
ORDER BY (created_at, user_id);

CREATE TABLE IF NOT EXISTS data_warehouse.fact_sales ON CLUSTER default AS data_warehouse.fact_sales_local
ENGINE = Distributed(default, data_warehouse, fact_sales_local, rand());

-- dim orders

CREATE TABLE IF NOT EXISTS data_warehouse.dim_orders_local ON CLUSTER default (
    id UUID,
    order_status String,
    delivery_address String,
    delivery_method String,
    created_at DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/dim_orders_local', '{replica}')
ORDER BY id;

CREATE TABLE IF NOT EXISTS data_warehouse.dim_orders ON CLUSTER default AS data_warehouse.dim_orders_local
ENGINE = Distributed(default, data_warehouse, dim_orders_local, rand());

-- dim users

CREATE TABLE IF NOT EXISTS data_warehouse.dim_users_local ON CLUSTER default (
    id UUID,
    login String,
    first_name String,
    last_name String,
    fathers_name String,
    phone String,
    email String,
    is_active UInt8,
    created_at DateTime,
    updated_at DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/dim_users_local', '{replica}')
ORDER BY id;

CREATE TABLE IF NOT EXISTS data_warehouse.dim_users ON CLUSTER default AS data_warehouse.dim_users_local
ENGINE = Distributed(default, data_warehouse, dim_users_local, rand());

-- dim roles

CREATE TABLE IF NOT EXISTS data_warehouse.dim_roles_local ON CLUSTER default (
    id UUID,
    user_id UUID,
    name String,
    description String,
    created_at DateTime,
    updated_at DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/dim_roles_local', '{replica}')
ORDER BY id;

CREATE TABLE IF NOT EXISTS data_warehouse.dim_roles ON CLUSTER default AS data_warehouse.dim_roles_local
ENGINE = Distributed(default, data_warehouse, dim_roles_local, rand());

-- dim sellers

CREATE TABLE IF NOT EXISTS data_warehouse.dim_sellers_local ON CLUSTER default (
    id UUID,
    name String,
    address String,
    postal_code String,
    inn String,
    kpp String,
    payment_account String,
    correspondent_account String,
    bank String,
    bik String,
    is_verified UInt8,
    verificated_at Nullable(DateTime),
    created_at DateTime,
    updated_at DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/dim_sellers_local', '{replica}')
ORDER BY id;

CREATE TABLE IF NOT EXISTS data_warehouse.dim_sellers ON CLUSTER default AS data_warehouse.dim_sellers_local
ENGINE = Distributed(default, data_warehouse, dim_sellers_local, rand());

-- dim social_accounts

CREATE TABLE IF NOT EXISTS data_warehouse.dim_social_accounts_local ON CLUSTER default (
    id UUID,
    user_id UUID,
    social_id String,
    social_name String,
    created_at DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/dim_social_accounts_local', '{replica}')
ORDER BY (user_id, social_name);

CREATE TABLE IF NOT EXISTS data_warehouse.dim_social_accounts ON CLUSTER default AS data_warehouse.dim_social_accounts_local
ENGINE = Distributed(default, data_warehouse, dim_social_accounts_local, rand());

-- dim products

CREATE TABLE IF NOT EXISTS data_warehouse.dim_products_local ON CLUSTER default (
    id UUID,
    name String,
    description String,
    price Float64,
    category_id String,
    stock Int32,
    images Array(String),
    created_at DateTime,
    updated_at DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/dim_products_local', '{replica}')
ORDER BY id;

CREATE TABLE IF NOT EXISTS data_warehouse.dim_products ON CLUSTER default AS data_warehouse.dim_products_local
ENGINE = Distributed(default, data_warehouse, dim_products_local, rand());

-- dim categories

CREATE TABLE IF NOT EXISTS data_warehouse.dim_categories_local ON CLUSTER default (
    id UUID,
    name String,
    description String,
    parent_id Nullable(UUID),
    created_at DateTime,
    updated_at DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/dim_categories_local', '{replica}')
ORDER BY id;

CREATE TABLE IF NOT EXISTS data_warehouse.dim_categories ON CLUSTER default AS data_warehouse.dim_categories_local
ENGINE = Distributed(default, data_warehouse, dim_categories_local, rand());

-- dim reviews

CREATE TABLE IF NOT EXISTS data_warehouse.dim_reviews_local ON CLUSTER default (
    id UUID,
    product_id String,
    user_id UUID,
    rating UInt8,
    comment String,
    created_at DateTime,
    updated_at DateTime
) ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/dim_reviews_local', '{replica}')
ORDER BY id;

CREATE TABLE IF NOT EXISTS data_warehouse.dim_reviews ON CLUSTER default AS data_warehouse.dim_reviews_local
ENGINE = Distributed(default, data_warehouse, dim_reviews_local, rand());