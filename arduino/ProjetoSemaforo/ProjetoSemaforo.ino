#include "semaforos.h"
#include "sensores.h"
#include "comunicacao.h"


void setup() {

  iniciarSemaforos();

  iniciarSensores();

  iniciarComunicacao();


  Serial.println();
  Serial.println("==============================");
  Serial.println(" SEMAFORO INTELIGENTE");
  Serial.println("==============================");

  Serial.println("Sistema iniciado.");
  Serial.println("HC-05 configurado como SLAVE.");
  Serial.println("Aguardando Raspberry...");
  Serial.println();
}


void loop() {

  // Atualiza sensores
  lerSensores();


  // Verifica novas detecções
  enviarEventosSensores();


  // Recebe comandos da Raspberry
  processarComunicacao();


  // Atualiza semáforos
  atualizarSemaforos();


  delay(50);
}
