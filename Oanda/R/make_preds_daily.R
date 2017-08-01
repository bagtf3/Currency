library(data.table)
library(quantmod)

options(digits = 6)

source("path/to/prep_file/prepdata.R")
source("path/to/helper_file/make_big_df_buy_sell.R")

#############
#############
#############

today <-as.Date(Sys.Date())
print(paste("Today is ", today, sep = ""))

dfs<-make_big_df_train(df)

buys<-dfs[[1]]
sells<-dfs[[2]]

new_df<-make_big_df_pred(df)
new_df<-na.omit(new_df)

###now we have the bigdfs we need. make predictions and investments and see how you do.

leads<-c(7, 14, 21, 28, 60, 90)
currs<-colnames(df)[-1]

#put predictions here
pred_df<-data.frame(matrix(0, ncol = ncol(df), nrow = 1 + length(leads)))
colnames(pred_df)<-colnames(df)
rownames(pred_df)<-c("Current", leads)

#need to get the dates programatically
aa<-colnames(buys)[grep("AUD.USD", colnames(buys))]
bb<-c("date", aa[grep("date", aa)])

#now extract the last row of data that matches those colnames
future_dates <- c(today, today + leads)
pred_df$date<-future_dates

#same for current values
current_prices<-as.numeric(df[nrow(df), colnames(df) %in% currs,])
pred_df[1,-1]<-current_prices

adjusted_df<-pred_df

###going to do a bunch of glms (bagging them, if you will)

for(c in 1:length(currs)){
  for(l in 1:length(leads)){
    #put preds here and average later
    preds_list<-c()
    
    #only need to make the formula and all that once
    #want to predict lead_p with all of the rm_p's for each c
    
    response<-paste(currs[c], "_lead_", leads[l], "_buys", sep = "")
    cols<-cng(buys, currs[c])
    keep<-cols[grep("ema", cols)]
    
    #max randomness
    
    for(rep in 1:3){
      
      interactions<-sample(1:length(keep), 5, replace = FALSE)
      dont_keep<-sample(1:length(keep), 5, replace = FALSE)
      
      keep_int<-keep[interactions]
      keep<-keep[-dont_keep]
      
      cs<-combn(keep_int, 2)
      int_list<-c()
      
      for(i in 1:ncol(cs)){
        a<-cs[1,i]
        b<-cs[2,i]
        int_list<-c(int_list, paste(a, b, sep = ":"))
      }
      
      f<-formula(paste(response, " ~ ", paste(keep, collapse = " + "), "+", paste(int_list, collapse = " + "),
                       sep = ""))
      
      samp<-sample(1:nrow(buys), round(nrow(buys)*0.85, 0), replace = FALSE)
      
      buys2<-buys[samp,]
      
      model<- glm(f ,family=binomial(link='logit'),data=buys2)
      preds_list[rep]<-predict(model, newdata = tail(new_df, 1), type = "response")
      
    }
    
    #now the sells
    #want to predict lead_p with all of the rm_p's for each c
    response<-paste(currs[c], "_lead_", leads[l], "_sells", sep = "")
    
    cols<-cng(sells, currs[c])
    keep<-cols[grep("ema", cols)]
    
    
    for(rep in 4:6){
      
      interactions<-sample(1:length(keep), 5, replace = FALSE)
      dont_keep<-sample(1:length(keep), 5, replace = FALSE)
      
      keep_int<-keep[interactions]
      keep<-keep[-dont_keep]
      
      cs<-combn(keep_int, 2)
      int_list<-c()
      
      for(i in 1:ncol(cs)){
        a<-cs[1,i]
        b<-cs[2,i]
        int_list<-c(int_list, paste(a, b, sep = ":"))
      }
      
      f<-formula(paste(response, " ~ ", paste(keep, collapse = " + "), "+", paste(int_list, collapse = " + "),
                       sep = ""))  
      samp<-sample(1:nrow(sells), round(nrow(sells)*0.85, 0), replace = FALSE)
      sells2<-sells[samp,]
      
      model<- glm(f ,family=binomial(link='logit'),data=sells2)
      preds_list[rep]<-predict(model, newdata = tail(new_df, 1), type = "response")* -1
      
    }
    
    adjusted_df[rownames(pred_df) == leads[l], colnames(pred_df) == currs[c]]<-round(mean(preds_list), 5)
    
  }
}

#############

#sink into file for preds
file = file("path/to/outfile/todays_preds.txt")
sink(file, append = FALSE)

for(c in 2:ncol(adjusted_df)){
  for(r in 2:nrow(adjusted_df)){
    
    action_list<-c()
    if(exists("action")){
      rm(action)
    }
    
    pred<-adjusted_df[r, c]
    
    if(abs(pred) > .3){
      
      rat<-0.03
      close_by<-adjusted_df[r,1]
      
      #completely adjustable here. This tunes sensitivity.
      un<-ifelse(abs(pred) %between% c(.29, .4), 10, ifelse(abs(pred) %between% c(.4, .45), 20, 40))
      
      item<-colnames(adjusted_df)[c]
      ifelse(pred > 0, assign('action', 'buy'), assign('action', 'sell'))
      
      current_price <-adjusted_df[1, c]
      units<- un #would be possible to adjust the units here if you see fit.
      
      if(action == 'buy'){
        action_list[1]<-"BUY"
        action_list[2]<- units
        action_list[3]<-item
        
        take_profit<- round(current_price * 1.03, 5)
        stop_loss <- round(current_price * 0.97, 5)
        
        action_list[4]<-take_profit
        action_list[5]<-stop_loss
        action_list[6]<-close_by
        
        print(paste("BUY: ", units, ", Instrument: ", item, ", Take Profit: ", 
                    take_profit, ", Stop Loss: ", stop_loss, ", Close by: ", close_by, sep = "" ))
      }
      
      if(action == 'sell'){
        action_list[1]<-"SELL"
        action_list[2]<- units
        action_list[3]<-item
        
        take_profit<- round(current_price * 0.97, 5)
        stop_loss <- round(current_price * 1.03, 5)
        
        action_list[4]<-take_profit
        action_list[5]<-stop_loss
        action_list[6]<-close_by
        
        print(paste("SELL: ", units, ", Instrument: ", item, ", Take Profit: ", 
                    take_profit, ", Stop Loss: ", stop_loss, ", Close by: ", close_by, sep = "" ))
      }
    }
  }
}

sink(file = NULL)
close(file)