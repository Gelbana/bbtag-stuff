import os,struct

#Array of magic numbers extracted from in-game function
chars = [0xF5, 0x5C, 0x84, 0x2A, 0xAD, 0x61, 0x54, 0xE7, 0x0A, 0xFC, 
  0x99, 0x6B, 0xD5, 0xA4, 0xD3, 0xD8, 0x48, 0x26, 0x69, 0xCB, 
  0x07, 0x42, 0x13, 0x5E, 0x10, 0x23, 0xD2, 0x6D, 0x36, 0xC7, 
  0xC1, 0x66, 0xDF, 0xA1, 0xAD, 0xF1, 0x44, 0x44, 0x7E, 0xC9, 
  0x8E, 0x24, 0x99, 0x00]


#Brute force the hell out of the encryption
def getStartingNumber(bytes):
  for i in range(0, len(chars)):
    test = bytes[:]
    for j in range(0, len(bytes)):
      result = chars[(i + j) % 43]
      test[j] ^= result
    if test == b'\x46\x50\x41\x43' or test == ' WSA' or test[:3] == 'HIP':
      return i
  return 50   


count = 0
directory = ""

#Iterate over files in directory
total = len(os.listdir(directory))
for filename in os.listdir(directory):
  count += 1
  if os.path.exists("extracted//" + filename) == True:
    print "Existing :" + filename
    continue
  if os.path.isdir(filename):
    continue

  ff = open(filename, "rb")
  currentFile = bytearray(ff.read())

  #Attempt to decrypt, most work
  bfNumber = getStartingNumber(currentFile[:4])
  if bfNumber == 50:
    print "Skipping: " + filename
    continue
  else:
    print "Extracting: %s  (%d/%d)" %(filename, count, total)
    for i in range(0, len(currentFile)):
      result = chars[bfNumber % 43]
      currentFile[i] ^= result
      bfNumber += 1

  #Save
  newName = filename
  f = open("extracted//" + newName, 'wb')
  f.write(currentFile)
  f.close()
  
ff.close()
