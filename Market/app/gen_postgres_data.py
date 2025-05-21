import csv
import uuid
import random
import os
from datetime import datetime, timedelta
from bcrypt import gensalt, hashpw
from faker import Faker

# Инициализация Faker для генерации реалистичных данных
fake = Faker('ru_RU')

# Конфигурац
NUM_USERS = 300_000
CHUNK_SIZE = 100_000  # Размер чанка для обработки
ROLES = ['admin', 'user', 'seller', 'moderator', 'support']
SOCIAL_PROVIDERS = ['google', 'facebook', 'twitter', 'vk', 'yandex', 'github']
DEVICE_TYPES = ['desktop', 'mobile', 'tablet', 'smart_tv', 'other']
BASE_DATA_DIR = 'data'

def setup_data_directory():
    """Создает директорию для новой генерации данных"""
    if not os.path.exists(BASE_DATA_DIR):
        os.makedirs(BASE_DATA_DIR)
    
    # Находим последнюю существующую генерацию
    existing_gens = [d for d in os.listdir(BASE_DATA_DIR) if d.startswith('gen')]
    if existing_gens:
        last_gen_num = max(int(gen[3:]) for gen in existing_gens)
        new_gen_num = last_gen_num + 1
    else:
        new_gen_num = 1
    
    gen_dir = os.path.join(BASE_DATA_DIR, f'gen{new_gen_num}')
    os.makedirs(gen_dir)
    return gen_dir

# Генерация ролей
def generate_roles(gen_dir):
    roles = []
    for i, name in enumerate(ROLES):
        roles.append({
            'id': str(uuid.uuid4()),
            'name': name,
            'description': f"Роль {name}",
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        })
    
    with open(os.path.join(gen_dir, 'roles.csv'), 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'description', 'created_at', 'updated_at'])
        writer.writeheader()
        writer.writerows(roles)
    
    return [role['id'] for role in roles]

# Генерация пользователей
def generate_users(gen_dir, role_ids):
    # Создаем все CSV файлы с заголовками
    users_file = open(os.path.join(gen_dir, 'users.csv'), 'w', newline='')
    users_writer = csv.DictWriter(users_file, fieldnames=[
        'id', 'login', 'password', 'first_name', 'last_name', 'fathers_name',
        'phone', 'email', 'is_active', 'created_at', 'updated_at'
    ])
    users_writer.writeheader()
    
    # sellers_file = open(os.path.join(gen_dir, 'sellers_info.csv'), 'w', newline='')
    # sellers_writer = csv.DictWriter(sellers_file, fieldnames=[
    #     'user_id', 'name', 'address', 'postal_code', 'inn', 'kpp',
    #     'payment_account', 'correspondent_account', 'bank', 'bik',
    #     'is_verified', 'verificated_at', 'created_at', 'updated_at'
    # ])
    # sellers_writer.writeheader()
    
    # social_file = open(os.path.join(gen_dir, 'social_accounts.csv'), 'w', newline='')
    # social_writer = csv.DictWriter(social_file, fieldnames=[
    #     'id', 'user_id', 'social_id', 'social_name', 'created_at'
    # ])
    # social_writer.writeheader()
    
    # history_file = open(os.path.join(gen_dir, 'user_history.csv'), 'w', newline='')
    # history_writer = csv.DictWriter(history_file, fieldnames=[
    #     'id', 'user_id', 'user_agent', 'user_device_type', 'attemted_at', 'is_success'
    # ])
    # history_writer.writeheader()
    
    # roles_file = open(os.path.join(gen_dir, 'user_role.csv'), 'w', newline='')
    # roles_writer = csv.DictWriter(roles_file, fieldnames=['user_id', 'role_id'])
    # roles_writer.writeheader()
    password = hashpw(fake.password().encode(), gensalt()).decode()
    # Генерация данных
    for i in range(0, NUM_USERS):
        if i % CHUNK_SIZE == 0 and i > 0:
            print(f"Обработано {i} пользователей...")
        
        user_id = uuid.uuid4()
        first_name = fake.first_name() if random.random() > 0.1 else None
        last_name = fake.last_name() if random.random() > 0.1 else None
        fathers_name = fake.middle_name() if random.random() > 0.7 else None
        phone = fake.phone_number() if random.random() > 0.2 else None
        email = fake.email() if random.random() > 0.2 else None
        # Записываем пользователя
        users_writer.writerow({
            'id': str(user_id),
            'login': f"user_{gen_dir}{i}",
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'fathers_name': fathers_name,
            'phone': phone,
            'email': f"{gen_dir}{email}",
            'is_active': random.choice([True, False]),
            'created_at': fake.date_time_between(start_date='-5y', end_date='now'),
            'updated_at': datetime.now()
        })
        
        # # Каждый 10-й пользователь - продавец
        # if i % 10 == 0:
        #     sellers_writer.writerow({
        #         'user_id': str(user_id),
        #         'name': fake.company(),
        #         'address': fake.address(),
        #         'postal_code': fake.postcode(),
        #         'inn': ''.join([str(random.randint(0, 9)) for _ in range(12)]),
        #         'kpp': ''.join([str(random.randint(0, 9)) for _ in range(9)]),
        #         'payment_account': ''.join([str(random.randint(0, 9)) for _ in range(20)]),
        #         'correspondent_account': ''.join([str(random.randint(0, 9)) for _ in range(20)]),
        #         'bank': fake.company() + ' банк',
        #         'bik': ''.join([str(random.randint(0, 9)) for _ in range(9)]),
        #         'is_verified': random.choice([True, False]),
        #         'verificated_at': fake.date_time_between(start_date='-2y', end_date='now') if random.random() > 0.5 else None,
        #         'created_at': datetime.now(),
        #         'updated_at': datetime.now()
        #     })
        
        # # Социальные аккаунты (1-3 на пользователя)
        # for _ in range(random.randint(1, 3)):
        #     social_writer.writerow({
        #         'id': str(uuid.uuid4()),
        #         'user_id': str(user_id),
        #         'social_id': str(uuid.uuid4()),
        #         'social_name': random.choice(SOCIAL_PROVIDERS),
        #         'created_at': datetime.now()
        #     })
        
        # # История входа (3-500 записей на пользователя)
        # for _ in range(random.randint(3, 500)):
        #     history_writer.writerow({
        #         'id': str(uuid.uuid4()),
        #         'user_id': str(user_id),
        #         'user_agent': fake.user_agent(),
        #         'user_device_type': random.choice(DEVICE_TYPES),
        #         'attemted_at': fake.date_time_between(start_date='-1y', end_date='now'),
        #         'is_success': random.choice([True, False])
        #     })
        
        # # Роли пользователя (1-3 роли)
        # for role_id in random.sample(role_ids, min(random.randint(1, 3), len(role_ids))):
        #     roles_writer.writerow({
        #         'user_id': str(user_id),
        #         'role_id': str(role_id)
        #     })
    
    # Закрываем все файлы
    users_file.close()
    # sellers_file.close()
    # social_file.close()
    # history_file.close()
    # roles_file.close()

def main():
    # Настраиваем директорию для данных
    gen_dir = setup_data_directory()
    print(f"Генерация данных в директории: {gen_dir}")
    
    # Генерируем роли и получаем их ID
    role_ids = generate_roles(gen_dir)
    
    # Генерируем пользователей и связанные данные
    generate_users(gen_dir, role_ids)
    
    print("Генерация данных завершена!")

if __name__ == "__main__":
    main()