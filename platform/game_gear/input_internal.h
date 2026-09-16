#ifndef GEAR_RAY_INPUT_INTERNAL_H
#define GEAR_RAY_INPUT_INTERNAL_H

/* Resident input history shared only with the blocking Bank 2 pause menu.
 * Released bits leave input_blocked independently; START is never masked. */
extern unsigned int keys;
extern unsigned int previous_keys;
extern unsigned char input_blocked;

#endif
