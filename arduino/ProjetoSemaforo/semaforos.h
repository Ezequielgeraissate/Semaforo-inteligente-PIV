#ifndef SEMAFOROS_H
#define SEMAFOROS_H

#include <Arduino.h>

void iniciarSemaforos();

void atualizarSemaforos();

void abrirVia(char via);

void fecharTodasVias();

char obterViaAberta();

#endif
