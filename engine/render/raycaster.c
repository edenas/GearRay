#include "camera.h"
#include "raycaster.h"
#include "world.h"

#define WALL_HEIGHT_SCALE 16384
#define GAME_GEAR_SCREEN_HEIGHT 144
#define RAY_COUNT 40
#define FIXED_POINT_SCALE 256
#define DDA_INFINITY 0xffffffffUL
#define DDA_RECIPROCAL_MAX_MAGNITUDE 512
#define CAMERA_PLANE_RANGE 512

/*
 * Exact Q8.8 DDA reciprocals for camera ray magnitudes 1..512.
 * Entry n is floor(65536 / n); entry zero is unused because a
 * zero-direction axis is represented by DDA_INFINITY.
 */
static const unsigned long dda_reciprocal_by_magnitude[
    DDA_RECIPROCAL_MAX_MAGNITUDE + 1] = {
    0UL, 65536UL, 32768UL, 21845UL, 16384UL, 13107UL, 10922UL, 9362UL,
    8192UL, 7281UL, 6553UL, 5957UL, 5461UL, 5041UL, 4681UL, 4369UL,
    4096UL, 3855UL, 3640UL, 3449UL, 3276UL, 3120UL, 2978UL, 2849UL,
    2730UL, 2621UL, 2520UL, 2427UL, 2340UL, 2259UL, 2184UL, 2114UL,
    2048UL, 1985UL, 1927UL, 1872UL, 1820UL, 1771UL, 1724UL, 1680UL,
    1638UL, 1598UL, 1560UL, 1524UL, 1489UL, 1456UL, 1424UL, 1394UL,
    1365UL, 1337UL, 1310UL, 1285UL, 1260UL, 1236UL, 1213UL, 1191UL,
    1170UL, 1149UL, 1129UL, 1110UL, 1092UL, 1074UL, 1057UL, 1040UL,
    1024UL, 1008UL, 992UL, 978UL, 963UL, 949UL, 936UL, 923UL,
    910UL, 897UL, 885UL, 873UL, 862UL, 851UL, 840UL, 829UL,
    819UL, 809UL, 799UL, 789UL, 780UL, 771UL, 762UL, 753UL,
    744UL, 736UL, 728UL, 720UL, 712UL, 704UL, 697UL, 689UL,
    682UL, 675UL, 668UL, 661UL, 655UL, 648UL, 642UL, 636UL,
    630UL, 624UL, 618UL, 612UL, 606UL, 601UL, 595UL, 590UL,
    585UL, 579UL, 574UL, 569UL, 564UL, 560UL, 555UL, 550UL,
    546UL, 541UL, 537UL, 532UL, 528UL, 524UL, 520UL, 516UL,
    512UL, 508UL, 504UL, 500UL, 496UL, 492UL, 489UL, 485UL,
    481UL, 478UL, 474UL, 471UL, 468UL, 464UL, 461UL, 458UL,
    455UL, 451UL, 448UL, 445UL, 442UL, 439UL, 436UL, 434UL,
    431UL, 428UL, 425UL, 422UL, 420UL, 417UL, 414UL, 412UL,
    409UL, 407UL, 404UL, 402UL, 399UL, 397UL, 394UL, 392UL,
    390UL, 387UL, 385UL, 383UL, 381UL, 378UL, 376UL, 374UL,
    372UL, 370UL, 368UL, 366UL, 364UL, 362UL, 360UL, 358UL,
    356UL, 354UL, 352UL, 350UL, 348UL, 346UL, 344UL, 343UL,
    341UL, 339UL, 337UL, 336UL, 334UL, 332UL, 330UL, 329UL,
    327UL, 326UL, 324UL, 322UL, 321UL, 319UL, 318UL, 316UL,
    315UL, 313UL, 312UL, 310UL, 309UL, 307UL, 306UL, 304UL,
    303UL, 302UL, 300UL, 299UL, 297UL, 296UL, 295UL, 293UL,
    292UL, 291UL, 289UL, 288UL, 287UL, 286UL, 284UL, 283UL,
    282UL, 281UL, 280UL, 278UL, 277UL, 276UL, 275UL, 274UL,
    273UL, 271UL, 270UL, 269UL, 268UL, 267UL, 266UL, 265UL,
    264UL, 263UL, 262UL, 261UL, 260UL, 259UL, 258UL, 257UL,
    256UL, 255UL, 254UL, 253UL, 252UL, 251UL, 250UL, 249UL,
    248UL, 247UL, 246UL, 245UL, 244UL, 243UL, 242UL, 241UL,
    240UL, 240UL, 239UL, 238UL, 237UL, 236UL, 235UL, 234UL,
    234UL, 233UL, 232UL, 231UL, 230UL, 229UL, 229UL, 228UL,
    227UL, 226UL, 225UL, 225UL, 224UL, 223UL, 222UL, 222UL,
    221UL, 220UL, 219UL, 219UL, 218UL, 217UL, 217UL, 216UL,
    215UL, 214UL, 214UL, 213UL, 212UL, 212UL, 211UL, 210UL,
    210UL, 209UL, 208UL, 208UL, 207UL, 206UL, 206UL, 205UL,
    204UL, 204UL, 203UL, 202UL, 202UL, 201UL, 201UL, 200UL,
    199UL, 199UL, 198UL, 197UL, 197UL, 196UL, 196UL, 195UL,
    195UL, 194UL, 193UL, 193UL, 192UL, 192UL, 191UL, 191UL,
    190UL, 189UL, 189UL, 188UL, 188UL, 187UL, 187UL, 186UL,
    186UL, 185UL, 185UL, 184UL, 184UL, 183UL, 183UL, 182UL,
    182UL, 181UL, 181UL, 180UL, 180UL, 179UL, 179UL, 178UL,
    178UL, 177UL, 177UL, 176UL, 176UL, 175UL, 175UL, 174UL,
    174UL, 173UL, 173UL, 172UL, 172UL, 172UL, 171UL, 171UL,
    170UL, 170UL, 169UL, 169UL, 168UL, 168UL, 168UL, 167UL,
    167UL, 166UL, 166UL, 165UL, 165UL, 165UL, 164UL, 164UL,
    163UL, 163UL, 163UL, 162UL, 162UL, 161UL, 161UL, 161UL,
    160UL, 160UL, 159UL, 159UL, 159UL, 158UL, 158UL, 157UL,
    157UL, 157UL, 156UL, 156UL, 156UL, 155UL, 155UL, 154UL,
    154UL, 154UL, 153UL, 153UL, 153UL, 152UL, 152UL, 152UL,
    151UL, 151UL, 151UL, 150UL, 150UL, 149UL, 149UL, 149UL,
    148UL, 148UL, 148UL, 147UL, 147UL, 147UL, 146UL, 146UL,
    146UL, 145UL, 145UL, 145UL, 144UL, 144UL, 144UL, 144UL,
    143UL, 143UL, 143UL, 142UL, 142UL, 142UL, 141UL, 141UL,
    141UL, 140UL, 140UL, 140UL, 140UL, 139UL, 139UL, 139UL,
    138UL, 138UL, 138UL, 137UL, 137UL, 137UL, 137UL, 136UL,
    136UL, 136UL, 135UL, 135UL, 135UL, 135UL, 134UL, 134UL,
    134UL, 134UL, 133UL, 133UL, 133UL, 132UL, 132UL, 132UL,
    132UL, 131UL, 131UL, 131UL, 131UL, 130UL, 130UL, 130UL,
    130UL, 129UL, 129UL, 129UL, 129UL, 128UL, 128UL, 128UL,
    128UL
};

