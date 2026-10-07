# Semáforo Inteligente

Projeto desenvolvido com o objetivo de criar um sistema de controle semafórico inteligente capaz de identificar a presença e a quantidade de veículos em diferentes vias e, a partir dessas informações, auxiliar na escolha da via que deverá receber prioridade.

O sistema utiliza sensores infravermelhos, Arduino Mega, Raspberry Pi, câmera OV5647 e visão computacional com YOLO-FastestV2.

---

## Objetivo

O objetivo do projeto é desenvolver um protótipo capaz de:

- detectar a presença de veículos nas vias;
- capturar imagens do cruzamento;
- identificar e contar veículos utilizando visão computacional;
- definir qual via deve receber prioridade;
- controlar quatro semáforos de forma automática e segura;
- futuramente disponibilizar informações em um dashboard e utilizar FPGA para aceleração de alguma etapa do processamento.

---

## Arquitetura Geral

O fluxo principal do sistema é:

```text
Sensores Infravermelhos
        ↓
Arduino Mega
        ↓
Comunicação Serial USB
        ↓
Raspberry Pi
        ↓
Câmera OV5647
        ↓
Imagem do cruzamento
        ↓
YOLO-FastestV2
        ↓
Contagem / identificação de veículos
        ↓
Lógica de decisão semafórica
        ↓
Comunicação Serial USB
        ↓
Arduino Mega
        ↓
4 Semáforos
