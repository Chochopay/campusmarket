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

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)