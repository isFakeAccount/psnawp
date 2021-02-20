from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9'
]

setup(
    name='PSNAWP',
    version='2021.20.2',
    packages=find_packages(),
    url='https://github.com/isFakeAccount/psnawp',
    license='MIT',
    author='isFakeAccount',
    author_email='trevorphillips@gmx.us',
    description='Retrieve User Information, Trophies, Game and Store data from the PlayStation Network',
    keywords='PSN API'
)
