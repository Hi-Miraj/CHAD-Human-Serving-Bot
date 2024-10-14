#include <Servo.h>  //include servo.h library
#include<AFMotor.h>
Servo myservo;
 
int pos = 0;    
boolean fire = false;
 
int Left = A8;      // left sensor 
int Right = A9;    // right sensor
int Forward = A10;   //front sensor

AF_DCMotor LM(2);

AF_DCMotor RM(3);
AF_DCMotor pump(4);
 
void setup()
{
  pinMode(Left, INPUT);
  pinMode(Right, INPUT);
  pinMode(Forward, INPUT);
LM.setSpeed(150);
RM.setSpeed(150);
pump.setSpeed(150);
 
  myservo.attach(10);
  myservo.write(90); 
}
 
void put_off_fire()
{
    delay (500);
    LM.run(RELEASE);
    RM.run(RELEASE);
    pump.run(FORWARD);
   
   delay(500);
    
    for (pos = 50; pos <= 130; pos += 1) { 
    myservo.write(pos); 
    delay(10);  
  }
  for (pos = 130; pos >= 50; pos -= 1) { 
    myservo.write(pos); 
    delay(10);
  }
  pump.run(RELEASE);
 
  myservo.write(90);
  
  fire=false;
}
 
void loop()
{
   myservo.write(90); //Sweep_Servo();  
 
    if (digitalRead(Left) ==1 && digitalRead(Right)==1 && digitalRead(Forward) ==1) 
    {
    LM.run(RELEASE);
    RM.run(RELEASE);
   
    }
   
    else if (digitalRead(Forward) ==0) 
    {
       LM.run(FORWARD);
    RM.run(FORWARD);
  
    fire = true;
    }
    
    else if (digitalRead(Left) ==0)
    {
    LM.run(RELEASE);
    RM.run(FORWARD);
 
    }
    
    else if (digitalRead(Right) ==0) 
    {
          LM.run(FORWARD);
    RM.run(RELEASE);
  
    }
    
delay(300);//change this value to increase the distance



 
     while (fire == true)
     {
      put_off_fire();
     }
}
