#!/usr/bin/env python3
"""Baca metadata LP dari super.img, baik format raw maupun Android sparse."""
import os, struct, sys

SPARSE_MAGIC = 0xED26FF3A
GEOM_MAGIC = 0x616c4467
META_MAGIC = 0x414c5030

def u16(b,o): return struct.unpack_from("<H",b,o)[0]
def u32(b,o): return struct.unpack_from("<I",b,o)[0]
def u64(b,o): return struct.unpack_from("<Q",b,o)[0]
def cstr(b):
    z=b.find(b"\x00")
    return (b[:z] if z>=0 else b).decode("utf-8","replace")

class Image:
    def __init__(self, path):
        self.f = open(path,"rb")
        head = self.f.read(40)
        if u32(head,0) == SPARSE_MAGIC:
            self.sparse = True
            self.blk = u32(head,12)
            total_blks = u32(head,16)
            self.total = total_blks * self.blk
            self.chunks = []
            file_hdr_sz = u16(head,8)
            chunk_hdr_sz = u16(head,10)
            self.f.seek(file_hdr_sz)
            out = 0
            for _ in range(u32(head,20)):
                hdr = self.f.read(chunk_hdr_sz)
                if len(hdr) < 12: break
                typ = u16(hdr,0); chunksz = u32(hdr,4); totalsz = u32(hdr,8)
                olen = chunksz * self.blk
                if typ == 0xCAC1:
                    self.chunks.append((out, self.f.tell(), olen, "raw"))
                out += olen
                self.f.seek(totalsz - chunk_hdr_sz, 1)
            print("SPARSE: block=%d total=%d (%.2f GiB) chunks=%d"
                  %(self.blk,self.total,self.total/1073741824,len(self.chunks)))
        else:
            self.sparse = False
            self.total = os.path.getsize(path)
            print("RAW image: %d bytes" % self.total)

    def read(self, off, size):
        if not self.sparse:
            self.f.seek(off); return self.f.read(size)
        buf = bytearray(size)
        end = off + size
        for out, foff, olen, typ in self.chunks:
            if out + olen <= off or out >= end: continue
            s = max(off, out) - out
            n = min(olen, end - out) - s
            self.f.seek(foff + s)
            buf[max(off,out)-off:max(off,out)-off+n] = self.f.read(n)
        return bytes(buf)

def parse(path):
    print("="*72); print("FILE:",path)
    img = Image(path)
    head = img.read(0, 1<<20)

    goff = head.find(struct.pack("<I",GEOM_MAGIC))
    if goff < 0:
        print("geometry magic tidak ketemu"); return
    gsize = u32(head,goff+4)
    o = goff+40  # magic(4) + struct_size(4) + checksum[32]
    mmsz=u32(head,o);o+=4
    slots=u32(head,o);o+=4
    lbs=u32(head,o);o+=4
    fls=u32(head,o);o+=4
    align=u32(head,o);o+=4
    aoff=u32(head,o);o+=4
    print("geometry@%d size=%d | metadata_max=%d slots=%d lbs=%d first_sector=%d align=%d"
          %(goff,gsize,mmsz,slots,lbs,fls,align))

    moff = head.find(struct.pack("<I",META_MAGIC), goff+4096)
    if moff < 0:
        print("metadata header tidak ketemu"); return
    major=u16(head,moff+4); minor=u16(head,moff+6)
    hsize=u32(head,moff+8)
    toff=moff+hsize
    print("metadata@%d v%d.%d hsize=%d tables@%d"%(moff,major,minor,hsize,toff))

    def desc(i):
        # header: magic4 + major2 + minor2 + header_size4 + header_checksum32
        #        + tables_size4 + tables_checksum32 = 80
        o=moff+80+i*12
        return u32(head,o),u32(head,o+4),u32(head,o+8)
    po,pn,ps=desc(0); eo,en,es=desc(1); go,gn,gs=desc(2); bo,bn,bs=desc(3)
    print("tables: parts=%d extents=%d groups=%d blkdevs=%d"%(pn,en,gn,bn))

    print("\n-- GROUPS --")
    groups=[]
    for i in range(gn):
        o=toff+go+i*gs
        name=cstr(head[o:o+36]); flags=u32(head,o+36); mx=u64(head,o+40)
        groups.append((name,mx))
        print("  %-32s max=%12d (%.3f GiB) flags=%d"%(name,mx,mx/1073741824,flags))

    print("\n-- BLOCK DEVICES --")
    for i in range(bn):
        o=toff+bo+i*bs
        first=u64(head,o); al=u32(head,o+8); ao=u32(head,o+12); size=u64(head,o+16)
        name=cstr(head[o+24:o+60])
        print("  %-32s size=%d (%.4f GiB) first=%d align=%d"
              %(name,size,size/1073741824,first,al))

    print("\n-- PARTITIONS --")
    total=0
    for i in range(pn):
        o=toff+po+i*ps
        name=cstr(head[o:o+36])
        # struct LpMetadataPartition (52 bytes):
        #   char name[36]; uint32 attributes; uint32 first_extent_index;
        #   uint32 num_extents; uint32 group_index;
        fe=u32(head,o+40); ne=u32(head,o+44); gi=u32(head,o+48)
        sec=0
        for j in range(ne):
            x=toff+eo+(fe+j)*es
            sec+=u64(head,x)  # num_sectors, 512-byte sectors
        sz=sec*512; total+=sz
        gname=groups[gi][0] if gi<len(groups) else str(gi)
        print("  %-28s %12d (%.3f GiB) ext=%d group=%s"%(name,sz,sz/1073741824,ne,gname))
    print("\nTOTAL logical: %d (%.4f GiB)"%(total,total/1073741824))

for p in sys.argv[1:]:
    try: parse(p)
    except Exception as e:
        print("ERROR",p,repr(e))
