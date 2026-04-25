#!/bin/bash
# Render the full site: book + slides
quarto render --profile book
quarto render --profile slides
