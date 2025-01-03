# example_bayesian_arima.py

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from model import BayesianARIMA, determine_arima_order, adf_test, BayesianSARIMA, determine_sarima_order
from utils import invert_differencing

# historical data for Apple Inc.
ticker = 'AAPL'
start_date = '2015-01-01'
end_date = '2023-12-31'
data = yf.download(ticker, start=start_date, end=end_date, interval='1d')

# target variable
y = data['Close']

# handle missing values
y = y.dropna()

# plot the original series
plt.figure(figsize=(12, 6))
plt.plot(y, label='Adjusted Close Price')
plt.title(f'{ticker} Adjusted Close Price')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()

order = (5, 1, 1, 1, 1, 2)


# initialize and train the Bayesian ARIMA model
p, d, q, P, D, Q = order
bayesian_arima = BayesianSARIMA(name="AAPL", p=p, d=d, q=q, m=2, P=P, D=D, Q=Q)

# load the model
bayesian_arima.load()

# prepare for forecasting
# differenced target series
y_diff = y.diff(d).dropna().values

# get the last 'p' observations from the differenced series
last_observations = y_diff[-p:]

steps = 5  # forecasting the next 5 days

# Generate forecasts
forecasts_diff = bayesian_arima.predict(steps=steps, last_observations=last_observations)
print("Forecasted Differenced Values:")
print(forecasts_diff)

# invert differencing to get the forecasted prices
forecast_values = invert_differencing(forecasts_diff, d, y)

print("Forecasted Adjusted Close Prices:")
print(forecast_values)

# forecast dates
last_date = y.index[-1]
forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=steps, freq='B')  # 'B' for business days

forecast_series = pd.Series(forecast_values, index=forecast_dates, name='Forecast')

print("Forecasted Adjusted Close Prices:")
print(forecast_series)

# plot the forecasts alongside historical data
plt.figure(figsize=(12, 6))
plt.plot(y, label='Historical')
plt.plot(forecast_series, label='Forecast', marker='o')
plt.title(f'{ticker} Adjusted Close Price Forecast')
plt.xlim(y.index[-20], forecast_dates[-1])              # zoom in on last 20 days
plt.ylim(150, 200)
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()
