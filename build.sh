#!/bin/bash
# Render the full site: book + slides
quarto render --profile book
quarto render --profile slides

# Copy RevealJS slides into the book output so links resolve correctly
mkdir -p _book/slides
cp docs/slides/*.html _book/slides/
