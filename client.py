import socket
import os
import struct
import hashlib
import numpy as np
import cv2
import pickle

class Client(object):
  """docstring for Client."""
  def __init__(self):
    super(Client, self).__init__()
    self.buffsize = 1024
    self.compressionQuility = 60

  def imgEncode(self,img,quality):
    encode_param = [cv2.IMWRITE_JPEG_QUALITY, quality]
    result, encimg = cv2.imencode('.jpg', img, encode_param)
    return encimg

  def imgDecode(self,img):
    return cv2.imdecode(img, 1)

  def receiveFile(self, sock):
    received = 0
    chunks = []
    while received < 4:
      data = sock.recv(4 - received)
      received += len(data)
      chunks.append(data)
    # print('Received len of file size struct', len(b''.join(chunks)))
    fsize = struct.unpack('!I', b''.join(chunks))[0]
    # print('Filesize:', fsize)

    received = 0
    chunks = []
    while received < fsize:
      data = sock.recv(min(fsize - received, self.buffsize))
      received += len(data)
      chunks.append(data)
      # print( 'received ' + str(received) + ' < fsize ' + str(fsize) )
    file = b''.join(chunks)
    # print('Received file')
    # print('Expected size:', fsize)
    # print('Received size:', len(file))

    received = 0
    chunks = []
    while received < 64:
      data = sock.recv(64 - received)
      received += len(data)
      chunks.append(data)
    sha512 = b''.join(chunks)
    # print('Received Hash', len(sha512), sha512)
    hash_ok = hashlib.sha512(file).digest() == sha512
    if hash_ok:
      pass
      # print('Hash is ok')
    else:
      print('Hash is not ok')

    # print( 'size ' + str(len(file)) )

    return pickle.loads(file)

  def run(self):
    addr = ('127.0.0.1', 8080)
    sock = socket.socket()
    sock.connect(addr)
    print('Connected to', addr)

    while(True):
      file = self.receiveFile(sock)
      frame = self.imgDecode(file)
      cv2.imshow('Client',frame)
      if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    sock.close()
    cv2.destroyAllWindows()


if __name__ == '__main__':
  client = Client()
  client.run()
