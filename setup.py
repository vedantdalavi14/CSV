"""
Setup configuration for Smart CSV Cleaner
"""

from setuptools import setup, find_packages

setup(
    packages=find_packages(exclude=["tests", "tests.*"]),
)
