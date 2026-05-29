import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv1D, MaxPooling1D, Flatten
import os

print("[ ARCHITECTING 1D-CNN RADAR BRAIN ]")

# 1. Load the Data
coding_df = pd.read_csv('CODING_dataset.csv')
gaming_df = pd.read_csv('GAMING_dataset.csv')

df = pd.concat([coding_df, gaming_df], ignore_index=True)
df = df.dropna()

# 2. Preprocess the Labels
df['Label'] = df['Label'].map({'CODING': 0, 'GAMING': 1})

X = df[['Distance', 'LDR_Left', 'LDR_Right', 'Temp']].values
y = df['Label'].values

# --- CRITICAL FIX: RESHAPING FOR 1D-CNN ---
# A 1D-CNN expects data in the shape: (number_of_samples, time_steps, features)
# If you are not using time-series windows, you treat each row as a sequence of 1 time-step.
X = X.reshape((X.shape[0], 1, X.shape[1])) 
# Now X shape is (samples, 1, 4)

# 3. Build the Brain (Actual 1D-CNN Architecture)
model = Sequential([
    # The 1D Convolutional Layer sliding over the signal
    Conv1D(filters=16, kernel_size=1, activation='relu', input_shape=(1, 4)),
    
    # Optional: MaxPooling1D can be added here if your time_steps > 1
    
    # Flatten the sequence back into a 1D array for the final decision
    Flatten(),
    
    # Hidden reasoning layer
    Dense(8, activation='relu'),
    
    # Output layer: 0 to 1 confidence score
    Dense(1, activation='sigmoid')
])

model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# 4. Train the Model
print("\n[ INITIATING TRAINING SEQUENCE ]")
history = model.fit(X, y, epochs=30, batch_size=10, validation_split=0.2)

# 5. Save the Brain
model.save('radar_brain_1DCNN.keras')
print("\n[ TRAINING COMPLETE ] Saved as 'radar_brain_1DCNN.keras'")
