library(TTR)
library(dplyr)

make_big_df_train<-function(df){

#fibs
lags<-c(1)
for(f in 1:11){
  y<-tail(lags, 1)
  z<-head(tail(lags, 2), 1)
  lags<-c(lags, y+z)
}


df2<-df

for(c in 2:ncol(df)){

  xx<-df[, c]
  
  for(i in 1:length(lags)){
    new<-EMA(xx, n = lags[i] + 1)
    df2<-cbind(df2, new)
    
    col_name<-paste("ema_", colnames(df)[c], lags[i], sep = "")
    colnames(df2)[ncol(df2)]<-col_name
  }
  
}

df3<-df

for(c in 2:ncol(df)){
  col<-colnames(df)[c]
  xx<-df2[, grep(col, colnames(df2))]
  all_cols<-colnames(xx)[-1]
  combs<-combn(all_cols, 2)
  
  for(q in 1:ncol(combs)){
    c1<-combs[1,q]
    c2<-combs[2,q]
    
    a<-xx[,colnames(xx) == c1]
    b<-xx[,colnames(xx) == c2]
    s <- sign(a - b)
    
    df3<-cbind(df3, s)
    new_name<-paste(c1, "_", c2, sep = "")
    colnames(df3)[ncol(df3)]<-new_name
  }
}

df3[df3 < 0]<-0
leads<-c(7, 14, 21, 28, 60, 90)

df_buys<-df
df_sells<-df

for(c in 2:ncol(df)){
  for(l in 1:length(leads)){

    new_date_name<-paste("date_", leads[l], "_", colnames(df)[c], sep = "")
    new_col_buys<-paste(colnames(df)[c], "_lead_", leads[l], "_buys", sep = "")
    new_col_sells<-paste(colnames(df)[c], "_lead_", leads[l], "_sells", sep = "")
    
    future<-lead(df[,c], leads[l])
    now<-df[,c]
    outcome<-future/now
    
    #has a harder time predicting buys that sells, so give it a little leeway
    buys<-ifelse(outcome >= 1.03, 1, 0)
    sells<-ifelse(outcome < 0.97, 1, 0)
    
    df_buys<-cbind(df_buys, buys)
    colnames(df_buys)[ncol(df_buys)]<-new_col_buys

    df_buys<-cbind(df_buys, lead(df[, 1], leads[l]))
    colnames(df_buys)[ncol(df_buys)]<-new_date_name
    
    df_sells<-cbind(df_sells, sells)
    colnames(df_sells)[ncol(df_sells)]<-new_col_sells
    
    df_sells<-cbind(df_sells, lead(df[,1], leads[l]))
    colnames(df_sells)[ncol(df_sells)]<-new_date_name
    
  }
}

df_buys<-df_buys[, 11:ncol(df_buys)]
df_sells<-df_sells[, 11:ncol(df_sells)]

big_df_buys<-na.omit(cbind(df3, df_buys))
big_df_sells<-na.omit(cbind(df3, df_sells))

df_list<-list(big_df_buys, big_df_sells)

return(df_list)

}


make_big_df_pred<-function(df){
  
  #fibs
  lags<-c(1)
  for(f in 1:11){
    y<-tail(lags, 1)
    z<-head(tail(lags, 2), 1)
    lags<-c(lags, y+z)
  }
  
  
  df2<-df
  
  for(c in 2:ncol(df)){
    
    xx<-df[, c]
    
    for(i in 1:length(lags)){
      new<-EMA(xx, n = lags[i] + 1)
      df2<-cbind(df2, new)
      
      col_name<-paste("ema_", colnames(df)[c], lags[i], sep = "")
      colnames(df2)[ncol(df2)]<-col_name
    }
    
  }
  
  df3<-df
  
  for(c in 2:ncol(df)){
    col<-colnames(df)[c]
    xx<-df2[, grep(col, colnames(df2))]
    all_cols<-colnames(xx)[-1]
    combs<-combn(all_cols, 2)
    
    for(q in 1:ncol(combs)){
      c1<-combs[1,q]
      c2<-combs[2,q]
      
      a<-xx[,colnames(xx) == c1]
      b<-xx[,colnames(xx) == c2]
      s <- sign(a - b)
      
      df3<-cbind(df3, s)
      new_name<-paste(c1, "_", c2, sep = "")
      colnames(df3)[ncol(df3)]<-new_name
    }
  }
  
  df3[df3 < 0]<-0
  
  return(df3)
  
}

cng<-function(df, grp){
  return(colnames(df)[grep(grp, colnames(df))])
}

#save(big_df_buys, file = "./big_df_buys.Rda")
#save(big_df_sells, file = "./big_df_sells.Rda")



