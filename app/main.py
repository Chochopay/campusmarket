from fastapi import FastAPI
from app.database import Base, engine
from contextlib import asynccontextmanager

from app.users.models import User
from app.categories.models import Category

from app.listings.models import Listing, ListingImage
from app.deal_requests.models import DealRequest
from app.messages.models import Message

from app.favorites.models import Favorite
from app.reports.models import Report

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.categories.router import router as categories_router
from app.listings.router import router as listings_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(listings_router)