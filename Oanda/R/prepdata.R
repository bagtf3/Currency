saved_file<-"path/saved/currencyfile.Rda"

#just incase
saved_filebackup<-"path/saved/currencyfile_backup.Rda"

load(saved_file)
save(df, file = saved_filebackup)

#now get todays data

from <- c("AUD", "EUR", "EUR", "GBP", "USD", "USD", "USD", "NZD", "EUR")
to <- c("USD", "GBP", "USD", "USD", "CAD", "JPY", "CHF", "USD", "JPY")

#if there is more than 1 day missing, get as many as we need.
# I believe the limit is 180, so the initial data source may need to come from somewhere else.

if(!((tail(df,1))$date >= Sys.Date() - 1)){
  start = (tail(df, 1))$date
  
  ##configure and use this function to get better data
  for(c in paste0(from, "/",to)){
    print(c)
    getFX(c, from = start, to = Sys.Date())
  }
  
  dflist<-c("EURGBP", "EURUSD", "GBPUSD", "USDCAD", "USDJPY", "USDCHF", "NZDUSD", "EURJPY")
  df_update<-data.frame(AUDUSD)
  df_update$date<-rownames(df_update)
  rownames(df_update)<-NULL
  df_update<-df_update[, c(2, 1)]
  
  for(c in dflist){
    tmp<-get(c)
    df_update<-cbind(df_update, as.vector(tmp[,1]))
  }
  
  colnames(df_update)<-colnames(df)
  df_update<-df_update[!(as.Date(df_update$date) %in% as.Date(df$date)),]
  
  df<-rbind(df, df_update)
}

#if we only need one day, use this.
if((tail(df,1)$date) == Sys.Date() -1){
  tmp<-data.frame(getQuote(paste0(from, to, "=X")))
  now<-data.frame(matrix(0, ncol = ncol(df), nrow = 1))
  colnames(now)<-colnames(df)
  now[1,1]<-as.Date(Sys.Date())
  
  now[1,-1]<-as.numeric(tmp$Last)
  now$date<-Sys.Date()
  now$date<-as.Date(now$date)
  df<-rbind(df, now)
  
}

#write the updated file inplace of the old one.
save(df, file = saved_file)