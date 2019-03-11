import os,struct  

"""Dantarion's bb extractor code adapted to work with bbtag to an extent
    Honestly its probably the samem bug thanks to him"""

count = 0
directory = ""

total = len(os.listdir(directory))
for filename in os.listdir(directory):
  count += 1
  
  print "Extracting: %s  (%d/%d)" %(filename, count, total)
  currentFile = open(directory + filename, "rb")

  if currentFile.read(4) != 'FPAC':
    continue
  
  DATA_START,TOTAL_SIZE,FILE_COUNT = struct.unpack("<3I", currentFile.read(12))


  UNK01,STRING_SIZE,UNK03,UNK04 = struct.unpack("<4I", currentFile.read(16))
  if FILE_COUNT == 0:
    continue
  ENTRY_SIZE = (DATA_START-0x20)/FILE_COUNT

  for i in range(0,FILE_COUNT):
      currentFile.seek(0x20+i*(ENTRY_SIZE))
      FILE_NAME,FILE_ID,FILE_OFFSET,FILE_SIZE,UNK = struct.unpack("<"+str(STRING_SIZE)+"s4I",currentFile.read(0x10+STRING_SIZE))

      FILE_NAME = FILE_NAME.split("\x00")[0]
      
      
      currentFile.seek(DATA_START+FILE_OFFSET)
       
      d = currentFile.read(FILE_SIZE)
      f = open("more//" + FILE_NAME, 'wb')
      f.write(d)
      f.close()


