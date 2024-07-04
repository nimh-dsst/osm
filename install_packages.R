# Install devtools if not already installed
if (!requireNamespace("devtools", quietly = TRUE)) {
  install.packages("devtools")
}

# Install jsonlite package if not already installed
if (!requireNamespace("jsonlite", quietly = TRUE)) {
  install.packages("jsonlite")
}

if (!requireNamespace("pdftools", quietly = TRUE)) {
  install.packages("pdftools")
}

# Load devtools package
library(devtools)

# Install oddpub and rtransparent from GitHub
install_github("quest-bih/oddpub")
install_github("serghiou/rtransparent", build_vignettes = FALSE)
