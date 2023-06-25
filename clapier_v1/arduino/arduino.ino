/*
  LiquidCrystal Library - Serial Input

  Demonstrates the use a 16x2 LCD display.  The LiquidCrystal
  library works with all LCD displays that are compatible with the
  Hitachi HD44780 driver. There are many of them out there, and you
  can usually tell them by the 16-pin interface.

  This sketch displays text sent over the serial port
  (e.g. from the Serial Monitor) on an attached LCD.

  The circuit:
   LCD RS pin to digital pin 12
   LCD Enable pin to digital pin 11
   LCD D4 pin to digital pin 5
   LCD D5 pin to digital pin 4
   LCD D6 pin to digital pin 3
   LCD D7 pin to digital pin 2
   LCD R/W pin to ground
   10K resistor:
   ends to +5V and ground
   wiper to LCD VO pin (pin 3)

  Library originally added 18 Apr 2008
  by David A. Mellis
  library modified 5 Jul 2009
  by Limor Fried (http://www.ladyada.net)
  example added 9 Jul 2009
  by Tom Igoe
  modified 22 Nov 2010
  by Tom Igoe
  modified 7 Nov 2016
  by Arturo Guadalupi

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/LiquidCrystalSerialDisplay

*/

/*
   0123456789ABCDEG
   prochain  10 min
   suivant   15 min
   ligneEcran000000

 * */


// include the library code:
#include <LiquidCrystal.h>

// initialize the library by associating any needed LCD interface pin
// with the arduino pin number it is connected to
const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

const unsigned int MAX_CHARACTERS = 31; // Nombre maximal de caractères par ligne + '\0'
const unsigned long DELAY_INTERVAL[10] = { 0, 2000, 1500,  1000, 800, 650, 500, 300, 100,50}; // Intervalle de décalage en millisecondes (première valeur pas utilisée)

String texteEcran[2] = {"Hello world à tous", "encore coucou"} ;

String lignes[2] = { "ligne0 ", "ligne1 " };
unsigned int index[2] = { 0, 0 };

unsigned long tempsActuel = 0; // Temps écoulé depuis la mise sous tension de la carte Arduino
unsigned long tempsDernierDecalage[2] = { 0, 0 };
unsigned int scroll[2] = { 0, 0 };

char delimiter = ';';


void setup() {
  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);
  // initialize the serial communications:
  Serial.begin(9600);
  lcd.print("Hello world! MQ");
  lcd.display();
  Serial.println("hello");
  delay(2000);
  lcd.setCursor(0, 1);
  lcd.print("Ready to com");
  lcd.display();
}

void loop() {
  // when characters arrive over the serial port...
  if (Serial.available()) {
    // wait a bit for the entire message to arrive
    //delay(100);

    // read all the available characters
    while (Serial.available() > 0) {
      // Récupération des data
      String data = Serial.readString();
      SplitDataEnLigne(data);
    }
  }

  AfficherEcran();
  delay(10);
}

int SplitDataEnLigne(String data)
{
  int i = 0;
  while (i < 2 && data.length() > 0) {
    int delimiterIndex = data.indexOf(delimiter);
    scroll[i] = String(data[0]).toInt();
    lignes[i] = data.substring(1, delimiterIndex);
    while (lignes[i].length() < 16)
    {
      lignes[i] += " ";
    }
    if (delimiterIndex != -1) {
      data = data.substring(delimiterIndex + 1);
    } else {
      data = ""; // Sert a rien je crois
    }
    index[i] = 0;
    tempsDernierDecalage[i]= millis();
    i++;
  }

  /*
    Serial.println();
    Serial.println("fin");
    Serial.print("scroll 0 : ");
    Serial.print(scroll[0]);
    Serial.print(" et scroll 1 : ");
    Serial.print(scroll[1]);
    Serial.println();

    Serial.println(lignes[0]);
    Serial.println(lignes[1]);
  */
  return 0;
}


int StringToInt(String s)
{
  int res = -1;
  if (s == "0") {
    res = 0;
  }
  else
  {
    res = s.toInt();
    res == 0 ? -1 : res;
  }
  return res;
}

void AfficherEcran()
{
  tempsActuel = millis();

  for (int i = 0 ; i < 2 ; ++i) {
    if (scroll[i] != 0) // Scroll
    {
      if (tempsActuel - tempsDernierDecalage[i] >= DELAY_INTERVAL[scroll[i]]) {
        tempsDernierDecalage[i] = tempsActuel;
        index[i] += 1;
        index[i] %= lignes[i].length();
      }
    }

    texteEcran[i] = lignes[i].substring(index[i]);
    if (texteEcran[i].length() < 16)
    {
      texteEcran[i] += lignes[i].substring(0, 16 - texteEcran[i].length());
    }
  }

  lcd.setCursor(0, 0);
  lcd.print(texteEcran[0]);
  lcd.setCursor(0, 1);
  lcd.print(texteEcran[1]);
  lcd.display();
}
