from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel


ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

@dataclass
class Error:
    message: str
    code: str
    
@dataclass
class Result:
    is_success: bool
    error: Error | None
    
    @staticmethod
    def success() -> "Result":
        return Result(is_success=True, error=None)
    
    @staticmethod
    def failure(error: Error) -> "Result":
        return Result(is_success=False, error=error)
    
@dataclass
class GenericResult(Result, Generic[ModelType]):
    response: ModelType
    is_success: bool
    error: Error | None
    
    @staticmethod
    def success(value: ModelType) -> "GenericResult":
        return GenericResult(is_success=True, error=None, response=value)
    
    @staticmethod
    def failure(err: Error) -> "GenericResult":
        return GenericResult(is_success=False, error=err, response=None)