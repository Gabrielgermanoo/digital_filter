import numpy as np
import matplotlib.pyplot as plt
import serial
import time
from scipy.signal import lti, step

# Configurar a comunicação serial
ser = serial.Serial('COM3', 9600)

# Parâmetros do sistema
M1 = 0.02     
M2 = 0.0005 
K = 0.5       
b1 = 0.41     
b2 = 0.0041   
K1 = 0        

num = [M2, b2, K]
den = np.polymul([M1, b1, K + K1], [M2, b2, K])
den[-1] -= K**2

system = lti(num, den)

t, y = step(system)

# Enviar dados para a placa e receber valores filtrados
filtered_values = []
raw_values = y.tolist()

for value in raw_values:
    ser.write(f"{value}\n".encode())
    time.sleep(1.0 / 100)  # Ajuste conforme necessário para a taxa de amostragem
    if ser.in_waiting > 0:
        filtered_value = float(ser.readline().strip())
        filtered_values.append(filtered_value)

# Fechar a porta serial
ser.close()

# Plotar os resultados
plt.plot(raw_values, label='Raw Signal')
plt.plot(filtered_values, label='Filtered Signal')
plt.legend()
plt.show()