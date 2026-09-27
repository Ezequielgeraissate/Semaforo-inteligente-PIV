#include "semaforos.h"
#include "sensores.h"
#include "comunicacao.h"

void setup() {

  iniciarSemaforos();
  iniciarSensores();
  iniciarComunicacao();

  Serial.println("Sistema iniciado.");
}

void loop() {

lerSensores();

  enviarEventosSensores();

  processarComunicacao();

  atualizarSemaforos();

  delay(50);
}
