#include <iostream>
#include <vector>
#include <string>
#include <opencv2/opencv.hpp>
#include "yolo-fastestv2.h"

int main(int argc, char** argv) {
    // Verifica se o Python enviou o caminho da imagem corretamente
    if (argc != 2) {
        std::cerr << "Erro: Caminho da imagem nao fornecido." << std::endl;
        return -1;
    }

    std::string imagePath = argv[1];
    cv::Mat cvImg = cv::imread(imagePath);
    
    if (cvImg.empty()) {
        std::cerr << "Erro: Falha ao abrir a imagem em " << imagePath << std::endl;
        return -1;
    }

    // Inicializa a classe do YOLO
    yoloFastestv2 api;

    // Carrega o modelo (Atenção: o Python executa a partir da pasta raspberry/)
    // Portanto, o caminho relativo aqui deve bater com a execução do main.py
    api.loadModel("./yolo/modelo/semaforo.param", "./yolo/modelo/semaforo.bin");

    // Vetor que guardará as caixas detectadas
    std::vector<TargetBox> boxes;
    
    // Roda a inferência
    api.detection(cvImg, boxes);

    // ==========================================
    // GERA A SAÍDA EM FORMATO JSON PARA O PYTHON
    // ==========================================
    std::cout << "[";
    for (size_t i = 0; i < boxes.size(); i++) {
        std::cout << "{"
                  << "\"classe\":" << boxes[i].cate << ","
                  << "\"score\":" << boxes[i].score << ","
                  << "\"x1\":" << boxes[i].x1 << ","
                  << "\"y1\":" << boxes[i].y1 << ","
                  << "\"x2\":" << boxes[i].x2 << ","
                  << "\"y2\":" << boxes[i].y2
                  << "}";
        
        if (i < boxes.size() - 1) {
            std::cout << ",";
        }
    }
    std::cout << "]" << std::endl;

    return 0;
}