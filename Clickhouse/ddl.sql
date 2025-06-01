CREATE TABLE orders (
    id UUID,
    user_id UUID,
    order_id UUID,
    payment_id String,
    is_paid Bool,
    order_status String,
    created_at DateTime,
    payment_status String,
    delivery_address String,
    delivery_method String,
    total_amount Decimal(18, 2),
    currency String DEFAULT 'RUB',
    user_login String,
    user_email String,
    user_phone String
) ENGINE = MergeTree()
ORDER BY (created_at, user_id, id);