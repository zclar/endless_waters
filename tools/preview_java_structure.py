"""Read Java NBT as data and draw a simplified isometric block preview."""
import gzip
from io import BytesIO
from pathlib import Path
import struct
from PIL import Image, ImageDraw, ImageFont


def read_structure(data):
    stream = BytesIO(gzip.decompress(data) if data[:2] == b'\x1f\x8b' else data)
    def read(fmt):
        return struct.unpack('>'+fmt, stream.read(struct.calcsize('>'+fmt)))[0]
    def text():
        return stream.read(read('H')).decode('utf8')
    def value(kind):
        if kind in [1,2,3,4,5,6]: return read({1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}[kind])
        if kind == 7: return stream.read(read('i'))
        if kind == 8: return text()
        if kind == 9:
            subtype,count = read('B'),read('i')
            return [value(subtype) for _ in range(count)]
        if kind == 10:
            result={}
            while True:
                tag=read('B')
                if not tag:return result
                key=text();result[key]=value(tag)
        if kind in [11,12]:return [read('i' if kind==11 else 'q') for _ in range(read('i'))]
        raise ValueError('Unsupported NBT tag '+str(kind))
    assert read('B')==10
    text();result=value(10)
    assert not stream.read()
    return result


def render(data, target, title):
    palette=data['palette']
    blocks={tuple(b['pos']):palette[b['state']]['Name'].removeprefix('minecraft:')
            for b in data['blocks'] if palette[b['state']]['Name'] not in
            ['minecraft:air','minecraft:cave_air','minecraft:structure_void','minecraft:water']}
    def color(name):
        if 'mangrove' in name:return (144,68,65)
        if 'wool' in name or 'sail' in name:return (211,207,188)
        if 'chest' in name:return (187,128,50)
        if 'copper' in name:return (75,132,117)
        if 'diamond' in name:return (77,177,180)
        if 'emerald' in name:return (70,151,106)
        if 'gold' in name:return (192,163,70)
        if 'ore' in name:return (130,128,124)
        if 'stone' in name:return (116,125,125)
        if 'spruce' in name or 'dark_oak' in name:return (100,73,46)
        if 'iron' in name:return (170,181,183)
        return (160,121,73)
    def project(x,y,z):return ((x-z)*.866,(x+z)*.5-y)
    corners=[project(x,y,z) for (x,y,z) in blocks for x,y,z in [(x,y,z),(x+1,y+1,z+1),(x+1,y,z),(x,y,z+1)]]
    xmin,xmax=min(c[0] for c in corners),max(c[0] for c in corners)
    ymin,ymax=min(c[1] for c in corners),max(c[1] for c in corners)
    scale=min(1000/(xmax-xmin+1),620/(ymax-ymin+1))
    image=Image.new('RGB',(1200,850),'#e9f1f3');draw=ImageDraw.Draw(image)
    def point(x,y,z):
        a,b=project(x,y,z)
        return (100+(a-xmin)*scale,100+(b-ymin)*scale)
    for (x,y,z),name in sorted(blocks.items(),key=lambda kv:(sum(kv[0]),kv[0][1])):
        c=color(name)
        faces=[((0,1,0),[(x,y+1,z),(x+1,y+1,z),(x+1,y+1,z+1),(x,y+1,z+1)],1.12),
               ((1,0,0),[(x+1,y,z),(x+1,y,z+1),(x+1,y+1,z+1),(x+1,y+1,z)],.84),
               ((0,0,1),[(x,y,z+1),(x+1,y,z+1),(x+1,y+1,z+1),(x,y+1,z+1)],.67)]
        for (dx,dy,dz),vertices,shade in faces:
            if (x+dx,y+dy,z+dz) not in blocks:
                draw.polygon([point(*v) for v in vertices],fill=tuple(min(255,int(n*shade)) for n in c),outline=(75,73,65))
    try:font=ImageFont.truetype('DejaVuSans.ttf',26)
    except OSError:font=ImageFont.load_default()
    draw.text((35,22),title,fill='#183945',font=font)
    draw.text((35,777),'Simplified blocks; no water, Minecraft textures or lighting.',fill='#294956',font=font)
    draw.text((35,812),f'Size: {data["size"]} | {len(blocks)} solid blocks',fill='#294956',font=font)
    image.save(target)
    return {'size':data['size'],'solid_blocks':len(blocks),'palette':palette}
