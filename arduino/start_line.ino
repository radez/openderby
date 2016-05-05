/*
Using a 7-segment display with the 74HC595 shift register
*/

#include <Servo.h>
Servo start_gate;

#include <Wire.h>
#define SlaveDeviceId 0x04

int digit001 = 2; // cathode for Ones digit on the 7 segment
int digit010 = 3; // cathode for tens digit on the 7 segment
int digit100 = 4; // cathode for hundreds digit on the 7 segment

int latchpin = 5;// connect to pin 12 on the '595
int datapin = 6; // connect to pin 14 on the '595
int clockpin = 7; // connect to pin 11 on the '595

int demopin1 = 8;
int demopin2 = 9;
int gatepin_start = 10;
int gatepin_reset = 11;

int gateup = 20;
int gatedown = 120;
unsigned long gatetime = 0;
int gate = 120;

// the array contains the binary value to make digits 0-9
// for the number '11'  use code '31' for CC and '224' for CA
int segment[11] = {63,6,91,79,102,109,125,7,127,111,0 }; // for common cathode
//int segment[10] = {192,249,164,176,153,146,130,248,128,144 }; // for common anode
int text[18] = {92,115,121,84,0,94,121,80,124,102,0,0,0,0,0,0,0,0 }; // for common cathode

int digiton[3] = {digit001,digit010,digit100};
//int digit[10] = {253,251,247,239,253,251,247,239,253,251};
int pos = 0; // position in the matrix we're updating
int data[6][3] = { // data matrix 6 lanes, 3 digits per lane
  {8,8,8}, {8,8,8}, {8,8,8}, {8,8,8}, {8,8,8}, {8,8,8}
  //{0,1,2}, {3,4,5}, {6,7,8}, {9,10,11}, {12,13,14}, {15,16,17}
};


void shiftOutFast(uint8_t dataPin, uint8_t clockPin, uint8_t bitOrder, uint8_t val) {
// get rid of digital writes to make this actually fast
    uint8_t i;

    for (i = 0; i < 8; i++)  {
        if (bitOrder == LSBFIRST)
            digitalWrite(dataPin, !!(val & (1 << i)));
        else
            digitalWrite(dataPin, !!(val & (1 << (7 - i))));

        digitalWrite(clockPin, HIGH);
        digitalWrite(clockPin, LOW);
    }
}

void setup() {
  pinMode(digit001, OUTPUT);
  pinMode(digit010, OUTPUT);
  pinMode(digit100, OUTPUT);

  pinMode(latchpin, OUTPUT);
  pinMode(clockpin, OUTPUT);
  pinMode(datapin, OUTPUT);

  pinMode(demopin1, INPUT);
  digitalWrite(demopin1, HIGH);
  pinMode(demopin2, INPUT);
  digitalWrite(demopin2, HIGH);

  pinMode(gatepin_start, INPUT);
  digitalWrite(gatepin_start, HIGH);
  pinMode(gatepin_reset, INPUT);
  digitalWrite(gatepin_reset, HIGH);

  start_gate.attach(14); //analog pin 0

  // Start I²C bus as a slave
  Wire.begin(SlaveDeviceId);
  Wire.onReceive(receiveEvent);
  Serial.begin(9600);

}

void resetData() {
  pos = 0;
  for (int ln=0; ln<6; ln++) {
    for (int dgt=0; dgt<3; dgt++) {
      data[ln][dgt] = 10;
    };
  };
};

void saveValue(int i) {

  if (i >= 48 && i <=58) {
    data[pos / 3][pos++ % 3] = i - 48;
  }
  // clear the output
  if (i == 32) { // ascii 32 = space
    //Serial.print("\nreset\n");
    resetData();
  }

  // 18 digits total
  if (pos >= 18) { pos = 0; };

}


void serialRead() {
  int newline = 0;
  while (Serial.available()) {
    // get the new byte:
    int i = (int)Serial.read();
    Serial.print(i);
    Serial.print('\n');
    saveValue(i);
    newline = 1;
  }
}

void receiveEvent(int howMany) {
  while (1 < Wire.available()) { // loop through all but the last
    int i = Wire.read(); // receive byte as a character
    //Serial.print(i);         // print the character
  }
  int x = Wire.read();    // receive byte as an integer
  saveValue(x);
  //Serial.println(x);         // print the integer
}

void demoData() {
  int val = data[0][0];
  //Serial.println((millis() / 1000) % 10);

  if ( digitalRead(demopin1) ) {
  // scrolling based demo
    if ( val != (millis() / 1000) % 10 ) {
      val = (millis() / 1000) % 10;
      for (int ln=0; ln<6; ln++) {
        for (int lus=0; lus<3; lus++) {
          data[ln][lus] = val++;
          if (val == 10) { val = 0; };
        };
      };
    };
  };

  if (digitalRead(demopin2) ) {
    // build up demo
    //Serial.println(pos);
    if (data[pos / 3][pos % 3] == 10 && pos % 10 == (millis() / 1000) % 10 ) {
      data[pos / 3][pos % 3] = pos++ % 10;
    } else {
      if (data[pos / 3][pos % 3] == pos % 10 && pos % 10 == (millis() / 1000) % 10 ) {
        data[pos / 3][pos++ % 3] = 10;
      };
    };
  };

  // 18 digits total
  if (pos >= 18) { pos = 0; };
}

void loop() {
  if ( ! digitalRead(demopin1) || ! digitalRead(demopin2) ) {
    demoData();
  } else {
    serialRead();
  };

  // 3 digits per module
  for (int lus=0; lus<3; lus++) {
    // clear the digits
    digitalWrite(digit001, HIGH);
    digitalWrite(digit010, HIGH);
    digitalWrite(digit100, HIGH);
    digitalWrite(latchpin, LOW);

    // 6 modules total
    for (int ln=0; ln<6; ln++) {
      shiftOut(datapin, clockpin, MSBFIRST, segment[data[ln][lus]]);
      //shiftOut(datapin, clockpin, MSBFIRST, text[data[ln][lus]]);
    }

    digitalWrite(digiton[lus], LOW);

    digitalWrite(latchpin, HIGH);
    delay(6);
  }

  if (gate == gateup && ! digitalRead(gatepin_start) && millis() - gatetime > 3000) {
    //Serial.println(gate);
    //Serial.println(! digitalRead(gatepin_start));
    //Serial.println(millis() - gatetime)
    gatetime = millis();
    gate = gatedown;
    start_gate.write(gate);
  } else if (gate == gatedown && ! digitalRead(gatepin_reset) && millis() - gatetime > 3000) {
    //Serial.println(gate);
    //Serial.println(! digitalRead(gatepin_start));
    //Serial.println(millis() - gatetime);
    gatetime = millis();
    gate = gateup;
    start_gate.write(gate);
  };
}
