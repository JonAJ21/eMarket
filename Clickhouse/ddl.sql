CREATE DATABASE IF NOT EXISTS data_warehouse;

-- fact sales
CREATE TABLE IF NOT EXISTS data_warehouse.fact_sales (
    id UUID,
    order_id UUID,
    user_id UUID,
    seller_id UUID,
    product_id UUID,
    is_paid UInt8,
    amount Float64,
    currency String,
    created_at Datetime
) ENGINE = MergeTree()
ORDER BY (created_at, user_id);

-- dim orders
CREATE TABLE IF NOT EXISTS data_warehouse.dim_orders (
    id UUID,
    order_status String,
    delivery_address String,
    delivery_method String,
    created_at DateTime
) ENGINE = MergeTree()
ORDER BY id;

-- dim users
CREATE TABLE IF NOT EXISTS data_warehouse.dim_users (
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
) ENGINE = MergeTree()
ORDER BY id;

-- dim roles
CREATE TABLE IF NOT EXISTS data_warehouse.dim_roles (
    id UUID,
    user_id UUID,
    name String,
    description String,
    created_at DateTime,
    updated_at DateTime
) ENGINE = MergeTree()
ORDER BY id;

-- dim sellers
CREATE TABLE IF NOT EXISTS data_warehouse.dim_sellers (
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
) ENGINE = MergeTree()
ORDER BY id;

-- dim social_accounts
CREATE TABLE IF NOT EXISTS data_warehouse.dim_social_accounts (
    id UUID,
    user_id UUID,
    social_id String,
    social_name String,
    created_at DateTime
) ENGINE = MergeTree()
ORDER BY (user_id, social_name);

-- dim products
CREATE TABLE IF NOT EXISTS data_warehouse.dim_products (
    id UUID,
    name String,
    description String,
    price Float64,
    category_id String,
    stock Int32,
    images Array(String),
    created_at DateTime,
    updated_at DateTime
) ENGINE = MergeTree()
ORDER BY id;

-- dim categories
CREATE TABLE IF NOT EXISTS data_warehouse.dim_categories (
    id UUID,
    name String,
    description String,
    parent_id Nullable(UUID),
    created_at DateTime,
    updated_at DateTime
) ENGINE = MergeTree()
ORDER BY id;

-- dim reviews
CREATE TABLE IF NOT EXISTS data_warehouse.dim_reviews (
    id UUID,
    product_id String,
    user_id UUID,
    rating UInt8,
    comment String,
    created_at DateTime,
    updated_at DateTime
) ENGINE = MergeTree()
ORDER BY id;