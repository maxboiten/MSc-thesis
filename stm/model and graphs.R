library(magrittr)
library(ggplot2)
library(stm)
library(gridExtra)
library(lubridate)
library(dplyr)

####searchK

load(file='D:/Thesis/R/searchK.Rdata')

plt1 <- ggplot(data=K_search$results,aes(K,exclus)) + geom_point() + geom_line(size=1,linejoin='round') + 
  theme_minimal() + xlab('') + ggtitle('Exclusivity') + ylab('') +
  theme(plot.title = element_text(hjust = 0.5))
plt2 <- ggplot(data=K_search$results,aes(K,semcoh)) + geom_point() + geom_line(size=1,linejoin='round') + 
  theme_minimal() + xlab('') + ggtitle('Semantic coherence') + ylab('') +
  theme(plot.title = element_text(hjust = 0.5))
plt3 <- ggplot(data=K_search$results,aes(K,heldout)) + geom_point() + geom_line(size=1,linejoin='round') + 
  theme_minimal() + xlab('') + ggtitle('Heldout likelihood') + ylab('') +
  theme(plot.title = element_text(hjust = 0.5))

plts <- grid.arrange(plt1,plt2,plt3,nrow=1)
ggsave('D:/Thesis/Figures/stm-Ksearch.pdf',plot=plts,width=10,height=4,dpi=600)

load('D:/Thesis/R/stm10.Rdata')

#Output semantic coherence
semcoh <- data.frame(models$semcoh)
names(semcoh) <- sprintf('topic %s',seq(10))

summarize(semcoh) %>% xtable

#Output exclusivity
exclus <- data.frame(models$exclusivity)
names(exclus) <- sprintf('topic %s',seq(10))

summarize(exclus) %>% xtable

#EVALUATE MODEL 9
model <- models$runout[[9]]

#word clouds (Saved by hand :/)
cloud(model,1,max.words=75,scale=c(3,.5))
cloud(model,2,max.words=75,scale=c(3,.5))
cloud(model,3,max.words=75,scale=c(3,.5))
cloud(model,4,max.words=75,scale=c(3,.5))
cloud(model,5,max.words=75,scale=c(3,.5))
cloud(model,6,max.words=75,scale=c(3,.5))
cloud(model,7,max.words=75,scale=c(3,.5))
cloud(model,8,max.words=75,scale=c(3,.5))
cloud(model,9,max.words=75,scale=c(3,.5))
cloud(model,10,max.words=75,scale=c(3,.5))

###Covariates
load('D:/Thesis/dtm.Rdata')

dfm_lemma <- dfm_trim(dfm_lemma,min_docfreq = .001,max_docfreq = .8,docfreq_type='prop')
docvars(dfm_lemma,'date') %<>% as.numeric
stm_data <- convert(dfm_lemma, to = 'stm')
rm(dfm_lemma)

prep <- estimateEffect(1:10 ~ medium + s(date,df=20), model, stm_data$meta)

#Plot topic proportion by year
yearseq <- seq(from = as.Date("1990-01-01"), to = as.Date("2018-01-01"), by = "year")
yearnames <- year(yearseq)

plot(prep,covariate='date',topics=1,method='continuous',printlegend=FALSE,linecol='black',xaxt='n')
axis(1,at = as.numeric(yearseq), labels = yearnames)

plot(prep,covariate='date',topics=2,method='continuous',printlegend=FALSE,linecol='black',xaxt='n')
axis(1,at = as.numeric(yearseq), labels = yearnames)

plot(prep,covariate='date',topics=3,method='continuous',printlegend=FALSE,linecol='black',xaxt='n')
axis(1,at = as.numeric(yearseq), labels = yearnames)

plot(prep,covariate='date',topics=4,method='continuous',printlegend=FALSE,linecol='black',xaxt='n')
axis(1,at = as.numeric(yearseq), labels = yearnames)

plot(prep,covariate='date',topics=5,method='continuous',printlegend=FALSE,linecol='black',xaxt='n')
axis(1,at = as.numeric(yearseq), labels = yearnames)

plot(prep,covariate='date',topics=6,method='continuous',printlegend=FALSE,linecol='black',xaxt='n')
axis(1,at = as.numeric(yearseq), labels = yearnames)

