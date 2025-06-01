import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_response(response):
    print(f"Status Code: {response.status_code}")
    try:
        print("Response:", response.json())
    except json.JSONDecodeError:
        print("Response:", response.text)
    print("-" * 50)

def test_categories():
    print("\nTesting Categories API...")
    
    # Создаем корневую категорию
    root_category_data = {
        "name": "Electronics",
        "description": "Electronic devices and gadgets"
    }
    response = requests.post(f"{BASE_URL}/categories/", json=root_category_data)
    print("\nCreate root category:")
    print_response(response)
    
    if response.status_code != 200:
        raise Exception(f"Failed to create root category: {response.text}")
    
    root_category_id = response.json()["_id"]

    # Создаем подкатегорию
    subcategory_data = {
        "name": "Smartphones",
        "description": "Mobile phones and accessories",
        "parent_id": root_category_id
    }
    response = requests.post(f"{BASE_URL}/categories/", json=subcategory_data)
    print("\nCreate subcategory:")
    print_response(response)
    
    if response.status_code != 200:
        raise Exception(f"Failed to create subcategory: {response.text}")
    
    subcategory_id = response.json()["_id"]

    # Получаем список категорий
    response = requests.get(f"{BASE_URL}/categories/")
    print("\nList all categories:")
    print_response(response)

    # Получаем подкатегории для корневой категории
    response = requests.get(f"{BASE_URL}/categories/{root_category_id}/subcategories")
    print("\nGet subcategories:")
    print_response(response)

    # Обновляем подкатегорию
    update_data = {
        "name": "Smartphones & Accessories",
        "description": "Mobile phones, cases, chargers and other accessories"
    }
    response = requests.put(f"{BASE_URL}/categories/{subcategory_id}", json=update_data)
    print("\nUpdate subcategory:")
    print_response(response)

    # Получаем обновленную подкатегорию
    response = requests.get(f"{BASE_URL}/categories/{subcategory_id}")
    print("\nGet updated subcategory:")
    print_response(response)

    return root_category_id, subcategory_id

def test_products(category_id):
    print("\nTesting Products API...")
    
    # Создаем первый продукт
    product1_data = {
        "name": "iPhone 15 Pro",
        "description": "Latest Apple smartphone with A17 Pro chip",
        "price": 999.99,
        "category_id": category_id,
        "stock": 10,
        "images": ["https://example.com/iphone15pro.jpg"]
    }
    response = requests.post(f"{BASE_URL}/products/", json=product1_data)
    print("\nCreate first product:")
    print_response(response)
    
    if response.status_code != 200:
        raise Exception(f"Failed to create first product: {response.text}")
    
    product1_id = response.json()["_id"]

    # Создаем второй продукт
    product2_data = {
        "name": "Samsung Galaxy S24",
        "description": "Latest Samsung smartphone with Snapdragon 8 Gen 3",
        "price": 899.99,
        "category_id": category_id,
        "stock": 15,
        "images": ["https://example.com/galaxys24.jpg"]
    }
    response = requests.post(f"{BASE_URL}/products/", json=product2_data)
    print("\nCreate second product:")
    print_response(response)
    
    if response.status_code != 200:
        raise Exception(f"Failed to create second product: {response.text}")
    
    product2_id = response.json()["_id"]

    # Получаем список всех продуктов
    response = requests.get(f"{BASE_URL}/products/")
    print("\nList all products:")
    print_response(response)

    # Получаем продукты по категории
    response = requests.get(f"{BASE_URL}/products/category/{category_id}")
    print("\nGet products by category:")
    print_response(response)

    # Поиск продуктов по названию
    response = requests.get(f"{BASE_URL}/products/search?query=iPhone")
    print("\nSearch products by name:")
    print_response(response)

    # Обновляем первый продукт
    update_data = {
        "price": 899.99,
        "stock": 5
    }
    response = requests.put(f"{BASE_URL}/products/{product1_id}", json=update_data)
    print("\nUpdate first product:")
    print_response(response)

    # Получаем обновленный продукт
    response = requests.get(f"{BASE_URL}/products/{product1_id}")
    print("\nGet updated product:")
    print_response(response)

    # Пытаемся создать продукт с несуществующей категорией
    invalid_product_data = {
        "name": "Invalid Product",
        "description": "This should fail",
        "price": 100.00,
        "category_id": "invalid_category_id",
        "stock": 1
    }
    response = requests.post(f"{BASE_URL}/products/", json=invalid_product_data)
    print("\nTry to create product with invalid category (should fail):")
    print_response(response)

    # Удаляем второй продукт
    response = requests.delete(f"{BASE_URL}/products/{product2_id}")
    print("\nDelete second product:")
    print_response(response)

    # Проверяем, что второй продукт удален
    response = requests.get(f"{BASE_URL}/products/{product2_id}")
    print("\nTry to get deleted product (should fail):")
    print_response(response)

    return product1_id

