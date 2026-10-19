#ifndef GEAR_RAY_WEAPONS_H
#define GEAR_RAY_WEAPONS_H

#define WEAPON_PISTOL 0
#define WEAPON_SHOTGUN 1
#define WEAPON_COUNT 2
#define WEAPON_OWNED_PISTOL 1
#define WEAPON_OWNED_SHOTGUN 2

/* A fixed owned mask and selected ID support bounded circular menu lookup. */
extern unsigned char owned_weapons;
extern unsigned char selected_weapon;
extern unsigned char shotgun_cell_x;
extern unsigned char shotgun_cell_y;
#define SHOTGUN_PICKUP_PRESENT (!(owned_weapons & WEAPON_OWNED_SHOTGUN))

#endif
