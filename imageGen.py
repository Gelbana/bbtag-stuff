import os,struct  
from cStringIO import StringIO
from PIL import Image, ImageDraw
from collections import OrderedDict


"""Again, adapted from Dantarion's tools' extracts hitboxes from BBTAG files.
   Takes image resources and kind of throws them together as a makeshift hitbox viewer.

   Colour offset is wrong, I'll fix it later maybe.
   """


count = 0
directory = ""

#Iterate over all file in directory
total = len(os.listdir(directory))
for filename in os.listdir(directory):
  count += 1
  framename = filename.replace(".hip",".jonbin")
  outname = filename.replace(".hip",".png")

  print "Extracting: %s  (%d/%d)" %(filename, count, total)
  currentFile = open(directory + filename, "rb")

  #Check valid file
  if currentFile.read(4) != "HIP\x00":
        continue
  
  data = struct.unpack("<3I4I4I4I", currentFile.read(0x3C))

  tmp = currentFile.tell()
  currentFile.seek(0,2)
  end = currentFile.tell()
  currentFile.seek(tmp)

  #Get colours, doesn't work (wrong offset)
  colours = []
  for i in range(0, 256):
    colours.append(struct.unpack("4B", currentFile.read(4))[::-1])

  pal = open("testColour//no00_00.hpl", "rb")
  pal.seek(0x20)
  
  for i in range(0, 256):
    tmp = struct.unpack("4B",pal.read(4))
    colours.append(list((tmp[0],tmp[1],tmp[2],tmp[3])[::-1]))

  rawData = StringIO()
  while currentFile.tell() < end:
    color = colours[struct.unpack("B", currentFile.read(1))[0]]
    counter = ord(currentFile.read(1))
    rawData.write(struct.pack("4B",*color) * counter)

  #Draw image
  img = Image.frombytes("RGBA",(data[7],data[8]),rawData.getvalue(),"raw","ARGB")

  pixel = img.load()
  width, height = img.size
  
  #Transparency, since the mish mash of resource sources have different chroma key colours 
  for y in xrange(height):
    for x in xrange(width):
      if pixel[x, y] == (0, 255, 0, 255):
        pixel[x, y] = (0, 255, 0, 0)

  #Get offset of sprite to hitbox
  currentFile.seek(0x28)
  offsetX = int(struct.unpack("<I", currentFile.read(4))[0])
  offsetY = int(struct.unpack("<I", currentFile.read(4))[0])
  
  #Get hurt/hitbox

  frames =  open("testHB//" + framename, "rb")
  base = frames.tell()
  d = OrderedDict()

  d["Images"] = []
  frames.read(4)
  imageCount, = struct.unpack("<H",frames.read(2))

  for i in range(0,imageCount):
    d["Images"].append(frames.read(32).split("\x00")[0])

  frames.read(3)
  chunkCount,hurtboxCount,hitboxCount,unkboxCount,unk2BoxCount= struct.unpack("<Ihhhh",frames.read(12))
  d["Unknown2"] = struct.unpack("<39H", frames.read(39*2))
  d["Chunks"] = []

  for i in range(0,chunkCount):
    chunk = OrderedDict()
    chunk["SrcX"],chunk["SrcY"],chunk["SrcWidth"],chunk["SrcHeight"], \
    chunk["X"],chunk["Y"],chunk["Width"],chunk["Height"] = struct.unpack("<4f4f",frames.read(4*8))
    chunk["Unknown"] = struct.unpack("<4I4I",frames.read(4*8))
    chunk["Layer"], = struct.unpack("<I",frames.read(4*1))
    chunk["Unknown2"] = struct.unpack("<3I",frames.read(3*4))
    d["Chunks"].append(chunk)
  
  d["Hurtboxes"] = []
  for i in range(0,hurtboxCount):
    box = OrderedDict()
    box["ID"],box["X"],box["Y"],box["Width"],box["Height"] = struct.unpack("<I4f",frames.read(20))
    d["Hurtboxes"].append(box)

  d["Hitboxes"] = []
  for i in range(0,hitboxCount):
    box = OrderedDict()
    box["ID"],box["X"],box["Y"],box["Width"],box["Height"] = struct.unpack("<I4f",frames.read(20))
    d["Hitboxes"].append(box)

  d["BoxType3"] = []
  for i in range(unkboxCount):
    box = OrderedDict()
    box["ID"],box["X"],box["Y"],box["Width"],box["Height"] = struct.unpack("<I4f",frames.read(20))
    d["BoxType3"].append(box)
  


  #Superimpose sprites onto canvas
  new_img_size = (int(d["Chunks"][0]["SrcWidth"]), int(d["Chunks"][0]["SrcHeight"]))
  new_im = Image.new("RGBA", new_img_size)  
  #new_im.paste(img, ((new_img_size[0]-width),
  #                    (new_img_size[1]-height)))

  #This is actually based on some flags within the file, but this crude check works most of the time
  if width > 500 or height > 500:
    img = img.resize((int(width/2), int(height/2)))
    new_im.paste(img, (offsetX/2, offsetY/2))
  else:
     new_im.paste(img, (offsetX, offsetY))
  img = new_im

  draw = ImageDraw.Draw(img)

  #Superimpose hitbox onto canvas
  for i in range(0,chunkCount):
    hb = d["Chunks"][i]
    startX =  hb["SrcX"]
    startY =   hb["SrcY"]
    endX =  hb["SrcWidth"] 
    endY =   hb["SrcHeight"] 

    draw.rectangle([startX, startY, endX, endY], outline=(0, 0, 0, 255))

  img.save("testResult//" + outname,"png")

  
  #print (chunk["SrcWidth"] + chunk["X"])
  for i in range(0,hurtboxCount):
    hb = d["Hurtboxes"][i]
    startX =  d["Chunks"][0]["SrcWidth"] + hb["X"]  - (d["Chunks"][0]["SrcWidth"] + d["Chunks"][0]["X"])
    startY =  d["Chunks"][0]["SrcHeight"]   + hb["Y"] - (d["Chunks"][0]["SrcHeight"]  + d["Chunks"][0]["Y"])
    endX =  startX + hb["Width"] 
    endY =  startY + hb["Height"] 
    draw.rectangle([startX, startY, endX, endY], outline=(0, 0, 255, 255))
  

  for i in range(0,hitboxCount):
    hb = d["Hitboxes"][i]
    startX =  d["Chunks"][0]["SrcWidth"] + hb["X"]  - (d["Chunks"][0]["SrcWidth"] + d["Chunks"][0]["X"])
    startY =  d["Chunks"][0]["SrcHeight"]   + hb["Y"] - (d["Chunks"][0]["SrcHeight"]  + d["Chunks"][0]["Y"])
    endX =  startX + hb["Width"] 
    endY =  startY + hb["Height"] 

    print  startX, startY, endX, endY
    draw.rectangle([startX, startY, endX, endY], outline=(255, 0, 0, 255))

  #Save and pray it looks okay
  img.save("testResult//" + outname,"png")
  
  
 
