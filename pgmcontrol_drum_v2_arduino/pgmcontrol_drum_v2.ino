#include <Arduino.h>

// digital out pins for solenoid valves
const int transistorPin1 = 8;
const int transistorPin2 = 10;
const int transistorPin3 = 13;
const int transistorPin4 = 11;
const int analogInPin1 = A3;
const int analogInPin2 = A5;
/*int data1 = 0;
int sensorvalue1 = 0;
int data2 = 0;
int sensorvalue2 = 0;*/

bool flag_1 = false;
bool flag_2 = false;
bool flag_3 = false;
bool flag_4 = false;

byte command;

unsigned long starting_time = millis();
unsigned long current_time = 0;

void setup(){
    Serial.begin(115200);
    //Serial.setTimeout(50);
    //Serial.print("\nSETUP:");
    //Serial.flush();
    
    //Add the PGM channels and start the control
    pinMode (transistorPin1, OUTPUT);
    pinMode (transistorPin2, OUTPUT);
    pinMode (transistorPin3, OUTPUT);
    pinMode (transistorPin4, OUTPUT);

    /*digitalWrite(transistorPin1, HIGH);
    digitalWrite(transistorPin2, HIGH);
    digitalWrite(transistorPin3, HIGH);
    digitalWrite(transistorPin4, HIGH);
    delay(100);*/
    digitalWrite(transistorPin1, LOW);
    digitalWrite(transistorPin2, LOW);
    digitalWrite(transistorPin3, LOW);
    digitalWrite(transistorPin4, LOW);
    Serial.println("started");
}

void loop(){

 /* sensorvalue1 = analogRead(analogInPin1);
  Serial.print(sensorvalue1);
  Serial.print(",");
  sensorvalue2 = analogRead(analogInPin2);
  Serial.print(sensorvalue2);
  Serial.print("\n");*/
    //Serial.println(Serial.available());
    if(Serial.available() > 0){
        String command = Serial.readStringUntil('\n');
        Serial.println("\tUSB: received command: " + String(command));
        command.trim();
        switch(command.toInt()){
            case 1: 
                if(flag_1){
                    digitalWrite(transistorPin1, LOW);
                }
                else digitalWrite(transistorPin1, HIGH);
                flag_1 = !flag_1;
                break;
            case 2: 
                if(flag_2){
                    digitalWrite(transistorPin2, LOW);
                }
                else digitalWrite(transistorPin2, HIGH);
                flag_2 = !flag_2;
                break;
            case 3: 
                if(flag_3){
                    digitalWrite(transistorPin3, LOW);
                }
                else digitalWrite(transistorPin3, HIGH);
                flag_3 = !flag_3;
                break;
            case 4: 
                if(flag_4){
                    digitalWrite(transistorPin4, LOW);
                }
                else digitalWrite(transistorPin4, HIGH);
                flag_4 = !flag_4; 
                break;
            case 5: 
            digitalWrite(transistorPin1, LOW);
            digitalWrite(transistorPin2, LOW);
            digitalWrite(transistorPin3, LOW);
            digitalWrite(transistorPin4, LOW);            
            break;
        }    
    }
    //delay(10);
}
