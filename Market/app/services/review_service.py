from typing import List, Optional
from bson import ObjectId
from models.review import Review
from schemas.review import ReviewCreate
from repositories.review_repository import ReviewRepository
from repositories.product_repository import ProductRepository

class ReviewService:
    def __init__(self):
        self.review_repo = ReviewRepository()
        self.product_repo = ProductRepository()

    async def create_review(self, review: ReviewCreate) -> Review:
        # Проверяем существование товара
        product = await self.product_repo.get_by_id(str(review.product_id))
        if not product:
            raise ValueError("Product not found")
        
        # Создаем модель Review из схемы ReviewCreate
        review_model = Review(
            product_id=review.product_id,
            user_id=review.user_id,
            rating=review.rating,
            comment=review.comment
        )
        return await self.review_repo.create(review_model)

    async def get_review(self, review_id: str) -> Optional[Review]:
        return await self.review_repo.get_by_id(review_id)

    async def update_review(self, review_id: str, review: Review) -> Optional[Review]:
        return await self.review_repo.update(review_id, review)

    async def delete_review(self, review_id: str) -> bool:
        return await self.review_repo.delete(review_id)

    async def get_product_reviews(self, product_id: str) -> List[Review]:
        return await self.review_repo.get_by_product(product_id)

    async def get_user_reviews(self, user_id: str) -> List[Review]:
        return await self.review_repo.get_by_user(user_id)

    async def get_product_rating(self, product_id: str) -> float:
        return await self.review_repo.get_average_rating(product_id) 