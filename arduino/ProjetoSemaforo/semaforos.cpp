#include "semaforos.h"

// --------------------
// PINOS
// --------------------

// Semáforo A
const int vermelhoA = 22;
const int amareloA  = 23;
const int verdeA    = 24;

// Semáforo B
const int vermelhoB = 26;
const int amareloB  = 27;
const int verdeB    = 28;

// Semáforo C
const int vermelhoC = 30;
const int amareloC  = 31;
const int verdeC    = 32;

// Semáforo D
const int vermelhoD = 34;
const int amareloD  = 35;
const int verdeD    = 36;


// --------------------
// TEMPOS
// --------------------

const unsigned long tempoAmarelo = 2000;
const unsigned long tempoSeguranca = 1000;


// --------------------
// ESTADO ATUAL
// --------------------

char viaAtual = 'N';


// --------------------
// FUNÇÕES AUXILIARES
// --------------------

void desligarTodosLEDs() {

  digitalWrite(vermelhoA, LOW);
  digitalWrite(amareloA, LOW);
  digitalWrite(verdeA, LOW);

  digitalWrite(vermelhoB, LOW);
  digitalWrite(amareloB, LOW);
  digitalWrite(verdeB, LOW);

  digitalWrite(vermelhoC, LOW);
  digitalWrite(amareloC, LOW);
  digitalWrite(verdeC, LOW);

  digitalWrite(vermelhoD, LOW);
  digitalWrite(amareloD, LOW);
  digitalWrite(verdeD, LOW);
}


void todosVermelhos() {

  desligarTodosLEDs();

  digitalWrite(vermelhoA, HIGH);
  digitalWrite(vermelhoB, HIGH);
  digitalWrite(vermelhoC, HIGH);
  digitalWrite(vermelhoD, HIGH);
}


void colocarAmarelo(char via) {

  todosVermelhos();

  switch (via) {

    case 'A':
      digitalWrite(vermelhoA, LOW);
      digitalWrite(amareloA, HIGH);
      break;

    case 'B':
      digitalWrite(vermelhoB, LOW);
      digitalWrite(amareloB, HIGH);
      break;

    case 'C':
      digitalWrite(vermelhoC, LOW);
      digitalWrite(amareloC, HIGH);
      break;

    case 'D':
      digitalWrite(vermelhoD, LOW);
      digitalWrite(amareloD, HIGH);
      break;
  }
}


void colocarVerde(char via) {

  todosVermelhos();

  switch (via) {

    case 'A':
      digitalWrite(vermelhoA, LOW);
      digitalWrite(verdeA, HIGH);
      break;

    case 'B':
      digitalWrite(vermelhoB, LOW);
      digitalWrite(verdeB, HIGH);
      break;

    case 'C':
      digitalWrite(vermelhoC, LOW);
      digitalWrite(verdeC, HIGH);
      break;

    case 'D':
      digitalWrite(vermelhoD, LOW);
      digitalWrite(verdeD, HIGH);
      break;
  }
}


// --------------------
// FUNÇÕES PÚBLICAS
// --------------------

void iniciarSemaforos() {

  pinMode(vermelhoA, OUTPUT);
  pinMode(amareloA, OUTPUT);
  pinMode(verdeA, OUTPUT);

  pinMode(vermelhoB, OUTPUT);
  pinMode(amareloB, OUTPUT);
  pinMode(verdeB, OUTPUT);

  pinMode(vermelhoC, OUTPUT);
  pinMode(amareloC, OUTPUT);
  pinMode(verdeC, OUTPUT);

  pinMode(vermelhoD, OUTPUT);
  pinMode(amareloD, OUTPUT);
  pinMode(verdeD, OUTPUT);

  todosVermelhos();

  viaAtual = 'N';
}


void abrirVia(char novaVia) {

  if (novaVia == viaAtual) {
    return;
  }

  if (viaAtual != 'N') {

    colocarAmarelo(viaAtual);

    delay(tempoAmarelo);

    todosVermelhos();

    delay(tempoSeguranca);
  }

  colocarVerde(novaVia);

  viaAtual = novaVia;
}


void fecharTodasVias() {

  todosVermelhos();

  viaAtual = 'N';
}


char obterViaAberta() {

  return viaAtual;
}


void atualizarSemaforos() {

  // Reservado para futuras atualizações
}
