library(magrittr)
library(ggplot2)
library(dplyr)
library(reshape2)
library(xtable)
library(Hmisc)
library(forcats)

#####Plot actor distribution over time.

#All
file <- 'D:/Thesis/Actors/counts.csv'

data <- read.csv(file)

names(data) <- c('Year','European','National','Mixed','N')

pltData <- select(data,Year,European,Mixed,National) %>% melt(id.vars='Year') %>%
  rename(Percentage=value, Category = variable)
  
plt <- ggplot(pltData,aes(Year,Percentage,fill=Category)) + geom_area(show.legend = TRUE) +
  theme_minimal() + scale_fill_grey()
ggsave(plt,file='D:/Thesis/Figures/actor-area.pdf')

#Separate per paper_type
file <- 'D:/Thesis/Actors/papertype_counts.csv'

data <- read.csv(file)

names(data) <- c('Year','Paper_type','European','National','Mixed','N')

pltData <- select(data,Paper_type,Year,European,Mixed,National) %>% melt(id.vars=c('Year','Paper_type')) %>%
  rename(Percentage=value, Category = variable)

plt <- ggplot(pltData,aes(Year,Percentage,fill=Category)) + geom_area(show.legend = TRUE) +
  theme_minimal() + scale_fill_grey() + facet_grid(~ Paper_type)
ggsave(plt,file='D:/Thesis/Figures/actor-area-paper-type.pdf',width=9,height=4)

for (type in c('Tabloid','Quality')) {
  print(paste0(type,':'))
  data %>%
    filter(Paper_type == type) %>% 
    select(Year,European,National,Mixed) %>% 
    as.matrix %>% 
    rcorr %>%
    print
}

######Plot Sentiment things
file <- 'D:/Thesis/Sentiment/plotdata.csv'

data <- read.csv(file)

divide_helper <- function(x,y) {return(x/y)}
data$DATE_dt %<>%  divide_helper(1000) %>%
  as.POSIXlt(.,origin="1970-01-01") %>%
  as.Date
rm(divide_helper)

data$pos <- data$positive/data$total
data$neg <- data$negative/data$total
data$subj <- data$pos + data$neg
data <- data[!is.na(data$subj),]

#TABLE BY NEWSPAPER
group_by(data,MEDIUM) %>% summarise(b0 = '', N = n(), b1 = '', submu = mean(subj),subsd = sd(subj), b2 = '',
                                    posmu = mean(pos), possd = sd(pos), b3 = '', negmu = mean(neg), 
                                    negsd = sd(neg)) %>%
  xtable(digits=3)

#PLOT BY DATE
plt <- select(data,DATE_dt,pos,neg) %>% melt(id.vars='DATE_dt') %>%
  rename(Percentage=value, Tone = variable) %>% transform(Percentage = Percentage*100) %>%
  ggplot() + 
  geom_smooth(aes(DATE_dt,Percentage, linetype=Tone),
              method='gam',formula = y ~ s(x, bs = "cs",k=30), color = 'black') +
  theme_minimal() + xlab('Date') + ylab('Percentage of total words')
ggsave(plt,file='D:/Thesis/Figures/tone-time.pdf',width=9,height=3)

#CORRELATION WITH DATE
rcorr(transform(data,date_num = as.integer(DATE_dt)) %>% select(date_num,pos,neg) %>% as.matrix)  

######## Data description

file <- 'D:/Thesis/R/databeschrijving.csv'

EU_elections <- c('1994-06-09','1999-06-10','2004-06-10','2009-06-04','2014-05-22') %>% as.Date
NL_elections <- c('1994-05-03','1998-05-06','2002-05-15','2003-01-22','2006-11-22',
                  '2010-06-09','2012-09-12','2017-03-15') %>% as.Date
Referenda <- c('2005-06-01','2016-04-06') %>% as.Date
elections <- data.frame(Date=EU_elections,type='European Parliament') %>%
  rbind(data.frame(Date=NL_elections,type='Tweede Kamer')) %>%
  rbind(data.frame(Date=Referenda,type='Referendum'))

data <- read.csv(file) %>%
  rename(Medium = MEDIUM, Date = DATE_dt, Length = LENGTH) %>%
  transform(Date = as.Date(as.character(Date))) %>%
  mutate(Medium = fct_recode(Medium,'De Volkskrant' = 'de Volkskrant'))

plt <- ggplot() + 
  geom_histogram(aes(Date),data=data,bins=336, fill = 'gray48') + 
  theme_minimal() + 
  facet_wrap(~ Medium, nrow=5) +
  ylab('Count') +
  geom_vline(aes(xintercept=Date,linetype=type),data=elections,size=.3) +
  scale_linetype_manual(values=c('solid','longdash','dotdash')) +
  theme(legend.position = 'bottom') + labs(linetype='Type of elections: ')
ggsave(plt,file='D:/Thesis/Figures/hist-date-per-paper.pdf',width=7,height=10.5)

plt <- ggplot(data,aes(x=Length)) + 
  geom_histogram(bins=200, fill = 'black') + 
  theme_minimal() + 
  facet_wrap(~ Medium, nrow=5) + 
  ylab('Count')
ggsave(plt,file='D:/Thesis/Figures/hist-length-per-paper.pdf',width=6,height=9)

data %<>% filter(Medium %in% c('Algemeen Dagblad','De Telegraaf'))

plt <- ggplot() + 
  geom_histogram(aes(Date),data=data,bins=336, fill = 'black') + 
  theme_minimal() + 
  facet_wrap(~ Medium, nrow=1) +
  ylab('Count') +
  geom_vline(aes(xintercept=Date,linetype=type),data=elections,size=.3) +
  scale_linetype_manual(values=c('solid','longdash','dotdash')) +
  theme(legend.position = 'bottom') + labs(linetype='Type of elections: ')
ggsave(plt,file='D:/Thesis/Figures/hist-date-per-paper-tabloid.pdf',width=9,height=4)

######### LDA Perplexities

file <- 'D:/Thesis/R/perplexities.csv'

plt <- read.csv(file) %>%
  ggplot(aes(x=Model,y=Perplexity)) + geom_point() + geom_path() + theme_minimal() + xlab('Number of topics')
ggsave(plt,file='D:/Thesis/Figures/perplexity.pdf')


####### Actor bar charts

file <- 'D:/Thesis/Actors/newspaper_bar.csv'

data <- read.csv(file) %>%
  mutate(Newspaper = recode(MEDIUM,'de Volkskrant' = 'De Volkskrant'))

plotData <- melt(data, id.vars = 'Newspaper', measure.vars=c('Fully.European','Mixed','Fully.national')) %>%
  mutate(variable = recode(variable,'Fully.national' = 'Fully National', 'Fully.European' = 'Fully European')) %>%
  rename(Percentage = value, Category = variable)

order = data %>% arrange(desc(Fully.national)) %>% select(Newspaper) %>% lapply(as.character) %>% as.list %>% unlist

plt <- ggplot(plotData,aes(x=Newspaper,y=Percentage,fill= Category)) +
  geom_bar(stat = "summary", fun.y = "mean") +
  scale_x_discrete(limits=order) +
  theme_minimal() +
  scale_fill_grey() +
  theme(axis.text.x = element_text(angle = 90, hjust = 1))

ggsave(plt,file='D:/Thesis/Figures/paper-actor-type.pdf')
