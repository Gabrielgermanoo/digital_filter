import numpy as np
import matplotlib.pyplot as plt
import serial
import time

def radix2_fft(x):
    N = len(x)
    if np.log2(N) % 1 > 0:
        raise ValueError("O comprimento do sinal deve ser uma potência de 2")
    
    if N <= 1:
        return x
    
    even = radix2_fft(x[0::2])
    odd = radix2_fft(x[1::2])
    
    T = [np.exp(-2j * np.pi * k / N) * odd[k] for k in range(N // 2)]
    return [even[k] + T[k] for k in range(N // 2)] + [even[k] - T[k] for k in range(N // 2)]

def transmit_receive_fft_data(signal, port='COM8', baudrate=9600):  # Atualize a porta serial aqui
    try:
        ser = serial.Serial(port, baudrate)
    except serial.SerialException as e:
        print(f"Erro ao abrir a porta serial: {e}")
        return
    
    # Adicionar ruído branco ao sinal
    noise = np.random.normal(0, 0.1, len(signal))
    noisy_signal = signal + noise
    
    # Aplicar FFT no sinal com ruído
    fft_result = radix2_fft(noisy_signal)
    
    filtered_values = []
    
    for value in fft_result:
        # Transmitir um valor da FFT
        data = f"{value.real},{value.imag}\n"
        print(f"Enviando: {data.strip()}")
        ser.write(data.encode())
        time.sleep(0.1)  # Ajuste conforme necessário para a taxa de amostragem
        
        # Receber o valor filtrado correspondente
        print("Receber dados filtrados...")
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode().strip()
                print(f"Recebido: {line}")
                try:
                    real, imag = map(float, line.split(','))
                    filtered_values.append(complex(real, imag))
                    break  # Sair do loop interno após receber um valor válido
                except ValueError:
                    print(f"Erro ao converter linha: {line}")
    
    print("Fechando comunicação serial...")
    ser.close()
    
    # Plotar os resultados
    plt.figure()
    
    plt.subplot(3, 1, 1)
    plt.plot(noisy_signal, label='Sinal Original com Ruído')
    plt.legend()
    
    plt.subplot(3, 1, 2)
    plt.plot(np.abs(fft_result), label='FFT Original')
    plt.legend()
    
    plt.subplot(3, 1, 3)
    plt.plot(np.abs(filtered_values), label='FFT Filtrada')
    plt.legend()
    
    plt.show()

# Exemplo de uso
signal = np.random.rand(8)  # Sinal de exemplo com comprimento de potência de 2
transmit_receive_fft_data(signal)