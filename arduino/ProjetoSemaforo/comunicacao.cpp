#include "comunicacao.h"
#include "semaforos.h"
#include "sensores.h"


void iniciarComunicacao() {

  Serial.begin(115200);

  delay(500);

  Serial.println("COMUNICACAO_OK");
}


void processarComunicacao() {

  if (Serial.available() > 0) {

    char comando = Serial.read();

    switch (comando) {

      case 'A':
        abrirVia('A');
        Serial.println("VIA_A_ABERTA");
        break;

      case 'B':
        abrirVia('B');
        Serial.println("VIA_B_ABERTA");
        break;

      case 'C':
        abrirVia('C');
        Serial.println("VIA_C_ABERTA");
        break;

      case 'D':
        abrirVia('D');
        Serial.println("VIA_D_ABERTA");
        break;

      case 'X':
        fecharTodasVias();
        Serial.println("TODAS_FECHADAS");
        break;

      case 'S':
        enviarEstadoSensores();
        enviarEstadoSemaforos();
        break;
    }
  }
}


void enviarEstadoSensores() {

  Serial.print("SENSORES:");

  Serial.print(sensorViaA());
  Serial.print(",");

  Serial.print(sensorViaB());
  Serial.print(",");

  Serial.print(sensorViaC());
  Serial.print(",");

  Serial.println(sensorViaD());
}


void enviarEstadoSemaforos() {

  Serial.print("VIA_ABERTA:");

  Serial.println(obterViaAberta());
}

void enviarEventosSensores() {

  static bool anteriorA = false;
  static bool anteriorB = false;
  static bool anteriorC = false;
  static bool anteriorD = false;

  // Sensores IR normalmente trabalham em LOW quando detectam.
  // Se o seu sensor trabalhar em HIGH, troque LOW por HIGH.
  bool atualA = (sensorViaA() == LOW);
  bool atualB = (sensorViaB() == LOW);
  bool atualC = (sensorViaC() == LOW);
  bool atualD = (sensorViaD() == LOW);

  if (atualA && !anteriorA) {
    Serial.println("DETECCAO:A");
  }

  if (atualB && !anteriorB) {
    Serial.println("DETECCAO:B");
  }

  if (atualC && !anteriorC) {
    Serial.println("DETECCAO:C");
  }

  if (atualD && !anteriorD) {
    Serial.println("DETECCAO:D");
  }

  anteriorA = atualA;
  anteriorB = atualB;
  anteriorC = atualC;
  anteriorD = atualD;
}
