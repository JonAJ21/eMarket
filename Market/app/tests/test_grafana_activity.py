import requests
import time
import random
import threading
from typing import Dict, List, Tuple
from faker import Faker
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8000/api/v1"
fake = Faker()

def print_response(response):
    print(f"Status Code: {response.status_code}")
    try:
        print("Response:", response.json())
    except:
        print("Response:", response.text)
    print("-" * 50)

class ActivityGenerator:
    def __init__(self):
        self.category_ids: List[str] = []
        self.product_ids: List[str] = []
        self.user_ids: List[str] = [f"test_user_{i}" for i in range(1, 21)]  # 20 тестовых пользователей
        self.lock = threading.Lock()
        
    def generate_categories(self) -> List[str]:
        """Генерация категорий"""
        print("\nGenerating categories...")
        
        categories = [
            {"name": "Electronics", "description": "Electronic devices and gadgets"},
            {"name": "Books", "description": "Books and literature"},
            {"name": "Clothing", "description": "Fashion and apparel"},
            {"name": "Home & Garden", "description": "Home improvement and garden supplies"},
            {"name": "Sports", "description": "Sports equipment and accessories"},
            {"name": "Beauty", "description": "Beauty and personal care products"},
            {"name": "Toys", "description": "Toys and games"},
            {"name": "Food", "description": "Food and beverages"},
            {"name": "Health", "description": "Health and wellness products"},
            {"name": "Automotive", "description": "Automotive parts and accessories"}
        ]
        
        for category in categories:
            response = requests.post(f"{BASE_URL}/categories/", json=category)
            if response.status_code == 200:
                with self.lock:
                    self.category_ids.append(response.json()["_id"])
                print(f"Created category: {category['name']}")
            time.sleep(0.1)
            
        return self.category_ids

    def generate_product(self, category_id: str) -> str:
        """Генерация одного продукта"""
        product = {
            "name": fake.catch_phrase(),
            "description": fake.text(max_nb_chars=200),
            "price": round(random.uniform(10.0, 2000.0), 2),
            "stock": random.randint(1, 100),
            "category_id": category_id,
            "images": [fake.image_url() for _ in range(random.randint(1, 3))]
        }
        
        response = requests.post(f"{BASE_URL}/products/", json=product)
        if response.status_code == 200:
            product_id = response.json()["_id"]
            with self.lock:
                self.product_ids.append(product_id)
            print(f"Created product: {product['name']}")
            return product_id
        return None

    def generate_products(self) -> List[str]:
        """Генерация продуктов в многопоточном режиме"""
        print("\nGenerating products...")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for _ in range(50):  # Генерируем 50 продуктов
                category_id = random.choice(self.category_ids)
                futures.append(executor.submit(self.generate_product, category_id))
            
            for future in as_completed(futures):
                future.result()
                
        return self.product_ids

    def generate_cart_activity_for_user(self, user_id: str):
        """Генерация активности корзины для одного пользователя"""
        for _ in range(10):  # 10 операций с корзиной для каждого пользователя
            product_id = random.choice(self.product_ids)
            
            # Добавление в корзину
            add_data = {
                "user_id": user_id,
                "product_id": product_id,
                "quantity": random.randint(1, 5)
            }
            requests.post(f"{BASE_URL}/cart/add", json=add_data)
            print(f"Added product {product_id} to cart for user {user_id}")
            time.sleep(0.1)
            
            # Обновление количества
            update_data = {
                "user_id": user_id,
                "product_id": product_id,
                "quantity": random.randint(1, 3)
            }
            requests.put(f"{BASE_URL}/cart/update", json=update_data)
            print(f"Updated cart for user {user_id}")
            time.sleep(0.1)
            
            # Удаление продукта
            remove_data = {
                "user_id": user_id,
                "product_id": product_id
            }
            requests.delete(f"{BASE_URL}/cart/remove", json=remove_data)
            print(f"Removed product from cart for user {user_id}")
            time.sleep(0.1)

    def generate_cart_activity(self):
        """Генерация активности корзины в многопоточном режиме"""
        print("\nGenerating cart activity...")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.generate_cart_activity_for_user, user_id) 
                      for user_id in self.user_ids]
            
            for future in as_completed(futures):
                future.result()

    def generate_review(self, product_id: str):
        """Генерация одного отзыва"""
        review_data = {
            "product_id": product_id,
            "user_id": random.choice(self.user_ids),
            "rating": random.randint(1, 5),
            "text": fake.text(max_nb_chars=200)
        }
        
        response = requests.post(f"{BASE_URL}/reviews/", json=review_data)
        if response.status_code == 200:
            print(f"Created review for product {product_id}")

    def generate_reviews(self):
        """Генерация отзывов в многопоточном режиме"""
        print("\nGenerating reviews...")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for product_id in self.product_ids:
                for _ in range(5):  # 5 отзывов на каждый продукт
                    futures.append(executor.submit(self.generate_review, product_id))
            
            for future in as_completed(futures):
                future.result()

    def generate_invalid_requests(self):
        """Генерация некорректных запросов"""
        print("\nGenerating invalid requests...")
        
        invalid_requests = [
            # Некорректные продукты
            {
                "name": fake.word(),
                "description": fake.text(),
                "price": -100.00,
                "category_id": "invalid_category_id",
                "stock": -1
            },
            {
                "name": "",
                "description": fake.text(),
                "price": 0,
                "category_id": "invalid_category_id",
                "stock": 0
            },
            # Некорректные категории
            {
                "name": "",
                "description": fake.text()
            },
            {
                "name": "a" * 101,  # Слишком длинное имя
                "description": fake.text()
            },
            # Некорректные отзывы
            {
                "product_id": "invalid_product_id",
                "user_id": "invalid_user_id",
                "rating": 6,
                "text": ""
            },
            {
                "product_id": "invalid_product_id",
                "user_id": "invalid_user_id",
                "rating": 0,
                "text": "a" * 1001  # Слишком длинный текст
            }
        ]
        
        for request in invalid_requests:
            if "rating" in request:  # Это отзыв
                response = requests.post(f"{BASE_URL}/reviews/", json=request)
            elif "price" in request:  # Это продукт
                response = requests.post(f"{BASE_URL}/products/", json=request)
            else:  # Это категория
                response = requests.post(f"{BASE_URL}/categories/", json=request)
            print(f"Tried to create invalid {request.get('name', 'review')}")
            time.sleep(0.1)

def main():
    generator = ActivityGenerator()
    
    # Генерируем категории
    generator.generate_categories()
    time.sleep(1)
    
    # Генерируем продукты
    generator.generate_products()
    time.sleep(1)
    
    # Генерируем активность корзины
    generator.generate_cart_activity()
    time.sleep(1)
    
    # Генерируем отзывы
    generator.generate_reviews()
    time.sleep(1)
    
    # Генерируем некорректные запросы
    generator.generate_invalid_requests()
    
    print("\nActivity generation completed!")

if __name__ == "__main__":
    main() 