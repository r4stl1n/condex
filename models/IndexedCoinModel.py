from peewee import *

from models.BaseModel import BaseModel

class IndexedCoinModel(BaseModel):
    Ticker = CharField(unique=True, max_length=64)
    DesiredPercentage = DoubleField()
    DistanceFromTarget = DoubleField()
    Locked = BooleanField()

    def get_distance_from_target(self, coinBalanceModel, totalBtcValue):
        return (coinBalanceModel.get_current_percentage(totalBtcValue) - self.DesiredPercentage)