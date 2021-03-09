from setuptools import setup, find_packages

classifiers = [
    'DEVELOPMENT STATUS :: 4 - BETA',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9'
]

requires = [
    'certifi',
    'chardet',
    'idna',
    'requests',
    'urllib3'
]

setup(
    name='PSNAWP',
    version='2021.9.3',
    packages=find_packages(),
    install_requires=requires,
    project_urls={
        "Change Log": "https://github.com/isFakeAccount/psnawp/commits/",
        "Documentation": "https://psnawp.readthedocs.io/en/latest/",
        "Issue Tracker": "https://github.com/isFakeAccount/psnawp/issues",
        "Source Code": "https://github.com/isFakeAccount/psnawp",
    },
    url='https://github.com/isFakeAccount/psnawp',
    license='MIT',
    author='isFakeAccount',
    author_email='trevorphillips@gmx.us',
    description='Retrieve User Information, Trophies, Game and Store data from the PlayStation Network',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    keywords='PSN API',
    classifiers=classifiers
)
