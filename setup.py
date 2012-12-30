from setuptools import setup, find_packages

setup(
    name = 'xcri',
    version = '1.0.0',
    packages = find_packages(),
    install_requires = ['suds', 'requests', 'lxml'],
    url = 'https://github.com/CottageLabs/xcri',
    author = ['Richard Jones', 'Mark MacGillivray'],
    author_email = ['richard@cottagelabs.com', 'mark@cottagelabs.com'],
    description = 'XCRI Tools',
    license = 'CC0',
    classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
