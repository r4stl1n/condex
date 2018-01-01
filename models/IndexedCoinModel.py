from peewee import BooleanField
from peewee import CharField
from peewee import DoubleField

from models.BaseModel import BaseModel

class IndexedCoinModel(BaseModel):
    """Representation of a single coin within the index."""

    Ticker = CharField(unique=True, max_length=64)
    DesiredPercentage = DoubleField()
    DistanceFromTarget = DoubleField()
    Locked = BooleanField()

    def get_distance_from_target(self, coin_balance_model, total_btc_value):
        """Get the percent this coin is off relative to the index."""
        return coin_balance_model.get_current_percentage(total_btc_value) - self.DesiredPercentage

    def get_percent_from_coin_target(self, coin_balance_model, total_btc_value):
        """Get the percent this coin is off relative to its own balance."""
        # desired percentage is in whole numbers, need to divide by 100 to get the decimal
        desired_pct = self.DesiredPercentage / 100
        distance = self.get_distance_from_target(coin_balance_model, total_btc_value)
        return round(distance / desired_pct, 2)
