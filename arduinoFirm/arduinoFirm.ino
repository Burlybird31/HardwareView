// C++ code
//
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x3F, 16, 2);

void setup()
{
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  
  lcd.init();
  lcd.backlight();
  
  lcd.setCursor(0, 0);
  lcd.print("SYSTEM MONITOR");
  lcd.setCursor(0, 1);
  lcd.print("Awaiting PC data");
  
}

void loop()
{
  if (Serial.available() > 0) {
  String cpuUtil = getString();
  String ramUsage = getString();
  String ramutil = getString();
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("CPU: ");
  lcd.print(cpuUtil);
  lcd.print("%");
    
  lcd.setCursor(0, 1);
  lcd.print("RAM: ");
  lcd.print(ramUsage);
  lcd.print("G ");
  lcd.print(ramutil);
  lcd.print("%");
  } }
  
String getString () {
  while (Serial.available() == 0 ) {
  }
  
  String combinedChar = "";
  while (Serial.available() > 0) {
    char activeChar = Serial.read();
    
    if (activeChar == ',') {
      Serial.println(combinedChar);
      return combinedChar;
    }
    
    combinedChar += activeChar;
    delay(10);
      
  }
  return combinedChar;
}