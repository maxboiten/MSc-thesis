library(readtext)
library(quanteda)
library(magrittr)
library(dplyr)

file <- "D:/Thesis/corpus_lemma.csv"
corp <- readtext(file,text_field = "text", encoding = "utf-8") %>%
  corpus

# Set timestamp to actual date
divide_helper <- function(x,y) {return(x/y)}
docvars(corp,'date') %<>% divide_helper(1000) %>%
  as.POSIXlt(.,origin="1970-01-01") %>%
  as.Date
rm(divide_helper)

docvars(corp,'medium') %<>% as.factor %>%
  recode('AD/Algemeen Dagblad' = 'Algemeen Dagblad', 'Metro (NL)' = 'Metro', 'Metro (Netherlands)' = 'Metro')

dfm_lemma <- tokens(corp,remove_numbers=TRUE,remove_punct=TRUE,remove_symbols=TRUE,remove_separators=TRUE,
                    remove_hyphens=TRUE,remove_url=TRUE) %>%
  tokens_remove(stopwords(language = 'nl')) %>%
  dfm

save(dfm_lemma,file='D:/Thesis/dtm.Rdata')
