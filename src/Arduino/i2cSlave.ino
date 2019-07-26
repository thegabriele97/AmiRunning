#include <Wire.h>

// MACROS
#define _abs(x) (x * (x < 0 ? -1 : 1))
#define BOOLCFG(mask) (bool_configs & mask)

static_assert(LOW == 0, "Expecting LOW to be 0");

enum protocol_field_e {
  REG = 0x0,
  COUNT = 0x1,
  START = 0x2
};

enum registers_e {
  REG_DIGITAL = 0x1,
  REG_DIG_PINMODE = 0x2, 
  REG_PROCEDURES = 0x3,
  REG_BIT_CONFIGS = 0x4
};

enum config_mask_e {
  M_VOLTMTR = 0x1,
  M_I2CLOG = 0x2
};

enum mode_e {
  MO_OUTPUT = 0x0,
  MO_INPUT = 0x1,
  MO_INPUT_RPU = 0x2
};

enum procedures_e {
  PROC_STEPPER = 0x0
};

static byte i2c_address = 0x8;
static byte VLTMTR_PIN = A0;

byte *data = (byte *)malloc(64 * sizeof *data);
int analog_value;
float voltage, old_volt = 0.5;
byte bool_configs = 0x00; /* 8 BIT ARRAY:
                          LSB+0: VOLTIMETER ENABLED (active high)
                          LSB+1: I2C SERIAL LOG ENABLED (active high)
                          LSB+2: ..
                          LSB+3: ..
                          LSB+4: ..
                          LSB+5: ..
                          LSB+6: ..
                          MSB-0: ..
                         */

void setup() {
  Wire.begin((int)i2c_address); // join i2c bus with address 0x8
  Wire.onReceive(receiveEvent); // receive event

  Serial.begin(9600);
}

void loop() {
   analog_value = analogRead(VLTMTR_PIN);
   voltage = (analog_value * 5.0) / 1024.0; 
   
   if (voltage < 0.1) {
     voltage = 0.0;
   } 

   // voltage is printed only if it's different
   // and if voltimeter is enabled
   if (BOOLCFG(M_VOLTMTR) && _abs(old_volt - voltage) > 0.9) {
    Serial.print("v= ");
    Serial.println(voltage);
    old_volt = voltage;
    return;
   }

   delay(100);
}

// function that executes whenever data is received from master
// this function is registered as an event, see setup()
void receiveEvent(int howMany) {
  int i;
  byte mode, tmp;

  i = 0;
  while (Wire.available()) {
    data[i++] = Wire.read();
  }

  if (BOOLCFG(M_I2CLOG)) {
    Serial.print("# bytes received: ");
    Serial.println(howMany, DEC);

    for (i = 0; i < howMany; i++) {
      Serial.print("0x");
      Serial.print(data[i], HEX);  
      Serial.print(" ");
    }
  }

  switch(data[REG]) {
    case REG_DIGITAL:
      // FIRST BYTE:  PIN
      // SECOND BYTE: STATE

      digitalWrite(data[START + 0], data[START + 1]);
      break;
      
    case REG_DIG_PINMODE:
      // FIRST BYTE:   PIN
      // SECOOND BYTE: PIN MODE
      // THIRD BYTE:   INITIAL STATE

      if (data[START + 1] == MO_INPUT_RPU) {
        mode = INPUT_PULLUP;
      } else {
        mode = (data[START + 1] == MO_OUTPUT) ? OUTPUT : INPUT; 
      }
      
      pinMode(data[START + 0], mode);
      digitalWrite(data[START + 0], data[START + 2]);
      break;

    case REG_BIT_CONFIGS:
      // FIRST BYTE:   BIT POSITION (all 0 except bit to swap)
      // SECOND BYTE:  BOOLEAN VALUE

      for (i = 0, tmp = 0x1; tmp; i++, tmp <<= 1) {
        if (data[START + 0] & tmp) {
          data[START + 1] <<= i;
          bool_configs = (bool_configs & ~tmp) | data[START + 1];

          i = 0;
          continue;
        }
      }

      break;
      
    case REG_PROCEDURES:
      Serial.println("No recognized procedure");
      break;
      
    default:
      Serial.print("No register Recognized: 0x");
      Serial.println(data[REG], HEX);
      break;
  }
}
