m_theme <- function() {
  theme_bw(base_size = 11) +
    theme(axis.line = element_line(colour = "grey32")) +
    theme(panel.grid.major.y = element_blank()) +
    theme(panel.grid.major.x = element_line(size = .1, colour = "grey92")) +
    theme(panel.grid.minor.y = element_blank()) +
    theme(panel.grid.minor.x = element_line(size = .1, colour = "grey92")) +
    theme(panel.border = element_blank()) +
    theme(panel.background = element_blank())
}
