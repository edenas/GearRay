"""Create isolated source trees. Production paths are read only."""
import pathlib, shutil, json
from model_experiments import rnd
ROOT=pathlib.Path(__file__).resolve().parents[4];BASE=ROOT/'build-perf-20261019'
def copytree(name):
    dst=BASE/name
    dst.mkdir(exist_ok=True)
    for d in ['game','engine','platform','tools','assets']:
        shutil.copytree(ROOT/d,dst/d,dirs_exist_ok=True)
    shutil.copyfile(ROOT/'CMakeLists.txt',dst/'CMakeLists.txt')
    return dst

# Canonical signature: remove only inputs that cannot affect wall pixels.
dst=copytree('signature-source');p=dst/'platform/game_gear/video.c';text=p.read_text()
for fn in ['game_gear_wall_column_is_unchanged','game_gear_store_wall_column_signature']:
    begin=text.index('static ',text.index(fn)-30)
    opening=text.index('{',begin)
    code='''
    /* Experiment: canonicalize the exact dependencies of visible wall output. */
    if (left_wall_height <= DISTANT_WALL_MAX_PROJECTED_HEIGHT)
    {
        left_hit_offset = 0;
        left_texture_id = 0;
        if (left_wall_height <= VERY_DISTANT_WALL_MAX_PROJECTED_HEIGHT)
            left_wall_side = WALL_SIDE_X;
    }
    else left_hit_offset >>= 5;
    if (right_wall_height <= DISTANT_WALL_MAX_PROJECTED_HEIGHT)
    {
        right_hit_offset = 0;
        right_texture_id = 0;
        if (right_wall_height <= VERY_DISTANT_WALL_MAX_PROJECTED_HEIGHT)
            right_wall_side = WALL_SIDE_X;
    }
    else right_hit_offset >>= 5;
'''
    # SDCC C dialect permits interleaved declarations in current compiler.
    text=text[:opening+1]+code+text[opening+1:]
p.write_text(text)

# Exact camera graph: all states reachable from north under both controls.
dst=copytree('camera-source')
graph=json.loads((pathlib.Path(__file__).parent/'camera-transition-graph.json').read_text())
rows=[]
for (x,y),(left,right) in zip(graph['states'],graph['edges']):
    rows.append('{'+','.join(map(str,[x,y,rnd(-y*169,256),rnd(x*169,256)]))+'}')
data='typedef struct {signed int x,y,px,py;} CameraGraphState;\nconst signed int camera_graph_vectors[][4] = {\n'+',\n'.join(rows)+'\n};\n'
data+='const unsigned char camera_graph_edges[][2] = {\n'+',\n'.join('{'+','.join(map(str,e))+'}' for e in graph['edges'])+'\n};\n'
(dst/'game/camera_graph.c').write_text(data)
p=dst/'game/camera.c';text=p.read_text();start=text.index('static signed int camera_round_rotation');end=text.index('void camera_initialize')
text=text[:start]+'''extern const signed int camera_graph_vectors[][4];
extern const unsigned char camera_graph_edges[][2];
static unsigned char camera_graph_state;
static void camera_rotate(unsigned char right)
{
    const signed int *state;
    camera_graph_state = camera_graph_edges[camera_graph_state][right];
    state = camera_graph_vectors[camera_graph_state];
    direction_x = state[0]; direction_y = state[1];
    plane_x = state[2]; plane_y = state[3];
}

'''+text[end:]
text=text.replace('    position_x = 1280;','    camera_graph_state = 0;\n    position_x = 1280;').replace('camera_rotate(-ROTATION_SINE)','camera_rotate(0)').replace('camera_rotate(ROTATION_SINE)','camera_rotate(1)')
p.write_text(text)
# Add this experimental object explicitly; no production CMake is edited.
p=dst/'CMakeLists.txt';text=p.read_text();key='add_custom_command(\n    OUTPUT "${GEAR_RAY_IHX}"'
idx=text.index(key)
text=text[:idx]+'''add_custom_command(OUTPUT "${CMAKE_BINARY_DIR}/camera_graph.rel"
    COMMAND "${GEAR_RAY_SDCC_EXECUTABLE}" -mz80 --constseg BANK2
        -c "${CMAKE_SOURCE_DIR}/game/camera_graph.c" -o "${CMAKE_BINARY_DIR}/camera_graph.rel"
    DEPENDS "${CMAKE_SOURCE_DIR}/game/camera_graph.c" VERBATIM)
'''+text[idx:]
text=text.replace('            "${GEAR_RAY_CAMERA_OBJECT}"\n','            "${GEAR_RAY_CAMERA_OBJECT}"\n            "${CMAKE_BINARY_DIR}/camera_graph.rel"\n',1)
text=text.replace('    DEPENDS "${GEAR_RAY_MAIN_OBJECT}"','    DEPENDS "${CMAKE_BINARY_DIR}/camera_graph.rel" "${GEAR_RAY_MAIN_OBJECT}"',1)
p.write_text(text)
print('Prepared signature-source and camera-source only')

