from peewee import *

from models.BaseModel import BaseModel

class IndexedCoinModel(BaseModel):
    Ticker = CharField(unique=True, max_length=64)
    DesiredPercentage = DoubleField()
    DistanceFromTarget = DoubleField()
    Locked = BooleanField()

    def get_distance_from_target(self, coinBalanceModel, totalBtcValue):
        """Get the percent this coin is off relative to the index."""
        return (coinBalanceModel.get_current_percentage(totalBtcValue) - self.DesiredPercentage)

    def get_percent_from_coin_target(self, coinBalanceModel, totalBtcValue):
        """Get the percent this coin is off relative to its own balance."""
        # desired percentage is in whole numbers, need to divide by 100 to get the decimal equivalent
        desired_pct = self.DesiredPercentage / 100
        distance = self.get_distance_from_target(coinBalanceModel, totalBtcValue)
        return round(distance / desired_pct, 2)