/*
  LiquidCrystal Library : http://www.arduino.cc/en/Tutorial/LiquidCrystalSerialDisplay

  The circuit:
  LCD RS pin to digital pin 12
  LCD Enable pin to digital pin 10
  LCD D4 pin to digital pin 8
  LCD D5 pin to digital pin 5
  LCD D6 pin to digital pin 4
  LCD D7 pin to digital pin 2

  Pas de réistance utilisé dans le circuit
*/

// include the library code:
#include <LiquidCrystal.h>

// initialize the library by associating any needed LCD interface pin
// with the arduino pin number it is connected to
const int rs = 12, en = 10, d4 = 8, d5 = 6, d6 = 4, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

const unsigned long DELAY_INTERVAL[10] = {0, 2000, 1500, 1000, 800, 650, 500, 300, 100, 50}; // Intervalle de décalage en millisecondes (première valeur pas utilisée)

String texteEcran[2] = {"Hello world à tous", "encore coucou"};

String lignes[2] = {"ligne 0 ", "ligne 1 "};
unsigned int index[2] = {0, 0};

unsigned long tempsActuel = 0; // Temps écoulé depuis la mise sous tension de la carte Arduino
unsigned long tempsDernierDecalage[2] = {0, 0};
unsigned int scroll[2] = {0, 0};

char delimiter = ';';

void setup()
{
  Serial.begin(9600); // initialize the serial communications:
  Serial.println("Initialisation arduino");
  lcd.begin(16, 2);   // set up the LCD's number of columns and rows:
  lcd.print("Hello world !");
  delay(1000);
  lcd.display();
  SplitDataEnLigne("0Hello world !;0Pret a recevoir");
}

void loop()
{

  // when characters arrive over the serial port...
  if (Serial.available())
  {
    // wait a bit for the entire message to arrive
    delay(10);
    // read all the available characters
    while (Serial.available() > 0)
    {
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
  while (i < 2 && data.length() > 0)
  {
    int delimiterIndex = data.indexOf(delimiter);
    scroll[i] = String(data[0]).toInt();
    lignes[i] = data.substring(1, delimiterIndex);
    while (lignes[i].length() < 16)
    {
      lignes[i] += " ";
    }
    if (delimiterIndex != -1)
    {
      data = data.substring(delimiterIndex + 1);
    }
    else
    {
      data = ""; // Sert a rien je crois
    }
    index[i] = 0;
    tempsDernierDecalage[i] = millis();
    i++;
  }
  return 0;
}

int StringToInt(String s)
{
  int res = -1;
  if (s == "0")
  {
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

  for (int i = 0; i < 2; ++i)
  {
    if (scroll[i] != 0) // Scroll
    {
      if (tempsActuel - tempsDernierDecalage[i] >= DELAY_INTERVAL[scroll[i]])
      {
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
