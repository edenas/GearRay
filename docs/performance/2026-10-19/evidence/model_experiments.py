"""Exact integer camera-state closure and signature dependency experiments."""
import math,json,pathlib,collections
OUT=pathlib.Path(__file__).parent
def trunc(n,d):return n//d if n>=0 else -((-n)//d)
def rnd(n,d):return trunc(n+(d//2 if n>=0 else -d//2),d)
def rotate(x,y,sign):
    nx=rnd(x*4058-y*556*sign,4096);ny=rnd(y*4058+x*556*sign,4096)
    length=math.isqrt(nx*nx+ny*ny)
    return rnd(nx*256,length),rnd(ny*256,length)
states={(0,-256):0};queue=collections.deque(states);edges=[]
while queue:
    v=queue.popleft();e=[]
    for sign in [-1,1]:
        w=rotate(*v,sign)
        if w not in states:states[w]=len(states);queue.append(w)
        e.append(states[w])
    edges.append(e)
    assert len(states)<100000
sequence=[];v=(0,-256);seen={}
while v not in seen:
    seen[v]=len(sequence);sequence.append(v);v=rotate(*v,1)
transient=seen[v];cycle=len(sequence)-transient
deltas=[]
for v in states:
    w=rotate(*v,1)
    angle=math.degrees(math.atan2(v[0]*w[1]-v[1]*w[0],v[0]*w[0]+v[1]*w[1]))
    deltas.append(angle)
result={'classification':'PROVEN integer model, pending generated-Z80 replay','reachable_direction_states':len(states),'constant_right_transient':transient,'right_cycle':cycle,'right_step_degrees_min':min(deltas),'right_step_degrees_max':max(deltas),'state_table_bytes_xy_plane':len(states)*8,'transition_table_bytes_uint16':len(states)*4,'transition_table_bytes_uint8':len(states)*2,'state_index_ram':1,'note':'A graph LUT can preserve repeated left/right history exactly. This is not a conventional uniform-angle LUT. Plane reconstructs from normalized direction with signed rounding.'}
(OUT/'camera-closure.json').write_text(json.dumps(result,indent=2))
(OUT/'camera-transition-graph.json').write_text(json.dumps({'states':list(states),'edges':edges},separators=(',',':')))
print(json.dumps(result,indent=2))
# Exact height table with small far-range branches fits Bank2 headroom.
def height(d):return max(1,min(144,16384//max(1,d)))
table=[height(d) for d in range(4097)]
errors=[]
for d in range(65536):
    h=table[d] if d<=4096 else 3 if d<=5461 else 2 if d<=8192 else 1
    if h!=height(d):errors.append(d)
(OUT/'height-lut-proof.json').write_text(json.dumps({'cases':65536,'mismatches':len(errors),'table_bytes':len(table),'table4096_entry':table[-1],'thresholds':[4096,5461,8192],'classification':'PROVEN integer domain; no runtime performance claim'},indent=2))