static unsigned long dda_get_reciprocal(unsigned int direction_magnitude)
{
    if (direction_magnitude == 0)
        return DDA_INFINITY;

    /* Clamp unexpected magnitudes to the last valid reciprocal entry. */
    if (direction_magnitude > DDA_RECIPROCAL_MAX_MAGNITUDE)
        direction_magnitude = DDA_RECIPROCAL_MAX_MAGNITUDE;

    return dda_reciprocal_by_magnitude[direction_magnitude];
}

static unsigned long dda_get_side_distance(unsigned int boundary_distance,
                                           unsigned long reciprocal)
{
    if (reciprocal == DDA_INFINITY)
        return DDA_INFINITY;

    return ((unsigned long)boundary_distance * reciprocal) >> 8;
}

static unsigned char hit_x;
static unsigned char hit_y;
static unsigned int hit_distance;
static unsigned char wall_height;
static unsigned char wall_heights[RAY_COUNT];

static unsigned char cast_ray(signed int direction_x,
                              signed int direction_y,
                              unsigned char *result_x,
                              unsigned char *result_y,
                              unsigned int *result_distance)
{
    unsigned int projected_height;
    signed int position_x = camera_get_position_x();
    signed int position_y = camera_get_position_y();
    signed int map_x = position_x / FIXED_POINT_SCALE;
    signed int map_y = position_y / FIXED_POINT_SCALE;
    signed int step_x;
    signed int step_y;
    unsigned int direction_magnitude_x;
    unsigned int direction_magnitude_y;
    unsigned long delta_distance_x;
    unsigned long delta_distance_y;
    unsigned long side_distance_x;
    unsigned long side_distance_y;
    unsigned long ray_distance;

    if (direction_x == 0)
    {
        step_x = 1;
        delta_distance_x = DDA_INFINITY;
        side_distance_x = DDA_INFINITY;
    }
    else if (direction_x < 0)
    {
        step_x = -1;
        direction_magnitude_x = (unsigned int)(-(signed long)direction_x);
        delta_distance_x = dda_get_reciprocal(direction_magnitude_x);
        side_distance_x = dda_get_side_distance(
            (unsigned int)(position_x - map_x * FIXED_POINT_SCALE),
            delta_distance_x);
    }
    else
    {
        step_x = 1;
        direction_magnitude_x = (unsigned int)direction_x;
        delta_distance_x = dda_get_reciprocal(direction_magnitude_x);
        side_distance_x = dda_get_side_distance(
            (unsigned int)((map_x + 1) * FIXED_POINT_SCALE - position_x),
            delta_distance_x);
    }

    if (direction_y == 0)
    {
        step_y = 1;
        delta_distance_y = DDA_INFINITY;
        side_distance_y = DDA_INFINITY;
    }
    else if (direction_y < 0)
    {
        step_y = -1;
        direction_magnitude_y = (unsigned int)(-(signed long)direction_y);
        delta_distance_y = dda_get_reciprocal(direction_magnitude_y);
        side_distance_y = dda_get_side_distance(
            (unsigned int)(position_y - map_y * FIXED_POINT_SCALE),
            delta_distance_y);
    }
    else
    {
        step_y = 1;
        direction_magnitude_y = (unsigned int)direction_y;
        delta_distance_y = dda_get_reciprocal(direction_magnitude_y);
        side_distance_y = dda_get_side_distance(
            (unsigned int)((map_y + 1) * FIXED_POINT_SCALE - position_y),
            delta_distance_y);
    }

    do
    {
        if (side_distance_x < side_distance_y)
        {
            ray_distance = side_distance_x;
            side_distance_x += delta_distance_x;
            map_x += step_x;
        }
        else
        {
            ray_distance = side_distance_y;
            side_distance_y += delta_distance_y;
            map_y += step_y;
        }
    }
    while (!world_is_wall((unsigned char)map_x, (unsigned char)map_y));

    *result_x = (unsigned char)map_x;
    *result_y = (unsigned char)map_y;
    *result_distance = ray_distance == 0 ? 1 : (unsigned int)ray_distance;

    projected_height = WALL_HEIGHT_SCALE / *result_distance;

    if (projected_height > GAME_GEAR_SCREEN_HEIGHT)
        projected_height = GAME_GEAR_SCREEN_HEIGHT;
    else if (projected_height == 0)
        projected_height = 1;

    return (unsigned char)projected_height;
}