def test_cart(product_id):
    print("\nTesting Cart API...")
    user_id = "test_user_1"

    # Добавляем товар в корзину
    add_data = {
        "product_id": product_id,
        "quantity": 2
    }
    response = requests.post(f"{BASE_URL}/cart/{user_id}/items", json=add_data)
    print("\nAdd product to cart:")
    print_response(response)

    # Получаем содержимое корзины
    response = requests.get(f"{BASE_URL}/cart/{user_id}")
    print("\nGet cart:")
    print_response(response)

    # Изменяем количество товара в корзине
    update_data = {
        "quantity": 5
    }
    response = requests.put(f"{BASE_URL}/cart/{user_id}/items/{product_id}", json=update_data)
    print("\nUpdate product quantity in cart:")
    print_response(response)

    # Получаем содержимое корзины после изменения количества
    response = requests.get(f"{BASE_URL}/cart/{user_id}")
    print("\nGet cart after quantity update:")
    print_response(response)

    # Удаляем товар из корзины
    response = requests.delete(f"{BASE_URL}/cart/{user_id}/items/{product_id}")
    print("\nRemove product from cart:")
    print_response(response)

    # Проверяем, что корзина пуста
    response = requests.get(f"{BASE_URL}/cart/{user_id}")
    print("\nGet cart after removal:")
    print_response(response)

    # Добавляем товар снова и очищаем корзину
    response = requests.post(f"{BASE_URL}/cart/{user_id}/items", json=add_data)
    response = requests.delete(f"{BASE_URL}/cart/{user_id}")
    print("\nClear cart:")
    print_response(response)

    # Проверяем, что корзина пуста после очистки
    response = requests.get(f"{BASE_URL}/cart/{user_id}")
    print("\nGet cart after clear:")
    print_response(response)

def test_category_deletion(root_category_id, subcategory_id):
    print("\nTesting Category Deletion...")
    
    # Пытаемся удалить корневую категорию (должно быть ошибкой, так как есть подкатегории)
    response = requests.delete(f"{BASE_URL}/categories/{root_category_id}")
    print("\nTry to delete root category (should fail):")
    print_response(response)

    # Удаляем подкатегорию
    response = requests.delete(f"{BASE_URL}/categories/{subcategory_id}")
    print("\nDelete subcategory:")
    print_response(response)

    # Теперь удаляем корневую категорию (должно успешно)
    response = requests.delete(f"{BASE_URL}/categories/{root_category_id}")
    print("\nDelete root category:")
    print_response(response)

def main():
    try:
        # Тестируем категории
        root_category_id, subcategory_id = test_categories()
        
        # Тестируем продукты
        product_id = test_products(root_category_id)
        
        # Тестируем корзину
        test_cart(product_id)
        
        # Тестируем удаление категорий
        test_category_deletion(root_category_id, subcategory_id)
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the server is running.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main() 