# Remove the variable bitplane loop in the software sprite/HUD compositor.
dst=copytree('planes-source')
for relative in ['platform/game_gear/video.c','platform/game_gear/hud_weapon.c']:
    p=dst/relative;text=p.read_text()
    import re
    pattern=r'            for \(plane = 0; plane < 4; \+\+plane\)\s*\{.*?\n            \}'
    matches=list(re.finditer(pattern,text,re.S))
    assert len(matches)==(1 if 'video.c' in relative else 2),(relative,len(matches))
    replacement='\n'.join('''            if (palette_index & %dU)
                destination[pixel_y * 4 + %d] |= mask;
            else
                destination[pixel_y * 4 + %d] &= (unsigned char)~mask;'''%(1<<plane,plane,plane) for plane in range(4))
    text=re.sub(pattern,replacement,text,flags=re.S)
    p.write_text(text)
print('Prepared planes-source')

# Bounded 16-bit DDA accumulators; retain exact 32-bit reciprocal products.
dst=copytree('dda16-source');p=dst/'engine/render/raycaster.c';text=p.read_text()
text=text.replace('#define DDA_INFINITY 0xffffffffUL','#define DDA_INFINITY 0xffffffffUL\n#define DDA_DISTANCE_CAP 8192U')
text=text.replace('static unsigned long dda_get_side_distance','static unsigned int dda_get_side_distance')
text=text.replace('    if (reciprocal == DDA_INFINITY)\n        return DDA_INFINITY;\n\n    return ((unsigned long)boundary_distance * reciprocal) >> 8;', '''    unsigned long distance;
    if (reciprocal == DDA_INFINITY) return DDA_DISTANCE_CAP;
    distance = ((unsigned long)boundary_distance * reciprocal) >> 8;
    return distance > DDA_DISTANCE_CAP ? DDA_DISTANCE_CAP : (unsigned int)distance;''')
for field in ['delta_distance_x','delta_distance_y','side_distance_x','side_distance_y','ray_distance']:
    text=text.replace('    unsigned long '+field+';', '    unsigned int '+field+';')
text=text.replace('    unsigned int ray_distance;','    unsigned int ray_distance;\n    unsigned long reciprocal;')
for axis in ['x','y']:
    text=text.replace(f'        delta_distance_{axis} = DDA_INFINITY;',f'        delta_distance_{axis} = DDA_DISTANCE_CAP;').replace(f'        side_distance_{axis} = DDA_INFINITY;',f'        side_distance_{axis} = DDA_DISTANCE_CAP;')
    text=text.replace(f'        delta_distance_{axis} = dda_get_reciprocal(direction_magnitude_{axis});',f'''        reciprocal = dda_get_reciprocal(direction_magnitude_{axis});
        delta_distance_{axis} = reciprocal > DDA_DISTANCE_CAP
            ? DDA_DISTANCE_CAP : (unsigned int)reciprocal;''')
    text=text.replace(f'            delta_distance_{axis});','            reciprocal);')
    text=text.replace(f'            side_distance_{axis} += delta_distance_{axis};',f'''            side_distance_{axis} += delta_distance_{axis};
            if (side_distance_{axis} > DDA_DISTANCE_CAP)
                side_distance_{axis} = DDA_DISTANCE_CAP;''')
p.write_text(text)
print('Prepared dda16-source')
