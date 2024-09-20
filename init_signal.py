import numpy as np
import matplotlib.pyplot as plt
import serial
import time


def plot_amplitude_vs_frequency(filtered_values, sampling_frequency):
    # Calcular a FFT dos valores filtrados
    fft_result = np.fft.fft(filtered_values)
    fft_freqs = np.fft.fftfreq(len(filtered_values), 1/sampling_frequency)
    
    # Calcular a magnitude
    magnitude = np.abs(fft_result)
    
    # Plotar amplitude vs frequência
    plt.figure(figsize=(10, 6))
    plt.plot(fft_freqs, magnitude)
    plt.title('Amplitude vs Frequência')
    plt.xlabel('Frequência (Hz)')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.show()

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

def transmit_receive_fft_data(signal, port='/dev/ttyACM0', baudrate=115200):  # Atualize a porta serial aqui
    try:
        ser = serial.Serial(port, baudrate)
        time.sleep(2)
    except serial.SerialException as e:
        print(f"Erro ao abrir a porta serial: {e}")
        return
    
    # Adicionar ruído branco ao sinal
    noise = np.random.normal(0, 0.1, len(signal))
    noisy_signal = signal + noise
    
    # Aplicar FFT no sinal com ruído
    fft_result = np.abs(radix2_fft(noisy_signal))
    
    filtered_values = []
    
    for value in noisy_signal:
        # Transmitir um valor da FFT
        data = f"{value.real}\n"
        #print(f"Enviando: {data.strip()}")
        ser.write(data.encode())
        
        # Receber o valor filtrado correspondente
        #print("Receber dados filtrados...")
        while ser.in_waiting == 0:
            pass

        if ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            #print(f"Recebido: {line}")
            filtered_values.append(float(line))
    
    print("Fechando comunicação serial...")
    ser.close()
    
    # Plotar os resultados
    plt.figure()
    
    plt.subplot(5, 1, 1)
    plt.plot(noisy_signal, label='Sinal Original com Ruído')
    plt.legend()
    
    plt.subplot(5, 1, 2)
    plt.plot(fft_result, label='FFT Original')
    plt.ylim(1500, 2200)
    plt.legend()
    
    plt.subplot(5, 1, 3)
    plt.plot(np.abs(radix2_fft(filtered_values)), label='FFT Filtrada')
    plt.ylim(1500, 2200)
    plt.legend()

    plt.subplot(5, 1, 4)
    plt.plot(filtered_values, label='Sinal Filtrado')
    plt.legend()

    plt.show()

    plot_amplitude_vs_frequency(filtered_values, 1024)


# Exemplo de uso
# definir a frequencia de amostragem
freq_a = 1024
n_amostras = 4096
periodo= 1/freq_a
t = np.arange(0, periodo * n_amostras, periodo)
signal = np.sin(2*np.pi * 10 * t) +  np.sin(2*np.pi * 200 * t) + np.sin(2*np.pi * 50 * t) # Sinal de exemplo com comprimento de potência de 2
transmit_receive_fft_data(signal)

