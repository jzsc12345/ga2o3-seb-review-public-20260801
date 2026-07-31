/****************************************************************************/
/* RUN118 ATLAS SCI F.VSATN probe: minimal pure-compute callback.           */
/* ABI source: atlas -T <filename>                                          */
/****************************************************************************/

#include <stdlib.h>
#include <math.h>
#include <ctype.h>
#include <malloc.h>
#include <string.h>
#include <template.h>

#define RUN118_ALPHA 4.637954033e7
#define RUN118_THETA 0.8
#define RUN118_TNOM 600.0

int vsatn(double xcomp, double ycomp, double temp,
          double *vsn, double *dvsn)
{
    double exp_term;
    double denom;

    if (vsn == 0 || dvsn == 0 || temp <= 0.0) {
        return(1);
    }

    exp_term = exp(temp / RUN118_TNOM);
    denom = 1.0 + RUN118_THETA * exp_term;

    *vsn = RUN118_ALPHA / denom;
    *dvsn = -RUN118_ALPHA * RUN118_THETA * exp_term
          / (RUN118_TNOM * denom * denom);

    return(0);
}
