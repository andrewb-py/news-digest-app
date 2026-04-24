# Конфигурационный файл Sphinx

import os
import sys

# Добавляем корень проекта в путь Python
sys.path.insert(0, os.path.abspath('..'))


# -- Проект -----------------------------------------------------
project = 'News Digest App'
author = 'Andrew Baevsky'
release = '0.1.0'

copyright = '2026, Andrew Baevsky'


# -- Общие настройки ---------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.githubpages',
]

# Включаем поддержку Google и NumPy docstring
napoleon_google_docstring = True
napolean_numpy_docstring = False

# Автозагрузка модулей
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Путь к шаблонам
templates_path = ['_templates']

# Файлы и папки, которые нужно игнорировать
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    'venv',
    'migrations',
    'tests'
]


# -- Вывод HTML --------------------------------------------------
html_theme = 'sphinx_rtd_theme'

# Путь к статическим файлам
html_static_path = ['_static']

# Логотип и имя проекта
html_logo = '_static/logo.png'
html_favicon = '_static/favicon.ico'

# Дополнительные настройки темы
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False
}

# Дополнительные CSS/JS
# html_css_files = ['custom.css']
# html_js_files = ['custom.js']


# -- Вывод LaTeX (PDF) -------------------------------------------
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    'preamble': '',
    'figure_align': 'htbp'
}

# Группировка LaTeX
latex_documents = [
    (
        'index',
        'NewsDigestApp.tex',
        'Документация News Digest App',
        'Andrew Baevsky',
        'manual'
    ),
]


# -- Расширения --------------------------------------------------
# Если используете autoapi — раскомментируйте:
# extensions.append('autoapi.sphinx')
# autoapi_dirs = ['../app']
# autoapi_ignore = ['*/migrations/*', '*/tests/*', '*/__pycache__/*']
# autoapi_options = ['members', 'undoc-members', 'show-inheritance']
# autoapi_python_use_implicit_namespaces = True
