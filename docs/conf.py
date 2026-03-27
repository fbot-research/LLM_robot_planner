# Minimal Sphinx conf.py for Read the Docs and autodoc

import os
import sys
sys.path.insert(0, os.path.abspath(".."))  # permite importar o pacote/module raiz

project = "AutoBot"
author = "AutoBot Team"
release = "0.1"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Autodoc options
autodoc_member_order = "bysource"
autodoc_typehints = "signature"