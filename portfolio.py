class market_order:
    def __init__(self, id, type, currency, bought_price, quantity, close_by, take_prof, stop_loss):
        
        self.id = id
        self.type = type
        self.bought_price = bought_price
        self.quantity = quantity
        self.value = quantity
        self.currency = currency 
        self.close_by = close_by
        self.take_prof = take_prof
        self.stop_loss = stop_loss
    
    #use these methods for portfolio thinning
    def get_value(self, price):
        
        p = float(price)
    
        if self.type == 'buy':
            return p/self.bought_price * self.quantity
        if self.type == 'short':
            return self.quantity * self.bought_price/p

        
class portfolio:
    def __init__(self, cash, orders, leverage, current_holdings):
        
        self.cash = cash
        self.orders = orders
        self.leverage = leverage
        self.current_holdings = 0
    
    def adjust_cash(self, adj):
        
        self.cash = self.cash + adj
        
    def add_order(self, order):
        
        self.orders.append(order)
        self.adjust_cash( -order.quantity)
        
    def close_order(self, order, current_val):
        
        order_val = order.get_value(current_val)
        
        self.adjust_cash(order_val)
        self.orders.remove(order)
        
    def calculate_holdings(self, currencies, current_vals):
        assert isinstance(currencies, list)
        assert isinstance(current_vals, list)
        liquid = self.cash
        orders_value = 0
        
        for ord in self.orders:
            for cur, val in zip(currencies, current_vals):
                if ord.currency == cur:
                    orders_value = orders_value + ord.get_value(val)
        
        total_value = orders_value + liquid
        self.current_holdings = total_value
        
    def orders_list(self):
        return [o.id for o in self.orders]
    
    #something is wrong with this one. Only gets rid of half of the orders.
    def clearing_house(self, currencies, current_vals):
        for order in self.orders:
            for cur, val in zip(currencies, current_vals):
                if order.currency == cur:
                    self.close_order(order, val)
