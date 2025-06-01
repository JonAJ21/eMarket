import random
import uuid

from faker import Faker

from TestDataGeneration.utils.schemas import Cart, CartItem, CartItemKafka, PaymentOrderEvent, Product, Review, SocialProviderEnum, UserDeviceTypeEnum


class DataGenerator:
    def __init__(
        self, pg_cursor, pg_conn, mongo_client, mongo_db, kafka_producer
    ):
        self.pg_cursor = pg_cursor
        self.pg_conn = pg_conn
        self.mongo_client = mongo_client
        self.mongo_db = mongo_db
        self.kafka_producer = kafka_producer
        self.fake = Faker('ru_RU')
        self.unique_values = {
            'logins': set(),
            'emails': set(),
            'phones': set(),
            'inns': set(),
            'kpps': set(),
            'payment_accounts': set(),
            'correspondent_accounts': set(),
            'biks': set()
        }

    def get_unique_value(self, field, generator_func):
        """Generate unique value for specified field"""
        max_attempts = 100
        for _ in range(max_attempts):
            value = generator_func()
            if value not in self.unique_values[field]:
                self.unique_values[field].add(value)
                return value
        raise ValueError(f"Failed to generate unique {field} after {max_attempts} attempts")

    def generate_roles(self):
        roles = [
            ("admin", "Administrator with full access"),
            ("seller", "User who can sell products"),
            ("customer", "Regular customer"),
            ("moderator", "Content moderator")
        ]
        
        for name, description in roles:
            role_id = str(uuid.uuid4())
            self.pg_cursor.execute(
                "INSERT INTO roles (id, name, description) VALUES (%s, %s, %s)",
                (role_id, name, description)
            )
        self.pg_conn.commit()
        return self.pg_cursor.rowcount

    def generate_users(self, num_users=20):
        users = []
        
        for i in range(num_users):
            user_id = str(uuid.uuid4())
            login = self.get_unique_value('logins', lambda: f"{self.fake.user_name()}{i}")
            email = self.get_unique_value('emails', lambda: self.fake.unique.email())
            phone = self.get_unique_value('phones', lambda: self.fake.unique.msisdn()[3:])  # Russian numbers without +7
            
            self.pg_cursor.execute(
                """INSERT INTO users (id, login, password, first_name, last_name, 
                fathers_name, email, phone, is_active) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (user_id, login, self.fake.password(length=12), self.fake.first_name(), 
                self.fake.last_name(), self.fake.middle_name(), email, phone, self.fake.boolean(80)))
            
            # Assign roles (50% customers, 30% sellers, 20% admins/moderators)
            if i < num_users * 0.5:
                self.pg_cursor.execute("SELECT id FROM roles WHERE name = 'customer'")
                role_id = self.pg_cursor.fetchone()[0]
            elif i < num_users * 0.8:
                self.pg_cursor.execute("SELECT id FROM roles WHERE name = 'seller'")
                role_id = self.pg_cursor.fetchone()[0]
                self.generate_seller_info(user_id)
            else:
                self.pg_cursor.execute("SELECT id FROM roles WHERE name IN ('admin', 'moderator') ORDER BY random() LIMIT 1")
                role_id = self.pg_cursor.fetchone()[0]
            
            self.pg_cursor.execute(
                "INSERT INTO user_role (user_id, role_id) VALUES (%s, %s)",
                (user_id, role_id)
            )
            
            # Generate social accounts for some users
            if random.random() < 0.3:
                self.generate_social_account(user_id)
            
            # Generate user history
            self.generate_user_history(user_id)
            
            users.append(user_id)
        self.pg_conn.commit()
        return users

    def generate_seller_info(self, user_id):
        inn = self.get_unique_value('inns', lambda: str(self.fake.random_number(digits=12, fix_len=True)))
        kpp = self.get_unique_value('kpps', lambda: str(self.fake.random_number(digits=9, fix_len=True)))
        payment_account = self.get_unique_value('payment_accounts', lambda: str(self.fake.random_number(digits=20, fix_len=True)))
        correspondent_account = self.get_unique_value('correspondent_accounts', lambda: str(self.fake.random_number(digits=20, fix_len=True)))
        bik = self.get_unique_value('biks', lambda: str(self.fake.random_number(digits=9, fix_len=True)))
        
        self.pg_cursor.execute(
            """INSERT INTO sellers_info 
            (user_id, name, address, postal_code, inn, kpp, payment_account, 
            correspondent_account, bank, bik, is_verified, verificated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (user_id, self.fake.company(), self.fake.address().replace('\n', ', '),
            self.fake.postcode(), inn, kpp, payment_account, correspondent_account,
            self.fake.credit_institution(), bik, self.fake.boolean(70),
            self.fake.date_time_this_year() if random.random() > 0.3 else None)
        )
        
    def generate_social_account(self, user_id):
        social_id = str(self.fake.random_number(digits=16))
        social_name = random.choice(list(SocialProviderEnum)).value
        
        self.pg_cursor.execute(
            """INSERT INTO social_accounts 
            (id, user_id, social_id, social_name)
            VALUES (%s, %s, %s, %s)""",
            (str(uuid.uuid4()), user_id, social_id, social_name)
        )

    def generate_user_history(self, user_id, num_entries=5):
        devices = list(UserDeviceTypeEnum)
        
        for _ in range(num_entries):
            is_success = random.random() > 0.2
            attemted_at = self.fake.date_time_this_month()
            
            self.pg_cursor.execute(
                """INSERT INTO user_history 
                (id, user_id, user_agent, user_device_type, attemted_at, is_success)
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (str(uuid.uuid4()), user_id, self.fake.user_agent(), 
                random.choice(devices).value, attemted_at, is_success)
            )


    def generate_products(self, categories, seller_ids, num_products=50):
        product_names = [
            "Смартфон", "Ноутбук", "Планшет", "Наушники", "Телевизор",
            "Футболка", "Джинсы", "Платье", "Куртка", "Обувь",
            "Диван", "Стол", "Стул", "Шкаф", "Кровать",
            "Роман", "Детектив", "Фэнтези", "Наука", "Учебник",
            "Велосипед", "Мяч", "Гантели", "Лыжи", "Ракетка"
        ]
        
        products = []
        for _ in range(num_products):
            product_id = str(uuid.uuid4())
            seller_id = random.choice(seller_ids)
            category_id = random.choice(categories)
            name = f"{random.choice(['Премиум', 'Профессиональный', 'Ультра', 'Стандарт'])} {random.choice(product_names)}"
            
            product = Product(
                id=product_id,
                seller_id=seller_id,
                name=name,
                description=self.fake.paragraph(nb_sentences=3),
                price=round(random.uniform(100, 100000), 2),
                category_id=category_id,
                stock=random.randint(0, 1000),
                images=[f"https://example.com/images/{product_id}_{j}.jpg" for j in range(1, random.randint(1, 5))]
            )
            
            self.mongo_db.products.insert_one(product.model_dump())
            products.append(product_id)
        
        return products

    def generate_carts(self, user_ids, products):
        carts = []
        for user_id in user_ids:
            cart_id = str(uuid.uuid4())
            items = []
            
            # Add 1-5 random products to cart
            for _ in range(random.randint(1, 5)):
                product = self.mongo_db.products.aggregate([{ "$sample": { "size": 1 } }]).next()
                items.append(CartItem(
                    product_id=product["id"],
                    quantity=random.randint(1, 3),
                    price=product["price"]
                ))
            
            cart = Cart(
                id=cart_id,
                user_id=user_id,
                items=items
            )
            
            self.mongo_db.carts.insert_one(cart.model_dump())
            carts.append(cart_id)
        
        return carts

    def generate_reviews(self, user_ids, products, num_reviews=100):
        reviews = []
        comments = [
            "Отличный товар!", "Очень доволен", "Могло быть лучше",
            "Отличное качество", "Не то, что ожидал", "Быстрая доставка",
            "Хорошее соотношение цены и качества", "Куплю еще раз", "Плохая упаковка",
            "Идеально подходит для моих нужд"
        ]
        
        for _ in range(num_reviews):
            review_id = str(uuid.uuid4())
            product_id = random.choice(products)
            user_id = random.choice(user_ids)
            
            review = Review(
                id=review_id,
                product_id=product_id,
                user_id=user_id,
                rating=random.randint(1, 5),
                comment=random.choice(comments) + " " + self.fake.sentence()
            )
            
            self.mongo_db.reviews.insert_one(review.model_dump())
            reviews.append(review_id)
        
        return reviews

    def generate_kafka_events(self, user_ids, num_events=20):
        delivery_methods = ["courier", "pickup", "post"]
        
        for _ in range(num_events):
            event_id = str(uuid.uuid4())
            user_id = random.choice(user_ids)
            order_id = str(uuid.uuid4())
            order_status = random.choice(["created", "processing", "shipped", "delivered"])
            
            # Get user's cart
            cart = self.mongo_db.carts.find_one({"user_id": user_id})
            if not cart:
                continue
                
            # Convert cart items to Kafka format
            kafka_items = []
            for item in cart["items"]:
                product = self.mongo_db.products.find_one({"id": item["product_id"]})
                if product:
                    kafka_items.append(CartItemKafka(
                        product_id=item["product_id"],
                        seller_id=product["seller_id"],
                        amount=item["price"] * item["quantity"]
                    ).model_dump())
            
            if not kafka_items:
                continue
                
            event = PaymentOrderEvent(
                id=event_id,
                user_id=user_id,
                order_id=order_id,
                order_status=order_status,
                products=kafka_items,
                is_paid=random.random() > 0.3,
                delivery_address=self.fake.address(),
                delivery_method=random.choice(delivery_methods),
                created_at=self.fake.date_time_this_month()
            )
            
            # Send to Kafka
            self.kafka_producer.send("payment_orders", event.model_dump())