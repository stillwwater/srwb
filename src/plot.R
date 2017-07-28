library(tidyverse)

data <- read.csv("word_data.csv") %>%
  arrange(desc(freq))

selwords <- as.factor(read.csv("selected_words.csv")$selected_words)
selected <- data[which(data$word %in% selwords), ]

plt <- ggplot(selected) +
  geom_col(aes(x = reorder(word, freq), y = freq), fill = "red3") +
  coord_flip() +
  labs(
    title = "Most popular words in /r/mechanicalkeyboards",
    x = "",
    y = "Frequency"
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

