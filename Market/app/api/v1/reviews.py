from typing import List
from fastapi import APIRouter, HTTPException, Query
from schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse, ProductRating
from services.review_service import ReviewService

router = APIRouter()
review_service = ReviewService()

@router.post("/", response_model=ReviewResponse)
async def create_review(review: ReviewCreate):
    try:
        return await review_service.create_review(review)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str):
    review = await review_service.get_review(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: str, review: ReviewUpdate):
    updated_review = await review_service.update_review(review_id, review)
    if not updated_review:
        raise HTTPException(status_code=404, detail="Review not found")
    return updated_review

@router.delete("/{review_id}")
async def delete_review(review_id: str):
    if not await review_service.delete_review(review_id):
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted successfully"}

@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def get_product_reviews(product_id: str):
    return await review_service.get_product_reviews(product_id)

@router.get("/user/{user_id}", response_model=List[ReviewResponse])
async def get_user_reviews(user_id: str):
    return await review_service.get_user_reviews(user_id)

@router.get("/product/{product_id}/rating", response_model=ProductRating)
async def get_product_rating(product_id: str):
    rating = await review_service.get_product_rating(product_id)
    reviews = await review_service.get_product_reviews(product_id)
    return ProductRating(rating=rating, total_reviews=len(reviews)) 