#include "mbed.h"
#include "rtos.h"

//Photointerrupter input pins
#define I1pin D2
#define I2pin D11
#define I3pin D12

//Incremental encoder input pins
#define CHA   D7
#define CHB   D8  

//Motor Drive output pins   //Mask in output byte
#define L1Lpin D4           //0x01
#define L1Hpin D5           //0x02
#define L2Lpin D3           //0x04
#define L2Hpin D6           //0x08
#define L3Lpin D9           //0x10
#define L3Hpin D10          //0x20

Ticker MotorUpdate;
Ticker AngleUpdate;


//Mapping from sequential drive states to motor phase outputs
/*
State   L1  L2  L3
0       H   -   L
1       -   H   L
2       L   H   -
3       L   -   H
4       -   L   H
5       H   L   -
6       -   -   -
7       -   -   -
*/
//Drive state to output table
const int8_t driveTable[] = {0x12,0x18,0x09,0x21,0x24,0x06,0x00,0x00};

//Mapping from interrupter inputs to sequential rotor states. 0x00 and 0x07 are not valid
const int8_t stateMap[] = {0x07,0x05,0x03,0x04,0x01,0x00,0x02,0x07};  
//const int8_t stateMap[] = {0x07,0x01,0x03,0x02,0x05,0x00,0x04,0x07}; //Alternative if phase order of input or drive is reversed

//Phase lead to make motor spin
const int8_t lead = -2;  //2 for forwards, -2 for backwards

//Status LED
DigitalOut led1(LED1);

//Photointerrupter inputs
DigitalIn I1(I1pin);
DigitalIn I2(I2pin);
DigitalIn I3(I3pin);

//Motor Drive outputs
DigitalOut L1L(L1Lpin);
DigitalOut L1H(L1Hpin);
DigitalOut L2L(L2Lpin);
DigitalOut L2H(L2Hpin);
DigitalOut L3L(L3Lpin);
DigitalOut L3H(L3Hpin);

int8_t intState = 0;
int8_t intStateOld = 0;
int8_t orState = 0;    //Rotor offset at motor state 0

//Set a given drive state
void motorOut(int8_t driveState){
    
    //Lookup the output byte from the drive state.
    int8_t driveOut = driveTable[driveState & 0x07];
      
    //Turn off first
    if (~driveOut & 0x01) L1L = 0;
    if (~driveOut & 0x02) L1H = 1;
    if (~driveOut & 0x04) L2L = 0;
    if (~driveOut & 0x08) L2H = 1;
    if (~driveOut & 0x10) L3L = 0;
    if (~driveOut & 0x20) L3H = 1;
    
    //Then turn on
    if (driveOut & 0x01) L1L = 1;
    if (driveOut & 0x02) L1H = 0;
    if (driveOut & 0x04) L2L = 1;
    if (driveOut & 0x08) L2H = 0;
    if (driveOut & 0x10) L3L = 1;
    if (driveOut & 0x20) L3H = 0;
    }
    
    //Convert photointerrupter inputs to a rotor state
inline int8_t readRotorState(){
    return stateMap[I1 + 2*I2 + 4*I3];
    }

void motorStop(){
      
    //Turn off first
    L1L = 0;
    L1H = 0;
    L2L = 0;
    L2H = 0;
    L3L = 0;
    L3H = 0;
}


//Basic synchronisation routine    
int8_t motorHome() {
    //Put the motor in drive state 0 and wait for it to stabilise
    motorOut(0);
    wait(1.0);
    
    //Get the rotor state
    return readRotorState();
}
    
bool switchstate = false;
uint16_t counter = 0;
uint16_t threshold = 100;
uint16_t speed = 1;

uint8_t angleCallibration[6];

void pwmMotorOut(){    
    counter++;
    if(counter == 250){
        counter = 0;
        switchstate = false;
    }
    if(counter > threshold){
        switchstate = true;
    }
    motorOut((intState-orState+lead+switchstate+6)%6);
    return;
}    
   
