# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from sphinx_pyproject import SphinxConfig

config = SphinxConfig("../pyproject.toml")

project = "(Better) TimeTagger CLI"
author = config.author
version = config.version
release = config.version

repo_url = "https://github.com/PassionateBytes/better-timetagger-cli"

rst_epilog = f"""
.. |project| replace:: {project}
.. |author| replace:: {author}
.. |version| replace:: {version}
.. |release| replace:: {release}
.. |br| raw:: html

   <br>
"""

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosectionlabel",
    "sphinx_toolbox.sidebar_links",
    "sphinx_toolbox.code",
    "sphinxcontrib.asciinema",
    "sphinx_click",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autoclass_content = "both"

# -- Autodoc-Pydantic configuration ------------------------------------------
# https://autodoc-pydantic.readthedocs.io/en/stable/users/configuration.html

autodoc_pydantic_model_signature_prefix = "pydantic schema"
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_model_show_validator_members = False
autodoc_pydantic_model_show_field_summary = False
autodoc_pydantic_model_show_json = True

autodoc_pydantic_field_list_validators = False
autodoc_pydantic_field_show_constraints = False
autodoc_pydantic_field_show_optional = False
autodoc_pydantic_field_show_required = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_title = project
copyright = f"{datetime.now().year}, {author}"
html_show_copyright = True
html_show_sphinx = False
html_sidebars = {"**": ["globaltoc.html", "versions.html"]}
pygments_style = "stata-dark"
pygments_dark_style = "stata-dark"