library(stm)
library(magrittr)
library(quanteda)

load('D:/Thesis/dtm.Rdata')

seed <- 1528499063 #Current time in cpu ticks before starting the searchK
K_opts <- c(seq(3,10),seq(12,40,2))

dfm_lemma <- dfm_trim(dfm_lemma,min_docfreq = .001,max_docfreq = .8,docfreq_type='prop')
docvars(dfm_lemma,'date') %<>% as.numeric
stm_data <- convert(dfm_lemma, to = 'stm')

#Save some space
rm(corp,dfm_lemma)

set.seed(seed)
K_search <- searchK(stm_data$documents,
                    stm_data$vocab,
                    K=K_opts,
                    prevalence =~ medium,
                    data=stm_data$meta, 
                    proportion = .9)

save(K_search,stm_data,seed,file='D:/Thesis/R/searchK.Rdata')

#########################################

models <- selectModel(stm_data$documents,stm_data$vocab,K=10,prevalence = ~ medium,data = stm_data$meta, seed = seed)
save(models,file='D:/Thesis/R/stm10.Rdata')
