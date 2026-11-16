"""Explicit 9-byte actor schemas; historical results are never rewritten."""
LEGACY='legacy-pixels-v0'
VISUAL='visual-type-animation-v1'
LAYOUTS=(LEGACY,VISUAL)

def decode_actor(data,layout,pixel_names=None):
    if len(data)!=9:raise ValueError('Actor record must contain exactly nine bytes')
    if layout==LEGACY:
        pointer=int.from_bytes(data[4:6],'little')
        if pixel_names is None or pointer not in pixel_names:
            raise ValueError('Unknown historical actor pixel pointer: '+hex(pointer))
        # Keep the old state serialization for valid legacy comparisons.
        return [data[:4].hex(),pixel_names[pointer],data[6:].hex()]
    if layout==VISUAL:
        if data[4]>=2 or data[5]>=7:raise ValueError('Invalid visual type/animation token')
        return [data[:4].hex(),{'visual_type':data[4],'animation_token':data[5]},data[6:].hex()]
    raise ValueError('Explicit supported actor layout required: '+str(layout))

def fixture_identity(layout,legacy_pointer=None,visual_type=0,animation_token=0):
    if layout==LEGACY:
        if legacy_pointer is None:raise ValueError('Legacy pointer required')
        return legacy_pointer.to_bytes(2,'little')
    if layout==VISUAL:
        if not 0<=visual_type<2 or not 0<=animation_token<7:
            raise ValueError('Invalid visual fixture identity')
        return bytes([visual_type,animation_token])
    raise ValueError('Explicit supported actor layout required: '+str(layout))
