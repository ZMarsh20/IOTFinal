#include <SparkFun_MMA8452Q.h>
#include <MsTimer2.h>
#include <Wire.h>
#include <LiquidCrystal.h>

const int rs = 13, en = 12, d4 = 11, d5 = 10, d6 = 9, d7 = 8;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
MMA8452Q accel;

int counter, timer, timerDelay, lightDelay;
double tiltVal, avg;
enum lights {green = 2, yellow, red1, red2, red3};
bool wordPresent, notCalibrated, neutral, blinkVal, game, twoWords;
String noun;

void flipReds() {
  blinkVal = !blinkVal;
  for (int i = red1; i <= red3; i++) {
    digitalWrite(i, blinkVal);
  }
}

void calibrate() {
  if (counter++ < 50) {
    digitalWrite(red1, HIGH);
    avg += tiltVal;
    if (counter > 20) {
      digitalWrite(red2, HIGH);
    }
    if (counter > 40) {
      digitalWrite(red3, HIGH);
    }
  }
  else {
    flipReds();
    avg = (avg / 50) - 1; //- 1 makes 0 avg at 90 degrees
    notCalibrated = false;
  }
}

void answer(bool ans) {
  if (neutral) {
    Serial.println(ans - 2);
    digitalWrite(yellow - ans, LOW);
    digitalWrite(green + ans, HIGH);
    wordPresent = false;
    neutral = false;
    lightDelay = 0;
    noun = "";
    timerDelay = timer;
  }
}

void blinker() {
  if (timer <= 600) {
    Serial.println(timer);
  }
  if (timer < 500) {
    if (timer % 10 == 0) {
      flipReds();
    }
  } else if (timer < 600) {
    if (timer % 5) {
      flipReds();
    }
  } else {
    blinkVal = false;
    flipReds();
    game = false;
    lcd.clear();
  }
  timer++;
  lightDelay++;
}

void gameRun() {
  if (notCalibrated) {
    calibrate();
  } else {
    if (timer <= 650) {
      blinker();
      if (lightDelay == 10) {
        digitalWrite(green, LOW);
        digitalWrite(yellow, LOW);
      }
      if (wordPresent) {
        double tilt = 10 * (tiltVal - avg);
        if (tilt < -8.5) {
          answer(false);
        } else if (tilt > 8.5) {
          answer(true);
        } else if (tilt < 3 && tilt > -3) {
          neutral = true;
        }
      }
    } else if (blinkVal) {
      flipReds();
    }
  }
}

void formatInput(String in) {
  lcd.setCursor(0, 0);
  for (int i = 8; i > 0; i--) {
    if (in.length() == 15 - (2 * i) + twoWords
        || in.length() == 16 - (2 * i) + twoWords) {
      lcd.setCursor(i, twoWords);
      break;
    }
  }
}
void parseInput(char character) {
  timerDelay = timer;
  if (character == '\n') {
    wordPresent = true;

    if (!twoWords) {
      lcd.clear();
    }
    formatInput(noun);
    twoWords = false;
    lcd.print(noun);
    noun = "";

    if (timer > 620) {
      timer = 0;
      lightDelay = 0;
      game = true;
      neutral = false;
    }
  } else if (character == '_') {
    noun += ' ';
  } else if (character == ' ') {
    lcd.clear();
    formatInput(noun);
    twoWords = true;
    lcd.print(noun);
    noun = "";
  } else if (character == 27) {
    timer = 650;
    lcd.clear();
  } else {
    noun += character;
  }
}
void setup() {
  lcd.begin(16, 2);
  lcd.clear();
  Serial.begin(57600);
  Wire.begin();
  accel.begin();
  for (int i = green; i <= red3; i++) {
    pinMode(i, OUTPUT);
  }

  game = false;
  wordPresent = false;
  neutral = false;
  notCalibrated = true;
  blinkVal = false;
  twoWords = false;
  avg = 0;
  counter = 0;
  timer = 651;
  timerDelay = timer;
  lightDelay = 0;
  noun = "";

  MsTimer2::set(100, gameRun);
  MsTimer2::start();
}

void loop() {
  if (accel.available()) {
    tiltVal = accel.getCalculatedZ();
  }

  if (Serial.available()) {
    char character = Serial.read();
    parseInput(character);
  } else if (!wordPresent) {
    if (timer - timerDelay > 2) {
      char resend = 5;
      Serial.println(resend);
      noun = "";
    }
  }
}
