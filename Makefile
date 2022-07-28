install:
	pip install .

test: install

test_backtest: test
	python -m unittest test.backtest

test_exchange: test
	python -m unittest test.exchange

test_helpers: test
	python -m unittest test.helpers

test_strategy: test
	python -m unittest test.strategy

test_all: test_backtest test_exchange test_helpers test_strategy
