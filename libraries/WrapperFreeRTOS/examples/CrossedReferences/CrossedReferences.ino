/**
 * @file CrossedReferences.ino
 * @author Alex Cajas (https://github.com/alexCajas/)
 * @brief Ejemplo básico de como usar referencias cruzadas.
 * @version 0.1
 */

#include "Controlador.hpp"

Controlador controlador("Controlador hogar");

void setup(){
    Serial.begin(115200);
    controlador.start();
}

void loop(){
    //tu codigo.
}