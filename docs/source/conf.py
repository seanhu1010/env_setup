# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../../envlib'))
sys.path.insert(0, os.path.abspath('../../envlib/env'))
sys.path.insert(0, os.path.abspath('../../envlib/envsetup'))
sys.path.insert(0, os.path.abspath('../../envlib/env_resources'))

# -- Project information -----------------------------------------------------

project = 'env_setup_v2'
copyright = '2021, sean'
author = 'sean'

# The full version, including alpha/beta/rc tags
release = 'v0.0.2'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'recommonmark',
]

autodoc_default_options = {
    'member-order': 'bysource',  # 按代码顺序组织文档
    'private-members': True,  # 展示私有方法及属性
    'special-members': True,  # 展示魔术方法
    'undoc-members': True,  # 没有docstrings的方法将不展示
    'show-inheritance': True,  # 默认展示类和函数的 点'.'分层级
    'exclude-members': '__dict__',  # 排除不展示魔术方法__dict__,
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'zh_CN'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
