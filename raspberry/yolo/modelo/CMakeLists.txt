cmake_minimum_required(VERSION 3.10)
project(yolo_fastest_app)

set(CMAKE_CXX_STANDARD 11)

# Encontra as bibliotecas necessárias instaladas na Raspberry Pi
find_package(OpenCV REQUIRED)
find_package(ncnn REQUIRED)

# Junta seus códigos em um executável chamado "yolo_fastest"
add_executable(yolo_fastest main.cpp yolo-fastestv2.cpp)

# Linka o OpenCV e o NCNN ao seu executável
target_link_libraries(yolo_fastest ncnn ${OpenCV_LIBS})