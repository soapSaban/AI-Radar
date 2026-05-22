import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import os

print("[ ARCHITECTING NEURAL NETWORK ]")

# 1. Load the Data
coding_df = pd.read_csv('CODING_dataset.csv')
gaming_df = pd.read_csv('GAMING_dataset.csv')

# Combine them into one master dataset
df = pd.concat([coding_df, gaming_df], ignore_index=True)
df = df.dropna()

# 2. Preprocess the Labels (Machine Learning needs numbers, not text)
# CODING = 0, GAMING = 1
df['Label'] = df['Label'].map({'CODING': 0, 'GAMING': 1})

# Separate the Features (X) from the Answer (y)
X = df[['Distance', 'LDR_Left', 'LDR_Right', 'Temp']].values
y = df['Label'].values

# 3. Build the Brain
# A dense network is perfect for multi-modal sensor fusion
model = Sequential([
    Dense(16, input_dim=4, activation='relu'), # Input layer: 4 sensors
    Dense(8, activation='relu'),               # Hidden reasoning layer
    Dense(1, activation='sigmoid')             # Output layer: 0 to 1 confidence score
])

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# 4. Train the Model
print("\n[ INITIATING TRAINING SEQUENCE ]")
# We use 20% of your data as a 'validation test' to ensure it actually learns
history = model.fit(X, y, epochs=30, batch_size=10, validation_split=0.2)

# 5. Save the Brain
model.save('radar_brain.keras')
print("\n[ TRAINING COMPLETE ] Saved as 'radar_brain.keras'")