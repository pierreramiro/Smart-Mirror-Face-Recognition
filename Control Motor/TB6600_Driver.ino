// 0.2     m/s
// 10/0.05 rev/m //medido en pulgadas
// 200     pulsos/rev
// Calculando, se tiene que STEPTIME es 1/8000 = 125usec 
// Los primeros 3 OFF y los tres ultimos ON
//6400 pulsos/rev @ 1A = 0.5 cm / seg
//1600 pulsos/rev @ 2.5A = 2 cm / seg
//Globals
#define STEPPIN 12   
#define DIRPIN 11    
#define ENAPIN 10     

const int STEPTIME = 125/2;
void setup() {
  // put your setup code here, to run once:
  pinMode(STEPPIN,OUTPUT);
  pinMode(DIRPIN,OUTPUT);
  pinMode(ENAPIN,OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  forward(1);
  
}

void forward(int steps){
  int i;
  digitalWrite(ENAPIN,LOW);//ENABLE IS ACTIVE LOW
  digitalWrite(DIRPIN,HIGH);//SET DIRECTION 
  for(i=0;i<steps;i++){
    digitalWrite(STEPPIN,HIGH);
    delayMicroseconds(STEPTIME);
    digitalWrite(STEPPIN,LOW);
    delayMicroseconds(STEPTIME);
  }
  digitalWrite(ENAPIN,HIGH);//DISABLE STEPPER
}

void reverse(int steps){
  int i;
  digitalWrite(ENAPIN,LOW);//ENABLE IS ACTIVE LOW
  digitalWrite(DIRPIN,LOW);//SET DIRECTION 
  for(i=0;i<steps;i++){
    digitalWrite(STEPPIN,HIGH);
    delayMicroseconds(STEPTIME);
    digitalWrite(STEPPIN,LOW);
    delayMicroseconds(STEPTIME);
  }
  digitalWrite(ENAPIN,HIGH);//DISABLE STEPPER
}
