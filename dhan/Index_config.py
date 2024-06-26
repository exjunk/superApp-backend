import dataclasses

@dataclasses.dataclass
class Index_config:
    name:str
    multiplier:int
    lotsize:int
    index_risk:float
    profit:float
    exchange_segment:str
    current_price:str
