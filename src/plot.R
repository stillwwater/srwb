library(tidyverse)
source("m_theme.R")

data <- read.csv("word_data.csv") %>%
  arrange(desc(freq))

selwords <- as.factor(read.csv("selected_words.csv")$selected_words)
selected <- data[which(data$word %in% selwords), ]

plt <- ggplot(selected) +
  geom_col(aes(x = reorder(word, freq), y = freq), fill = "#ef5350") +
  coord_flip() +
  m_theme() +
  labs(
    title = "Most popular words in /r/MechanicalKeyboards",
    x     = "",
    y     = "Frequency"
  )

print(plt)

ggsave(
  filename = "plot.png",
  plot     = plt,
  device   = "png",
  dpi      = 100,
  height   = 10,
  width    = 9
)

