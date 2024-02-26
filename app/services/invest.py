from datetime import datetime

from app.models.base import AbstractDonation


def make_investments(
    target: AbstractDonation,
    sources: list[AbstractDonation],
) -> list[AbstractDonation]:
    invested_sources = []
    for source in sources:
        amount = min(
            target.full_amount - target.invested_amount,
            source.full_amount - source.invested_amount,
        )
        for obj in source, target:
            obj.invested_amount += amount
            if obj.full_amount - obj.invested_amount == 0:
                obj.fully_invested = True
                obj.close_date = datetime.now()
        invested_sources.append(source)
        if target.fully_invested:
            break
    return invested_sources
