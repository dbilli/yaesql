
from setuptools import setup, find_packages

install_requires = [
    "pyparsing"
]

setup(
    name="Yaesql",
    version="0.1",
    packages=find_packages(),

    install_requires=install_requires,

    author="Diego Billi",
    author_email="diegobilli@gmail.com",
    description="Yet Another ElasticSearch Query Language",
    keywords="ElasticSearch query language generator",
    url="https://https://github.com/dbilli/yaesql/",
    project_urls={
        "Bug Tracker"  : "https://github.com/dbilli/yaesql/issues",
        "Documentation": "https://https://github.com/dbilli/yaesql/",
        "Source Code"  : "https://code.example.com/HelloWorld/",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    
    test_suite="tests.run_tests",
)
