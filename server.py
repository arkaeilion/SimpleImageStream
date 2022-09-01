import socket
import os
import struct
import hashlib
import numpy as np
import cv2
import pickle

class Server(object):
  """docstring for Server."""
  def __init__(self):
    super(Server, self).__init__()
    self.buffsize = 1024
    self.compressionQuility = 60

  def imgEncode(self,img,quality):
    encode_param = [cv2.IMWRITE_JPEG_QUALITY, quality]
    result, encimg = cv2.imencode('.jpg', img, encode_param)
    return encimg

  def imgDecode(self,img):
    return cv2.imdecode(img, 1)

  def getChunck(self, file, i):
    s = i
    n = i + self.buffsize
    return n, file[s:n]

  def sendFile(self, file, client):
    file = pickle.dumps(file)
    fsize = struct.pack('!I', len(file))
    client.send(fsize)
    i = 0
    while True:
      i, chunk = self.getChunck(file, i)
      if not chunk:
        break
      client.send(chunk)
    i = 0
    hash = hashlib.sha512()
    while True:
      i, chunk = self.getChunck(file, i)
      if not chunk:
        break
      hash.update(chunk)
    client.send(hash.digest())

  def run(self):
    cap = cv2.VideoCapture(0)
    addr = ('', 8080)
    sock = socket.socket()
    sock.bind(addr)
    sock.listen(5)
    client, addr = sock.accept()
    print('Got connection from:', addr)

    while(True):
      ret, frame = cap.read()
      # print( 'size ' + str(len( pickle.dumps(frame) )) )
      file = self.imgEncode(frame,self.compressionQuility)
      self.sendFile(file, client)
      cv2.imshow('Server',frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    client.close()
    sock.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
  server = Server()
  server.run()
