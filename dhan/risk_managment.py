
import db_management as db_management
from Enums import Index



def config():
    result = db_management.get_config_details(client_id=1000002314)
    



class Client_configuration:
    def __init__(self,dhanClientId,bnf_max_quantity,nifty_max_quantity,finnifty_max_quantity,midcap_max_quantity,bankex_max_quantity,sensex_max_quantity,hard_sl,soft_sl,max_risk_of_day,risk_per_trade,kill_switch_risk):
        self.dhanClientId = dhanClientId
        self.bnf_max_quantity = bnf_max_quantity
        self.nifty_max_quantity = nifty_max_quantity
        self.finnifty_max_quantity = finnifty_max_quantity
        self.midcap_max_quantity = midcap_max_quantity
        self.bankex_max_quantity = bankex_max_quantity
        self.sensex_max_quantity = sensex_max_quantity
        self.hard_sl = hard_sl
        self.soft_sl  = soft_sl
        self.max_risk_of_day = max_risk_of_day
        self.risk_per_trade = risk_per_trade
        self.kill_switch_risk = kill_switch_risk

    def __repr__(self) -> str:
        return f"Client_configuration(dhanClientId = {self.dhanClientId},bnf_max_quantity = {self.bnf_max_quantity},nifty_max_quantity = {self.nifty_max_quantity},finnifty_max_quantity = {self.finnifty_max_quantity},midcap_max_quantity = {self.midcap_max_quantity},bankex_max_quantity = {self.bankex_max_quantity},sensex_max_quantity = {self.sensex_max_quantity},hard_sl = {self.hard_sl},soft_sl = {self.soft_sl},max_risk_of_day = {self.max_risk_of_day},risk_per_trade = {self.risk_per_trade},kill_switch_risk = {self.kill_switch_risk})"
    
    def get_qty(self,index):
        if index == Index.BANKNIFTY:
            return self.bnf_max_quantity
        if index == Index.SENSEX:
            return self.sensex_max_quantity
        if index == Index.NIFTY:
            return self.nifty_max_quantity
        if index == Index.FINNIFTY:
            return self.finnifty_max_quantity
        
        

def dict_to_class(cls, d):
    # Prepare arguments by converting nested dictionaries
    kwargs = {}
    for key, value in d.items():
            # If value is a dictionary, recursively convert it
        if isinstance(value, dict):
                # You need to know or map the nested class types
            if key == 'client_config':
                nested_cls = Client_configuration
            else:
                continue
            kwargs[key] = dict_to_class(nested_cls, value)
        else:
            kwargs[key] = value
    return cls(**kwargs)    
