reset;

model;

var x0 >=0;
var x1>=0;
var x2>=0;
var x3>=0;
var x4>=0;
var x5>=0;
var x6>=0;
var x7>=0;
var x8>=0;

# Funcion_Objetivo

minimize z: x0 + x1 + x2 + x3 + x4 + x5 + x6 + x7 + x8;

#Restricciones_de_tiempo

subject to t1: x1 - x0 >= 10;

subject to t2: x2 - x1 >= 5;

subject to t3: x3-x1 >= 8;

subject to t4: x4-x2 >= 3;

subject to t5: x5-x2 >= 7;

subject to t6: x5-x3 >= 7;

subject to t7: x6-x3 >= 5;

subject to t8: x7-x4 >= 10;

subject to t9: x7-x5 >= 10;

subject to t10: x7-x6 >= 10;

subject to t11: x8-x7 >= 2;



option solver cplex;
expand;
solve z;
display x1;
display x2;
display x3;
display x4;
display x5;
display x6;
display x7;
display x8;


