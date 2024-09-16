const float cutoff_frequency = 5.0;
const float sampling_frequency = 100.0;
const float RC = 1.0 / (2.0 * 3.1416 * cutoffFrequency);
const float dt = 1.0 / samplingFrequency;
const float alpha = dt / (RC + dt);

float previous_filtered_val = 0.0;

void setup() {
  Serial.begin(9600);
  // analogReference(DEFAULT);
}

void loop() {
    if (Serial.available() > 0) {
    // Ler o valor recebido via Serial
    float rawValue = Serial.parseFloat();
    
    // Aplicar o filtro passa-baixa
    float filteredValue = previousFilteredValue + alpha * (rawValue - previousFilteredValue);
    previousFilteredValue = filteredValue;

    // Enviar o valor filtrado de volta via Serial
    Serial.println(filteredValue);
  }
}