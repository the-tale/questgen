# coding: utf-8
import setuptools

setuptools.setup(
    name='Questgen',
    version='0.3.0',
    description='generator of nonlenear quests with events and flow validating',
    long_description = open('README.rst').read(),
    url='https://github.com/Tiendil/questgen',
    author='Aleksey Yeletsky <Tiendil>',
    author_email='a.eletsky@gmail.com',
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',

        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',

        'Natural Language :: English',
        'Natural Language :: Russian'],
    keywords=['gamedev', 'game', 'game development', 'quests', 'quests generation', 'procedural content generation'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    test_suite = 'tests',
    )
