##backtest.py
## will backtest currency data vs predictions

import pandas as pd
import csv
import matplotlib.pyplot as plt
import portfolio as p

#going to start with 2000 and test again a default portfolio
my_portfolio = p.portfolio(cash = 2000, orders = [], leverage = 0, current_holdings = 0 )
portfolio_x = p.portfolio(cash = 2000, orders = [], leverage = 0, current_holdings = 0 )

cash_list = []
holdings_list = []
date_list = []
market_average = []
order_list = []
tp_sl = []

#this can be adjusted
max_orders = 500
master = pd.read_csv("path/to/currencydata.csv")

day_flag = 0
timecount = 0
takeprofit = 0
stoploss = 0 
clearcount=0

#initial investment multiplier = 1
#if we make money investing, we will increase the amount we can invest.
#This is tunable.
IM = 1

#main loop
for index, row in master.iterrows() :
    
    #keep track of the cash levels
    #read in date
    today = row['date']
    
    #set that dates you want to test here
    if today >= "2012-07-10" and today < "2017-04-10":
        if len(my_portfolio.orders) >= max_orders or my_portfolio.cash < -20000:
            my_portfolio.clearing_house(curs, prices)
            
            #if we get too many orders, we can clear some out.
            print "clearing house: new length of orders: " + str(len(my_portfolio.orders))
            clearcount+=1
            
        try:
            #open the file containing that days predictions.
            infile = open("Cpath/to/predictions" + today + ".csv", "r")
            preds = pd.read_csv(infile)
            infile.close()
        
        except:
            continue
    else:
        continue
    
    #ok, so first we want to reconcile existing orders, given the current day's prices
    curs = [x for x in preds.columns if x not in [ u'Unnamed: 0', "X", "NA", 'date']]
    prices = [x for x in row[1:10]]
    price_dict = {c:p for c, p in zip(curs, prices)}
    
    print str("\n" + today) + " double"
    
    for order in my_portfolio.orders:
        
        # current price
        cv = price_dict[order.currency]
        
        #first see if we are at the target date
        if order.close_by <= today:
            timecount+=1
            my_portfolio.close_order(order, current_val = cv)
        
        #next check the 'buys' to see if the take_prof or stop_loss is hit
        if order in my_portfolio.orders and order.type == 'buy':
            if cv >= order.take_prof:
                takeprofit+=1
                my_portfolio.close_order(order, current_val = cv)
            
            elif cv <= order.stop_loss:
                stoploss+=1
                my_portfolio.close_order(order, current_val = cv)
        
        #then the shorts
        elif order in my_portfolio.orders and order.type == 'short':
            if cv <= order.take_prof:
                takeprofit+=1
                my_portfolio.close_order(order, current_val = cv)
            
            elif cv >= order.stop_loss:
                stoploss+=1
                my_portfolio.close_order(order, current_val = cv) 
            
    #now we want to look at making new orders
    for col in curs:
        for r in xrange(1, 7):
            
            #this just sets up an 'index portfolio'
            if day_flag == 0:
                id = str(uuid.uuid4())
                portfolio_x.add_order(p.market_order(id, "short", currency = col, bought_price = row[col], quantity = int(2000/36), \
                                                   close_by = "3001-01-01", take_prof = 1000, stop_loss = -1000))
                
                #can adjust the sensitivity here
            if abs(preds[col][r]) >= .3 and len(my_portfolio.orders) < max_orders:
                
                #unique id
                id = str(uuid.uuid4())
                
                #first find out if we want to buy or short 
                if preds[col][r] > 0:
                    buy_or_short = "buy"
                else:
                    buy_or_short = "short"
                
                #now we want to create an order
                #you can set these quantities to whatever rates work best
                
                #preds[col][r] is the probability that a given currency will go up or down
                #based on our predictions.
                if abs(preds[col][r]) < .35:
                    quant = int(25*IM)
                    rat = .027
                elif abs(preds[col][r]) >= .35 and abs(preds[col][r]) < .45:
                    quant = int(50*IM)
                    rat = .03
                elif abs(preds[col][r]) >= .45:
                    quant = int(IM*80)
                    rat = .03
                
                #assume a 0.5% fee
                #set a take profit @ 90% of our estimation and a stoploss at a 5% loss
                if buy_or_short == 'buy':
                    type = buy_or_short
                    currency = col
                    bought_price = row[col] * 1.0005
                    quantity = quant
                    close_by = preds['date'][r]
                    take_prof = row[col]*( 1 + rat)
                    stop_loss = row[col] * 0.99
                                   
                    the_order = p.market_order(id, buy_or_short, currency, bought_price, \
                                               quantity, close_by, take_prof, stop_loss)
                    my_portfolio.add_order(the_order)
                
                elif buy_or_short == 'short':
                    type = buy_or_short
                    currency = col
                    bought_price = row[col] * 0.9995
                    quantity = quant
                    close_by = preds['date'][r]
                    take_prof = row[col]* (1 - rat)
                    stop_loss = row[col] * 1.01
                    
                    the_order = p.market_order(id, buy_or_short, currency, bought_price,\
                                               quantity, close_by, take_prof, stop_loss)
                    my_portfolio.add_order(the_order)
            else:
                pass
            
    #admin stuff
    date_list.append(today)
    cash_list.append(my_portfolio.cash)
    
    my_portfolio.calculate_holdings(curs, prices)
    print str(my_portfolio.current_holdings)
    
    order_list.append(len(my_portfolio.orders))
    holdings_list.append(my_portfolio.current_holdings)
    
    portfolio_x.calculate_holdings(curs, prices)
    market_average.append(portfolio_x.current_holdings)
    IM =  my_portfolio.current_holdings/2000
    day_flag = 1
    
    if stoploss == 0:
        tp_sl.append(0)
    else:
        tp_sl.append(float(takeprofit)/float(stoploss))
    
    #done?

#########
plt.plot(cash_list)
plt.plot(holdings_list)
plt.plot(market_average)
plt.plot(tp_sl)