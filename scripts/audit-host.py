import struct,json,pathlib
base=pathlib.Path.home()/'AppData/Local/Programs/DeepSeek Harness/resources'
archive=base/'app.asar'
out=pathlib.Path(__file__).resolve().parents[1]/'.dsh-audit'
out.mkdir(exist_ok=True)
with archive.open('rb') as f:
    _,header_size,_,json_size=struct.unpack('<4I',f.read(16))
    header=json.loads(f.read(json_size))
    entries={}
    def walk(tree,prefix=''):
        for name,item in tree.items():
            key=prefix+name
            if 'files' in item:walk(item['files'],key+'/')
            else:entries[key]=item
    walk(header['files'])
    (out/'file-list.txt').write_text('\n'.join(entries),encoding='utf8')
    for key,item in entries.items():
        selected=key in ['package.json','lib/main.js'] or (key.startswith('dsh/') and (key.endswith(('.js','.mjs','.cjs','.d.ts','.json','.yml','.yaml','.md')) and not key.endswith(('.map','.test.js'))))
        if not selected or 'link' in item or item.get('size',0)>4_000_000:continue
        dest=out/key;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():continue
        if item.get('unpacked'):
            source=base/'app.asar.unpacked'/key
            if not source.exists():continue
            content=source.read_bytes()
        else:
            f.seek(8+header_size+int(item['offset']));content=f.read(item['size'])
        dest.write_bytes(content)
    print('Desktop:',json.loads((out/'package.json').read_text())['version'])
    for p in (out/'dsh/node_modules/@deepseek-ai').glob('*/package.json'):
        meta=json.loads(p.read_text(encoding='utf8'));print(meta['name'],meta['version'])
