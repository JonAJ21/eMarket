import functools
import time
from typing import Callable, Any
from prometheus_client import Counter, Histogram, Gauge

# Метрики для товаров
product_operations_counter = Counter(
    'product_operations_total',
    'Total number of product operations',
    ['operation_type', 'status']
)

product_operation_duration = Histogram(
    'product_operation_duration_seconds',
    'Duration of product operations',
    ['operation_type']
)

products_in_stock = Gauge(
    'products_in_stock',
    'Number of products in stock',
    ['product_id']
)

# Метрики для категорий
category_operations_counter = Counter(
    'category_operations_total',
    'Total number of category operations',
    ['operation_type', 'status']
)

category_operation_duration = Histogram(
    'category_operation_duration_seconds',
    'Duration of category operations',
    ['operation_type']
)

products_in_category = Gauge(
    'products_in_category',
    'Number of products in category',
    ['category_id']
)

# Метрики для отзывов
review_operations_counter = Counter(
    'review_operations_total',
    'Total number of review operations',
    ['operation_type', 'status']
)

review_operation_duration = Histogram(
    'review_operation_duration_seconds',
    'Duration of review operations',
    ['operation_type']
)

product_rating = Gauge(
    'product_rating',
    'Average product rating',
    ['product_id']
)

# Метрики для корзины
cart_operations_counter = Counter(
    'cart_operations_total',
    'Total number of cart operations',
    ['operation_type', 'status']
)

cart_operation_duration = Histogram(
    'cart_operation_duration_seconds',
    'Duration of cart operations',
    ['operation_type']
)

cart_items_count = Gauge(
    'cart_items_count',
    'Number of items in cart',
    ['user_id']
)

def track_product_metrics(operation_type: str):
    """
    Декоратор для отслеживания метрик операций с товарами
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                product_operations_counter.labels(
                    operation_type=operation_type,
                    status='success'
                ).inc()
                return result
            except Exception as e:
                product_operations_counter.labels(
                    operation_type=operation_type,
                    status='error'
                ).inc()
                raise e
            finally:
                duration = time.time() - start_time
                product_operation_duration.labels(
                    operation_type=operation_type
                ).observe(duration)
        return wrapper
    return decorator

def track_category_metrics(operation_type: str):
    """
    Декоратор для отслеживания метрик операций с категориями
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                category_operations_counter.labels(
                    operation_type=operation_type,
                    status='success'
                ).inc()
                return result
            except Exception as e:
                category_operations_counter.labels(
                    operation_type=operation_type,
                    status='error'
                ).inc()
                raise e
            finally:
                duration = time.time() - start_time
                category_operation_duration.labels(
                    operation_type=operation_type
                ).observe(duration)
        return wrapper
    return decorator

def track_review_metrics(operation_type: str):
    """
    Декоратор для отслеживания метрик операций с отзывами
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                review_operations_counter.labels(
                    operation_type=operation_type,
                    status='success'
                ).inc()
                return result
            except Exception as e:
                review_operations_counter.labels(
                    operation_type=operation_type,
                    status='error'
                ).inc()
                raise e
            finally:
                duration = time.time() - start_time
                review_operation_duration.labels(
                    operation_type=operation_type
                ).observe(duration)
        return wrapper
    return decorator

def track_cart_metrics(operation_type: str):
    """
    Декоратор для отслеживания метрик операций с корзиной
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                cart_operations_counter.labels(
                    operation_type=operation_type,
                    status='success'
                ).inc()
                return result
            except Exception as e:
                cart_operations_counter.labels(
                    operation_type=operation_type,
                    status='error'
                ).inc()
                raise e
            finally:
                duration = time.time() - start_time
                cart_operation_duration.labels(
                    operation_type=operation_type
                ).observe(duration)
        return wrapper
    return decorator 