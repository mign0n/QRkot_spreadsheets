from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Integer

from app.core.db import Base


class AbstractDonation(Base):
    __abstract__ = True
    __table_args__ = (
        CheckConstraint('full_amount > 0'),
        CheckConstraint('full_amount >= invested_amount'),
        CheckConstraint('invested_amount >= 0'),
    )

    full_amount = Column(Integer)
    invested_amount = Column(Integer, default=0)
    fully_invested = Column(Boolean, default=False)
    create_date = Column(DateTime)
    close_date = Column(DateTime)

    def __repr__(self):
        return (
            '{}: id = {}, full_amount = {}, invested_amount = {},'
            ' create_date = {}, close_date = {}'
        ).format(
            type(self).__name__,
            self.id,
            self.full_amount,
            self.invested_amount,
            self.create_date,
            self.close_date,
        )
