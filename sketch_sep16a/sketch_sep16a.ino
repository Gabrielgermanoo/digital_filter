const float cutoff_frequency = 100.0;
const float sampling_frequency = 2048.0;
const float RC = 1.0 / (2.0 * 3.1416 * cutoff_frequency);
const float dt = 1.0 / sampling_frequency;
const float alpha = dt / (RC + dt);

float previous_filtered_val = 0.0;

void setup() {
  Serial.begin(115200);
  // analogReference(DEFAULT);
}

void loop() {
  if (Serial.available() > 0) {
    float rawValue = Serial.parseFloat();
    Serial.read();

    if (Serial.read() == '\n') {
      Serial.println(rawValue, 6);

      // Aplicar o filtro passa-baixa
      // float filteredValue = previous_filtered_val + alpha * (rawValue - previous_filtered_val);
      // previous_filtered_val = filteredValue;

      // Serial.print(filteredValue, 6);  // Enviar com precisão de 6 casas decimais
      // Serial.print(",");
      // Serial.println(0.0, 6);  // Enviar parte imaginária como 0.0
      // Serial.flush();
    }
  }
  
  // Pequeno atraso para evitar sobrecarga da CPU
  delay(10);
}