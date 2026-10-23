"""Linked object-order symbol resolution, including unanchored paged constants."""
import pathlib,re
def symbols(build):
    public={m[1]:int(m[2],16) for m in re.finditer(r'^DEF (\S+) 0x([\da-fA-F]+)',(build/'GearRay.noi').read_text(),re.M)}
    result={('global',k):v for k,v in public.items()}
    # Local DATA areas concatenate in actual linker object order, ahead of libraries.
    ram=public['s__DATA']
    paged={name[2:]:value for name,value in public.items() if name.startswith('s__BANK')}
    for line in (build/'GearRay.lk').read_text().splitlines():
        p=pathlib.Path(line)
        if p.suffix!='.rel': continue
        if p.parent!=build:
            # Frozen link files retain their original absolute build paths.
            # Preserve linker order; resolve only an existing same-name local
            # object in the restored tree. External crt/library entries stay out.
            restored=build/p.name
            if not restored.is_file(): continue
            p=restored
        rel=p.read_text(); areas=[]; bases={}; current=None
        for l in rel.splitlines():
            a=re.match(r'A (\S+) size ([\dA-F]+)',l)
            if a:
                current=a[1];areas.append(current)
                if current=='_DATA':bases[current]=ram;ram+=int(a[2],16)
                elif current in paged:bases[current]=paged[current];paged[current]+=int(a[2],16)
            s=re.match(r'S (\S+) Def([\dA-F]+)',l)
            if s and current and s[1] in public:bases[current]=public[s[1]]-int(s[2],16)
        sym=p.with_suffix('.sym').read_text()
        for s in re.finditer(r'^\s*(\d+)\s+(_\w+)\s+([\dA-F]{8})\s+[GR]+\s*$',sym,re.M):
            area=areas[int(s[1])]
            if area in bases:result[(p.stem,s[2])]=bases[area]+int(s[3],16)
    for (mod,n),v in result.items():
        if mod!='global' and n in public:assert public[n]==v,(mod,n,v,public[n])
    return result
