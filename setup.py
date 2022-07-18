from setuptools import setup


setup(
    # meta
    name="dyno",
    version="0.1.0",
    author="William Santos",
    author_email="w@wsantos.net",
    description="Strategy backtesting framework built on Pyspark",
    url="https://github.com/tradingmachines/dyno",

    # publicly accessible packages
    package_dir={"": "lib"},
    packages=[
        # expose back testing api
        "dyno.backtest"],

    # dependencies
    install_requires=[
        "pyspark == 3.2.1",
        "tqdm == 4.47.0"])
