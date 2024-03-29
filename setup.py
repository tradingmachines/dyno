from setuptools import setup


setup(
    # meta
    name="dyno",
    version="0.1.0",
    author="William Santos",
    author_email="w@wsantos.net",
    description="Backtesting framework for high-frequency trading strategies",
    url="https://github.com/tradingmachines/dyno",

    # publicly accessible packages
    package_dir={"": "lib"},
    packages=["dyno"],

    # dependencies
    install_requires=[
        "pyspark >= pyspark==3.3.1"])
