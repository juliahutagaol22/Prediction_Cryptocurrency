# -*- coding: utf-8 -*-
"""lstm.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zbeo1eXSOCpCGlQ46kSszym5uTne1dB8
"""

pip install yfinance

# import Library

import math
from datetime import datetime
import yfinance as yf
import pandas_datareader.data as pdr
import pandas as pd

import pandas as pd
import numpy as np
import datetime as dt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM
import keras
import matplotlib.pyplot as plt

import missingno as msno

yf.pdr_override()

# Dataset
# df = pdr.get_data_yahoo("BNB-USD", start="2019-05-10", end="2022-05-10")
df = pdr.get_data_yahoo("DOGE-USD", start="2019-05-10", end="2022-05-10")
df

#Visualisasikan nilai yang hilang
msno.matrix(df)

# Cek tipe data
df.info()

# Cek History Harga Kripto dari tahun 2019 sampai 2022
plt.figure(figsize=(16,8))
plt.title("History Harga Crypto")
plt.plot(df['Close'])
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price (USD)', fontsize=18)
plt.show()

# Memisahkan data pelatihan(training) dengan data pengujian

# Buat Dataframe baru untuk colom "CLose"
data = df.filter(['Close'])

# Convert dataframe ke numpy
dataset = data.values

# Ambil 60% data sebagai data pelatihan
# Untuk data sebanyak 40% akan digunakan sebagai data pengujian untuk melakukan prediksi model
training_data_len = math.ceil( len(dataset) * .6)

training_data_len

#Normalisasi Data

# data akan dipetakan ke interval [0,1] untuk meningkatkan kecepatan konvergensi
# model dan meningkatkan akurasi model. Metode yang digunakan di sini disebut
# normalisasi min-max atau normalisasi 0-1.

#Skala Data
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dataset)

scaled_data

# Pada percobaan kali ini, timesteps yang digunakan adalah 60, yaitu data 60 hari pertama digunakan
# untuk memprediksi data hari ke-61.

# input LSTM membutuhkan array tiga dimensi yaitu sampel, langkah waktu dan fitur.

# Set data training
# Set data scaled
train_data = scaled_data[0:training_data_len, :]

# Split data menjadi x_train dan y_train
# x_train dan x_test akan digunakan sebagai data input LSTM,
x_train = []
y_train = []

for i in range (60, len(train_data)):
  x_train.append(train_data[i-60:i, 0])
  y_train.append(train_data[i,0])

  if i<=60:
    print(x_train)
    print(y_train)
    print()

# Convert x_train dan y_train ke numpy
x_train, y_train = np.array(x_train), np.array(y_train)

# Bentuk ulang data
# Ubah data 2D menjadi data 3D
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
x_train.shape

# Membangun Model LSTM

# Untuk lapisan memiliki 50 neuron LSTM, dan output dari lapisan ini adalah vektor 50 dimensi.
# Parameter input_shape mengharuskan kita untuk memasukkan array dua dimensi, termasuk timestep dan fitur.
# Parameter return_sequences digunakan untuk menyetel apakah akan mengembalikan larik yang berisi langkah waktu.
# True mengembalikan array tiga dimensi (ukuran batch, langkah waktu, jumlah unit).
# False mengembalikan array dua dimensi (ukuran batch, jumlah unit).

model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
model.add (LSTM(50, return_sequences=False))

# Dense artinya setiap node pada layer ini terhubung ke semua node pada layer sebelumnya.
# Parameter 25 dan 1 berarti ada 25 dan 1 neuron di lapisan pada percobaan ini.
model.add(Dense(25))
model.add(Dense(1))

# Jalankan Model
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])

# Train Model
model.fit(x_train, y_train, batch_size=1, epochs=1)

#Model struktur
model.summary()

# Pengujian data
# Buat array baru yang berisi nilai skala dari indeks 817 sampai 1096
test_data = scaled_data[training_data_len - 60:, :]

# Buat Data x_train dan y_train

x_test = []
y_test = dataset[training_data_len:, :]
for i in range(60, len(test_data)):
  x_test.append(test_data[i-60:i, 0])

# Convert data ke numpy
x_test = np.array(x_test)

# Bentuk ulang data
# Ubah data 2D menjadi data 3D
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

# Karena x_test telah dinormalisasi sebelumnya, kita perlu menggunakan
# fungsi inverse_transform() untuk membalikkannya.

# Model untuk mempediksi harga
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

# Dapatkan RMSE (Root Mean Squared Error)

rmse = np.sqrt (np.mean(predictions - y_test)**2)
rmse

mape = np.mean (np.abs((y_test - predictions ) / y_test)) * 100
mape

# Plot data
train = data[:training_data_len]
valid = data[training_data_len:]
valid['Predictions'] = predictions


# Visualisasi Data

plt.figure(figsize=(16,8))
plt.title('Model')
plt.xlabel('Date')
plt.ylabel('Close Price (USD)', fontsize=18)
plt.plot(train['Close'])
plt.plot(valid[['Close', 'Predictions']])
plt.legend(['Train', 'Val', 'Predictions'], loc='lower right')
plt.show()

valid

valid.head()

valid.tail()

#Prediksi harga menggunakan data 'Close' 60 hari terakhir

#Data quote
apple_quote = pdr.get_data_yahoo("BTC-USD", end="2022-04-27")

#Dataframe baru
new_df = apple_quote.filter(['Close'])

#Dapatkan data 'Close' 60 hari terakhir
last_60_days = new_df[-60:].values

# Set skala data  antara 0 dan 1
last_60_days_scaled = scaler.transform(last_60_days)

# Buat list kosong
X_test = []

# Append data 60 terakhir
X_test.append(last_60_days_scaled)

# Convert X_test data dan set ke numpy
X_test = np.array(X_test)

# Bentuk ulang data
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

# Dapatkan prediksi harga yang diskalakan
pred_price = model.predict(X_test)

# Batalkan skala
pred_price = scaler.inverse_transform(pred_price)
print(pred_price)

#Data quote
apple_quote2 = pdr.get_data_yahoo("BTC-USD", start="2022-04-28", end="2022-04-28")
print(apple_quote2['Close'])

