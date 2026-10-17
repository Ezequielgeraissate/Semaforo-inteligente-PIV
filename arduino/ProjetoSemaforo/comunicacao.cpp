#include <Arduino.h>

#include "comunicacao.h"
#include "sensores.h"
#include "semaforos.h"


// =====================================================
// CONFIGURAÇÕES
// =====================================================

// USB somente para DEBUG
const unsigned long BAUD_DEBUG = 115200;

// UART do HC-05
const unsigned long BAUD_BLUETOOTH = 9600;


// =====================================================
// ENVIAR MENSAGEM BLUETOOTH
// =====================================================

void enviarBluetooth(const char *mensagem) {

  // Comunicação REAL com Raspberry
  Serial1.println(mensagem);


  // Apenas DEBUG no computador
  Serial.print("[Arduino -> Raspberry] ");
  Serial.println(mensagem);
}


// =====================================================
// INICIALIZAÇÃO
// =====================================================

void iniciarComunicacao() {

  // Monitor Serial
  Serial.begin(BAUD_DEBUG);


  // HC-05
  //
  // Mega 2560:
  // TX1 = pino 18
  // RX1 = pino 19

  Serial1.begin(BAUD_BLUETOOTH);


  delay(500);


  Serial.println();
  Serial.println("[DEBUG] USB iniciada em 115200.");
  Serial.println("[DEBUG] HC-05 iniciado em 9600.");
  Serial.println("[DEBUG] Aguardando conexao Bluetooth.");
}


// =====================================================
// RECEBER COMANDOS DA RASPBERRY
// =====================================================

void processarComunicacao() {

  while (Serial1.available() > 0) {

    char comando = Serial1.read();


    // Ignora espaços e ENTER
    if (
      comando == '\n' ||
      comando == '\r' ||
      comando == ' '
    ) {

      continue;
    }


    Serial.print(
      "[Raspberry -> Arduino] "
    );

    Serial.println(comando);


    switch (comando) {


      // =================================================
      // TESTE DE COMUNICAÇÃO
      // =================================================

      case 'P':

        enviarBluetooth("PONG");

        break;


      // =================================================
      // VIA A
      // =================================================

      case 'A':

        Serial.println(
          "[ACAO] Abrir Via A"
        );

        abrirVia('A');

        enviarBluetooth(
          "VIA_A_SOLICITADA"
        );

        break;


      // =================================================
      // VIA B
      // =================================================

      case 'B':

        Serial.println(
          "[ACAO] Abrir Via B"
        );

        abrirVia('B');

        enviarBluetooth(
          "VIA_B_SOLICITADA"
        );

        break;


      // =================================================
      // VIA C
      // =================================================

      case 'C':

        Serial.println(
          "[ACAO] Abrir Via C"
        );

        abrirVia('C');

        enviarBluetooth(
          "VIA_C_SOLICITADA"
        );

        break;


      // =================================================
      // VIA D
      // =================================================

      case 'D':

        Serial.println(
          "[ACAO] Abrir Via D"
        );

        abrirVia('D');

        enviarBluetooth(
          "VIA_D_SOLICITADA"
        );

        break;


      // =================================================
      // TODAS VERMELHAS
      // =================================================

      case 'X':

        Serial.println(
          "[ACAO] Fechar todas as vias"
        );

        fecharTodasVias();

        enviarBluetooth(
          "TODAS_FECHADAS"
        );

        break;


      // =================================================
      // ESTADO DO SISTEMA
      // =================================================

      case 'S':

        Serial.println(
          "[ACAO] Estado solicitado pela Raspberry"
        );

        enviarEstadoSensores();

        enviarEstadoSemaforos();

        break;


      // =================================================
      // COMANDO INVÁLIDO
      // =================================================

      default:

        Serial.print(
          "[ERRO] Comando desconhecido: "
        );

        Serial.println(comando);

        break;
    }
  }
}


// =====================================================
// ESTADO DOS SENSORES
// =====================================================

void enviarEstadoSensores() {

  // Bluetooth

  Serial1.print("SENSORES:");

  Serial1.print(sensorViaA());
  Serial1.print(",");

  Serial1.print(sensorViaB());
  Serial1.print(",");

  Serial1.print(sensorViaC());
  Serial1.print(",");

  Serial1.println(sensorViaD());


  // Debug

  Serial.print(
    "[Arduino -> Raspberry] SENSORES:"
  );

  Serial.print(sensorViaA());
  Serial.print(",");

  Serial.print(sensorViaB());
  Serial.print(",");

  Serial.print(sensorViaC());
  Serial.print(",");

  Serial.println(sensorViaD());
}


// =====================================================
// ESTADO DOS SEMÁFOROS
// =====================================================

void enviarEstadoSemaforos() {

  char via = obterViaAberta();


  // Bluetooth

  Serial1.print(
    "VIA_ABERTA:"
  );

  Serial1.println(via);


  // Debug

  Serial.print(
    "[Arduino -> Raspberry] VIA_ABERTA:"
  );

  Serial.println(via);
}


// =====================================================
// EVENTOS DOS SENSORES
// =====================================================

void enviarEventosSensores() {

  static bool anteriorA = false;
  static bool anteriorB = false;
  static bool anteriorC = false;
  static bool anteriorD = false;


  bool atualA = sensorViaA();

  bool atualB = sensorViaB();

  bool atualC = sensorViaC();

  bool atualD = sensorViaD();


  // ===================================================
  // SENSOR A
  // ===================================================

  if (
    atualA &&
    !anteriorA
  ) {

    Serial.println(
      "[SENSOR] Deteccao na Via A"
    );

    enviarBluetooth(
      "DETECCAO:A"
    );
  }


  // ===================================================
  // SENSOR B
  // ===================================================

  if (
    atualB &&
    !anteriorB
  ) {

    Serial.println(
      "[SENSOR] Deteccao na Via B"
    );

    enviarBluetooth(
      "DETECCAO:B"
    );
  }


  // ===================================================
  // SENSOR C
  // ===================================================

  if (
    atualC &&
    !anteriorC
  ) {

    Serial.println(
      "[SENSOR] Deteccao na Via C"
    );

    enviarBluetooth(
      "DETECCAO:C"
    );
  }


  // ===================================================
  // SENSOR D
  // ===================================================

  if (
    atualD &&
    !anteriorD
  ) {

    Serial.println(
      "[SENSOR] Deteccao na Via D"
    );

    enviarBluetooth(
      "DETECCAO:D"
    );
  }


  anteriorA = atualA;

  anteriorB = atualB;

  anteriorC = atualC;

  anteriorD = atualD;
}
