import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'LLM Robot Planner'
copyright = '2026, FBOT@Research'
author = 'FBOT@Research'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.youtube'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme_options = {
    # --- Configuração das Logos ---
    "light_logo": "logo_white.png", # O nome do seu arquivo para o tema claro
    "dark_logo": "logo_black.png",  # O nome do seu arquivo para o tema escuro

    # --- Cores personalizadas para o modo claro ---
    "light_css_variables": {
        "color-brand-primary": "#2980b9", 
        "color-brand-content": "#2980b9", 
    },
    
    # --- Cores personalizadas para o modo escuro ---
    "dark_css_variables": {
        "color-brand-primary": "#ff5500", 
        "color-brand-content": "#ff5500", 
    },
    
    "sidebar_hide_name": True,
}

html_js_files = [
    "theme.js",
]

html_title = ""
html_theme = 'furo'
html_permalinks = False
html_static_path = ['_static']
html_css_files = ["css/custom.css"]
html_favicon = "_static/favicon.ico"
# html_logo = "_static/Submarca_fundo_claro.png"