void angleIncrease(){
    threshold += speed;
    if(threshold >= 250){
        threshold = 0;
        
    }
}    
    
InterruptIn Angle1(I1pin); //large angle interrupts
InterruptIn Angle2(I2pin);
InterruptIn Angle3(I3pin);
InterruptIn Direction1(CHA); //small angle interrupts
InterruptIn Direction2(CHB);    

int smallangle = 0;
float coilCallib[6];

void smallangleincrement(){
    smallangle++;
}

void opticalCallibrate(){ //gives the number of small angle divisions between each 
    int oldsmallangle = 0;
    Direction1.rise(&smallangleincrement);
    
    intState = readRotorState();
    motorOut((intState-orState+lead+6)%6);
    
    while(smallangle < 117){ //rotate once to get motor up to speed
        intState = readRotorState();
        if (intState != intStateOld) {
            intStateOld = intState;
            motorOut((intState-orState+lead+6)%6); //+6 to make sure the remainder is positive
        }
    }
    smallangle = 0;
    while(smallangle < 117){ //rotate again and record how many small angle increments it takes between each coil
        printf("%d\n\r", smallangle);
        intState = readRotorState();
        if (intState != intStateOld) {
            coilCallib[intState] = smallangle - oldsmallangle;
            oldsmallangle = smallangle;

            intStateOld = intState;
            motorOut((intState-orState+lead+6)%6); //+6 to make sure the remainder is positive
        }
    }
    
    Direction1.rise(NULL);
    float sum = 0;
    for(int i = 0; i < 6; i++){
        sum += coilCallib[i];
    }
    for(int i = 0; i < 6; i++){
        coilCallib[i] = 6*coilCallib[i]/sum;
    }
    motorHome();
}

Ticker rotationspeed;
Ticker speedtest;

void controlspeed(){
    counter++;
    if(counter == 250){
        counter = 0;
    }
    if(counter > threshold){
        motorOut((readRotorState()+orState+lead+6)%6);
    }
    else{
        motorStop();
    }
}

void nextrotor(){
    intStateOld = (intStateOld - 1)%6;
    motorOut((intState-orState+lead+6)%6);
}

int speedcounter = 0;

void countspeed(){
    speedcounter++;
}

void printspeed(){
    printf("speed = %d\n\r", speedcounter);
    speedcounter = 0;
}


//Main
int main() {
    
    //Initialise the serial port
    Serial pc(SERIAL_TX, SERIAL_RX);
    
    pc.printf("Hello\n\r");
    
    //Run the motor synchronisation
    orState = motorHome();
    pc.printf("Rotor origin: %x\n\r",orState);
    
    wait(1.0);
    opticalCallibrate();
    /*
    //while loop that waits for instructions and executes them
    float R, V;
    bool done = false;
    while(1){
        while(!pc.readable());
        pc.scanf("R%5f", &R);
        pc.scanf("V%5f", &V);
        pc.printf("%f rotations requested at %f speed\n\r",R, V);
        
        
        smallangle = 0;
        Direction1.rise(&smallangleincrement);
        Angle1.rise(&nextrotor);
        Angle2.rise(&nextrotor);
        Angle3.rise(&nextrotor);
        Angle1.fall(&nextrotor);
        Angle2.fall(&nextrotor);
        Angle3.fall(&nextrotor);
        int rotationangle = 117*R;
        while(smallangle < rotationangle);
    }
    */
    /*
    //orState is subtracted from future rotor state inputs to align rotor and motor states
    
    MotorUpdate.attach_us(&pwmMotorOut, 100);
    AngleUpdate.attach(&angleIncrease, 0.01);
    */
    //Poll the rotor state and set the motor outputs accordingly to spin the motor
    Angle1.rise(&countspeed);
    speedtest.attach(&printspeed,1);
    rotationspeed.attach_us(&controlspeed, 10);
    while (1) {
            
            //motorOut((intState-orState+lead+6)%6); //+6 to make sure the remainder is positive
        }
}
