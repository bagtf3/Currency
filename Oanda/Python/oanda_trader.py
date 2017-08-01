import json
from oandapyV20 import API    # the client
import oandapyV20.endpoints.trades as trades
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.contrib.requests import TakeProfitDetails, StopLossDetails
from oandapyV20.contrib.requests import TrailingStopLossOrderRequest
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20
import datetime
import logging 

today = str(datetime.date.today())

#however much you added to the account. 500 = $500 initial invvestment.
added_funds = float(500)

# So I wanted to see if it was better at prediciton prices increases or
# decreases, so I originally kept longs and shorts seperate, but it got too
# messy.

log_file = "path/to/logfile_live.txt"
log_file_short = "path/to/log_file_short.txt

#this could be, for example, the predictions from R
# or you could do it natively in python.
infile = open("path/to/todays_preds.txt", "r")

#see the API documentation.
access_token = '123456789abcdefghijk'
accountID = '123456789'

api = API(access_token = access_token, environment = 'live')

if __name__ == '__main__':
    r = accounts.AccountDetails(accountID)
    api.request(r)
    
    #trades
    t = r.response['account']['trades']

    #NAV
    nav = float(r.response[u'account']['NAV'])
    
    #Investment Multiplier
    IM = nav/added_funds
    
    lf = open(log_file, "r")
    all_orders = lf.readlines()
    dupe_orders = all_orders[:]
    
    #check old orders first
    for order in all_orders:
        pred = order.split(',')
        
        #extract the date
        if pred[4].split(":")[1].strip('''" "\"\n''') <= today:       
            #get the id       
            #this is a mess. want to compare the id and see if that order is still open
            ID = pred[5].split(':')[1].strip('\n').strip('\"').strip(" ")
            ID = unicode(ID)
            close_trade = trades.TradeClose(accountID=accountID, tradeID = ID)
            
            #see if it has already been closed or not
            try:
                close_flag = 0
                for trade in t:
                    if trade['id'] == ID:
                        close_flag = 1
                        
                if close_flag > 0:
                    rv = api.request(close_trade)
                    print "Closing order " + ID + " successful. Removing from log file"
                    dupe_orders.remove(order)
                    
                elif close_flag == 0:
                    print "Order " + ID + " already closed. Removing from log file."
                    #should remove that order from dupe_orders
                    dupe_orders.remove(order)
                    
            except oandapyV20.exceptions.V20Error as err:
                print(r.status_code, err)
        else:
            pass
            #print(json.dumps(rv, indent=2))
    lf.close()
    
    #re-write the log file with the changes made
    lf = open(log_file, "w")
    for order in dupe_orders:
        lf.write(order)
    lf.close()


    ##############
    #create new orders
    ##############


    for action in infile:    
        pred = action.split(',')
        
        #how many
        p1 = pred[0].split(":")[0].split(" ")[1].strip('\"')
        if p1 == "SELL":
            UNITS = -1* int(pred[0].split(":")[1])
            acctID = shortID
        else:
            UNITS = int(pred[0].split(":")[1])
            acctID = accountID
        
        #now the rest    
        #must be ineger units, so we round and cast to an integer. This deals with the investment multiplier.
        
        UNITS = int(round(float(UNITS*IM),0))
        INSTRUMENT = "_".join(pred[1].split(":")[1].split(".")).strip(" ")
        
        #USD_JPY requires fewer decimals
        if INSTRUMENT in ['USD_JPY', 'GBP_JPY', 'EUR_JPY']:
            TAKE_PROFIT = round(float(pred[2].split(":")[1]), 2)
            STOP_LOSS = round(float(pred[3].split(":")[1]), 2)
        else:
            TAKE_PROFIT = round(float(pred[2].split(":")[1]), 4)
            STOP_LOSS = round(float(pred[3].split(":")[1]), 4)
        
        #the order
        mktOrder = MarketOrderRequest(
                instrument=INSTRUMENT,
                units=UNITS,
                takeProfitOnFill=TakeProfitDetails(price=TAKE_PROFIT).data,
                stopLossOnFill=StopLossDetails(price=STOP_LOSS).data)
        
        # create the OrderCreate request
        r = orders.OrderCreate(acctID, data=mktOrder.data)
        try:
            # create the OrderCreate request
            make_trade = api.request(r)
            try:
                fill_id = make_trade['orderFillTransaction']['id']    
                order_id = " ID: " + str(fill_id)+ '''\"\n'''
            except:
                fill_id = make_trade['orderCancelTransaction']['id']
                order_id = " ID: " + str(fill_id)+ '''\"\n'''
            
            print "Order " + str(fill_id) + " created successfully."
            
            #if it worked, add it to the log
            #have to build the new log entry first
            old_action = action.split(',')[1:5]
            new_amt = action.split(',')[0].split(':')[0] + ": " + str(abs(UNITS))
            new_action_list = []
            new_action_list.append(new_amt)
                
            for item in old_action:
                new_action_list.append(item.strip('\n').strip('\"'))    
            
            #add id and write
            new_action_list.append(order_id)
            to_write = ','.join(new_action_list)
            
            #write it out to the respective files
            if p1 == 'BUY':
                with open(log_file, "a") as lf:
                    lf.write(to_write)
            
            elif p1 == 'SELL':
                with open(log_file_short, "a") as lfs:
                    lfs.write(to_write)
                    
        except oandapyV20.exceptions.V20Error as err:
            print(r.status_code, err)
            
        #i dont remember what this does
        else:
            pass
            #print(json.dumps(rv, indent=2))
    infile.close()