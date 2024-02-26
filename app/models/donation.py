from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import AbstractDonation


class Donation(AbstractDonation):
    user_id = Column(
        Integer,
        ForeignKey('user.id', name='fk_donation_user_id_user'),
    )
    comment = Column(Text)

    def __repr__(self):
        return '{}, user_id = {}'.format(
            super().__repr__(),
            self.user_id,
        )
