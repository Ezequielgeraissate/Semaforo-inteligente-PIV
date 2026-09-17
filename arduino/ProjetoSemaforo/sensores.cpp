#include "sensores.h"

// --------------------
// PINOS DOS SENSORES
// --------------------

const int sensorA = 40;
const int sensorB = 41;
const int sensorC = 42;
const int sensorD = 43;


// --------------------
// ESTADOS
// --------------------

bool estadoA = false;
bool estadoB = false;
bool estadoC = false;
bool estadoD = false;


// --------------------
// INICIALIZAÇÃO
// --------------------

void iniciarSensores() {

  pinMode(sensorA, INPUT);
  pinMode(sensorB, INPUT);
  pinMode(sensorC, INPUT);
  pinMode(sensorD, INPUT);
}


// --------------------
// LEITURA
// --------------------

void lerSensores() {

  estadoA = digitalRead(sensorA);
  estadoB = digitalRead(sensorB);
  estadoC = digitalRead(sensorC);
  estadoD = digitalRead(sensorD);
}


// --------------------
// RETORNO
// --------------------

bool sensorViaA() {
  return estadoA;
}

bool sensorViaB() {
  return estadoB;
}

bool sensorViaC() {
  return estadoC;
}

bool sensorViaD() {
  return estadoD;
}
