/* Vérifie que mote.h compile en C et que la bibliothèque hôte se lie et répond. Lancé par la CI. */
#include <stdio.h>
#include "mote.h"

int main(void) {
    int64_t a = mote_now_ns();
    int64_t b = mote_now_ns();
    if (MOTE_ABI_VERSION != 1 || a < 0 || b < a) {
        fprintf(stderr, "smoke: échec (abi=%d a=%lld b=%lld)\n", MOTE_ABI_VERSION, (long long)a, (long long)b);
        return 1;
    }
    printf("smoke: ok (abi=%d)\n", MOTE_ABI_VERSION);
    return 0;
}
