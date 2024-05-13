import dataclasses

@dataclasses.dataclass
class Index_config:
    name:str
    multiplier:int
    lotsize:int
    exchange_segment:str
    current_price:str
