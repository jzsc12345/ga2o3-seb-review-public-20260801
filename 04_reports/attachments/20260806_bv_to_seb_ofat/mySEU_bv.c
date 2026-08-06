#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>
#include <malloc.h>
#include <string.h>
#include <template.h>
/*
 * SEU generation rate as a funcition of position and time (3D)
 * Statement: SINGLEEVENTUPSET
 * Parameter: F.SEU
 * Arguments:
 * x          location x (microns)
 * y          location y (microns)
 * z          location z (microns)
 * t          time (seconds )
 * *rat       generation rate per cc per sec.
 */
int seu(double x,double y,double z,double t,double *rat)
{
/* Pulse parameters preserved from the supplied SEB template. */
double LET=0.36; double q=1.6022e-19; double T0=4e-12; double Tc=2e-12;                         
/* x0 must match set xion=10.25 in bv_SEB_x10p25_300V.in. */
double r=0.05; double x0=10.25; 
double A; double R; double T;

   T = exp(-(pow((t-T0), 2) / pow(Tc, 2)));
   R = exp(-(pow(x-x0, 2) / pow(r, 2)));
   A = LET / (q * 3.142 * r * Tc);

   /* Restrict generation to the present Ga2O3 stack (y=0.0...0.6 um). */
   if((y >= 0.0) && (y <= 0.6)) 
   *rat = A * R * T;  
   else 
   *rat = 0;
    
	return(0);                /* 0 - ok */
}