plot(prep,covariate='date',topics=7,method='continuous',printlegend=FALSE,linecol='black',xaxt='n')
axis(1,at = as.numeric(yearseq), labels = yearnames)

plot(prep,covariate='date',topics=8,method='continuous',printlegend=FALSE,linecol='black',xaxt='n')
axis(1,at = as.numeric(yearseq), labels = yearnames)

plot(prep,covariate='date',topics=9,method='continuous',printlegend=FALSE,linecol='black',xaxt='n')
axis(1,at = as.numeric(yearseq), labels = yearnames)

plot(prep,covariate='date',topics=10,method='continuous',printlegend=FALSE,linecol='black',xaxt='n')
axis(1,at = as.numeric(yearseq), labels = yearnames)

###PLOT TOPIC SUM
topics <- c(4,5,9)
minmax <- c('min','max')
plotData <- plot(prep,covariate='date',topics=topics,method='continuous')
data <- data.frame(Date=plotData$x) %>%
  mutate(Date=as.Date(Date,origin='1970-01-01')) %>%
  cbind(plotData$means %>% as.data.frame(col.names=paste0('mean',topics))) %>%
  cbind(plotData$ci[[1]] %>% as.data.frame %>% t %>% data.frame %>% rename(min=X2.5.,max=X97.5.)) %>%
  mutate(r4 = mean4-min) %>% select(-one_of(minmax)) %>%
  cbind(plotData$ci[[2]] %>% as.data.frame %>% t %>% data.frame %>% rename(min=X2.5.,max=X97.5.)) %>%
  mutate(r5 = mean5-min) %>% select(-one_of(minmax)) %>%
  cbind(plotData$ci[[3]] %>% as.data.frame %>% t %>% data.frame %>% rename(min=X2.5.,max=X97.5.)) %>%
  mutate(r9 = mean9-min) %>% select(-one_of(minmax)) %>%
  mutate(TopicSum = mean4+mean5+mean9,rSum = sqrt(r4^2 + r5^2 + r9^2)) %>%
  mutate(Bottom = TopicSum-rSum, Top = TopicSum+rSum)

plt <- ggplot(data) + 
  geom_line(aes(Date,TopicSum)) +
  geom_line(aes(Date,Bottom),linetype='dashed') +
  geom_line(aes(Date,Top),linetype='dashed') +
  theme_minimal() + 
  ylab('Sum of EU institution topic proportions')

ggsave(plt,file='D:/Thesis/Figures/stm-topicsum.pdf',width=9,height=4)

###PLOT BY MEDIUM
medium <- c('Algemeen Dagblad','Financieele Dagblad','Metro','Nederlands Dagblad','NRC Handelsblad',
            'NRC.NEXT','Reformatorisch Dagblad','De Telegraaf','De Volkskrant','Trouw')

plot(prep,covariate='medium',topic=1,custom.labels=medium,labeltype='custom',xlim = c(0,.15),xlab='Topic proportion')
plot(prep,covariate='medium',topic=2,custom.labels=medium,labeltype='custom',xlim = c(0,.15),xlab='Topic proportion')
plot(prep,covariate='medium',topic=3,custom.labels=medium,labeltype='custom',xlim = c(0,.15),xlab='Topic proportion')
plot(prep,covariate='medium',topic=4,custom.labels=medium,labeltype='custom',xlim = c(0,.15),xlab='Topic proportion')
plot(prep,covariate='medium',topic=5,custom.labels=medium,labeltype='custom',xlim = c(0,.18),xlab='Topic proportion')
plot(prep,covariate='medium',topic=6,custom.labels=medium,labeltype='custom',xlim = c(0,.25),xlab='Topic proportion')
plot(prep,covariate='medium',topic=7,custom.labels=medium,labeltype='custom',xlim = c(0,.15),xlab='Topic proportion')
plot(prep,covariate='medium',topic=8,custom.labels=medium,labeltype='custom',xlim = c(0,.15),xlab='Topic proportion')
plot(prep,covariate='medium',topic=9,custom.labels=medium,labeltype='custom',xlim = c(0,.18),xlab='Topic proportion')
plot(prep,covariate='medium',topic=10,custom.labels=medium,labeltype='custom',xlim = c(0,.15),xlab='Topic proportion')