void raycaster_initialize(void)
{
    unsigned char ray_index;

    hit_x = 0;
    hit_y = 0;
    hit_distance = 0;
    wall_height = 1;

    for (ray_index = 0; ray_index < RAY_COUNT; ++ray_index)
        wall_heights[ray_index] = 1;
}

void raycaster_update(void)
{
    unsigned char ray_index;
    unsigned char ray_hit_x;
    unsigned char ray_hit_y;
    unsigned int ray_hit_distance;
    signed int camera_x;
    signed int ray_direction_x;
    signed int ray_direction_y;

    wall_height = cast_ray(camera_get_direction_x(),
                           camera_get_direction_y(),
                           &hit_x, &hit_y, &hit_distance);

    for (ray_index = 0; ray_index < RAY_COUNT; ++ray_index)
    {
        camera_x = -FIXED_POINT_SCALE
                 + ((signed int)ray_index * CAMERA_PLANE_RANGE)
                 / (RAY_COUNT - 1);
        ray_direction_x = camera_get_direction_x()
                        + (signed int)(((signed long)camera_get_plane_x()
                                      * camera_x) / FIXED_POINT_SCALE);
        ray_direction_y = camera_get_direction_y()
                        + (signed int)(((signed long)camera_get_plane_y()
                                      * camera_x) / FIXED_POINT_SCALE);

        wall_heights[ray_index] = cast_ray(ray_direction_x,
                                           ray_direction_y,
                                           &ray_hit_x,
                                           &ray_hit_y,
                                           &ray_hit_distance);
    }
}

unsigned char raycaster_get_hit_x(void)
{
    return hit_x;
}

unsigned char raycaster_get_hit_y(void)
{
    return hit_y;
}

unsigned int raycaster_get_hit_distance(void)
{
    return hit_distance;
}

unsigned char raycaster_get_wall_height(void)
{
    return wall_height;
}

unsigned char raycaster_get_ray_count(void)
{
    return RAY_COUNT;
}

unsigned char raycaster_get_wall_height_for_ray(unsigned char ray_index)
{
    if (ray_index >= RAY_COUNT)
        return 0;

    return wall_heights[ray_index];
}
