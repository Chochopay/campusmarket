from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from typing import List, Literal, Optional

from app.users.models import User
from app.listings.models import Listing
from app.reports.models import Report
from app.deal_requests.models import DealRequest

from app.reports.schemas import ReportResponse, ReportCreate, ReportAccess

from app.auth.dependencies import require_moderator_or_admin, get_current_user

from app.database import get_db



router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/", response_model=ReportResponse)
def create_report(data: ReportCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):

    listing = db.execute(select(Listing).where(Listing.id == data.listing_id)).scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Такого объявления не существует"
        )
    if listing.user_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Вы не можете пожаловаться на свое объявление"
        )
    if listing.status not in ("published", "reserved", "completed"):
        raise HTTPException(
            status_code=409,
            detail="Вы не можете пожаловаться на объявление пока оно в текущем состоянии"
        )
    report = db.execute(select(Report).where(Report.user_id == current_user.id,
                                             Report.listing_id == listing.id)).scalar_one_or_none()
    if report:
        raise HTTPException(
            status_code=409,
            detail="Вы уже подавали жалобу на это объявление"
        )
    new_report = Report(
        user_id=current_user.id,
        listing_id=data.listing_id,
        reason=data.reason
    )
    try:
        db.add(new_report)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Вы уже подавали жалобу на это объявление"
        )

    db.refresh(new_report)
    return new_report


@router.get("/", response_model=List[ReportResponse])
def get_reports(status: Optional[Literal["pending", "resolved"]] = None, current_user: User = Depends(require_moderator_or_admin), db: Session = Depends(get_db)):
    query = select(Report)
    if status:
        query = query.where(Report.status == status)
    reports = db.execute(query).scalars().all()
    return reports


@router.patch("/{report_id}", response_model=ReportResponse)
def process_report(report_id: int,
                   data: ReportAccess,
                   current_user: User = Depends(require_moderator_or_admin),
                   db: Session = Depends(get_db)):
    report = db.execute(select(Report).where(Report.id == report_id)).scalar_one_or_none()
    if not report:
        raise HTTPException(
            status_code=404,
            detail="Такой Жалобы нет"
        )
    if report.status != "pending":
        raise HTTPException(
            status_code=409,
            detail="Жалоба уже неактуальна"
        )
    listing = db.execute(select(Listing).where(Listing.id == report.listing_id)).scalar_one_or_none()
    if not listing:
        raise HTTPException(
            status_code=404,
            detail="Такого объявления не существует"
        )

    if data.action == "hide":
        if listing.status not in ("published", "reserved", "completed"):
            raise HTTPException(
                status_code=409,
                detail="Вы не можете изменить статус объявление пока оно в текущем состоянии"
            )
        reports = db.execute(select(Report).where(Report.listing_id == listing.id,
                                                  Report.id != report.id,
                                                  Report.status == "pending")).scalars().all()
        report.status = "resolved"
        for other_report in reports:
            other_report.status = "resolved"
        report.resolution = data.resolution
        listing.status = "hidden"
        request = db.execute(select(DealRequest).where(DealRequest.listing_id == listing.id,
                                                        DealRequest.status == "accepted")).scalar_one_or_none()
        if request:
            request.status = "pending"
    elif data.action == "dismiss":
        report.status = "resolved"
        report.resolution = "Жалоба закрыта по причине скрытия объявления по жалобе другого пользователя"
    db.commit()
    db.refresh(report)
    return report
