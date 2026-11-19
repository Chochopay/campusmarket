from pydantic import BaseModel

# Если у вас Python ниже версии 3.12 используйте схему ниже

# from typing import Generic, TypeVar
# T = TypeVar["T"]
# class Pagination(BaseModel, GenericType[T]):
#     items: list[T]
#     total: int
#     limit: int
#     offset: int

class Pagination[T](BaseModel):
    items: list[T]
    total: int
    limit: int
    offset: int