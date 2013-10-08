# coding: utf-8
import setuptools

setuptools.setup(
    name = 'Questgen',
    version = '0.1.0',
    author = 'Aleksey Yeletsky',
    author_email = 'a.eletsky@gmail.com',
    packages = setuptools.find_packages(),
    url = 'https://github.com/Tiendil/questgen',
    license = 'LICENSE',
    description = "Questgen - generator of nonlenear quests with events and flow validating",
    long_description = open('README.md').read(),
    include_package_data = True # setuptools-git MUST be installed
)
