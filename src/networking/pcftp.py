#!/usr/bin/env python

import os
import re
import sys
import time
import socket
import threading
import subprocess

class TransferredFile:
   def __init__ (self, filepath=None):
      if (filepath):
         if (os.path.isfile(os.path.abspath(filepath))):
            self.mode = 'upload'
            self.data = None
            try:
               fh = open(os.path.abspath(filepath), 'rb')
               self.data = fh.read()
               fh.close()
            except:
               raise Exception("Can't read file at '"+ str(filepath) + "'!")
            
            if (not self.data):
               raise ValueError("File is empty!")
            
            self.data_size = len(self.data)
            self.filepath = filepath
            self.filename = [pathsplit
               for pathsplit in re.split('[\/]', filepath)
               if (pathsplit)
            ][-1]
            
            self.ready = True
         else:
            raise ValueError("'" + str(filepath) + "' path is not a file!")
      else:
         self.mode = 'download'
         self.ready = True
   
   def transfer_file (self, connection, socketconnection):
      if (self.ready and (self.mode == 'upload')):
         try:
            socketconnection.sendall(self.data)
         except:
            raise Exception("[Upload]::Transfer error!")
         
         print("File '" + str(self.filepath) + "' uploaded successfully!")
         return True
      elif (self.ready and (self.mode == 'download')):
         time.sleep(2)
         try:
            self.data = connection.recvall(
               socketconnection,
               self.data_size,
            )
         except:
            raise Exception("[Download]::Transfer error!")
         
         filepath = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'TransferredFiles'
         )
         
         if (not os.path.isdir(filepath)):
            os.mkdir(filepath)
         
         filepath = os.path.join(filepath, self.filename)
         
         try:
            fh = open(filepath, 'wb')
            fh.write(self.data)
            fh.close()
         except:
            raise Exception("Can't write file at '" + str(filepath) + "'!")
         
         print("File '" + str(self.filename) + "' downloaded successfully, "
            "stored at '" + str(filepath) + "'"
         )
         return True
      else:
         return None
      
      return None
   
   def transfer_metadata (self, connection, socketconnection):
      if (self.ready and (self.mode == 'upload')):
         try:
            metadata = str(
               self.filename + "||$$||"
               + str(self.data_size)
            ).encode()
            
            socketconnection.sendall(metadata)
            
            time.sleep(2)
         except:
            raise Exception("[Upload]::Metadata transfer error!")
         
         return True
      elif (self.ready and (self.mode == 'download')):
         try:
            metadata = socketconnection.recv(50000)
            metadata = metadata.decode()
         except:
            raise Exception("[Download]::Metadata transfer error!")
         
         metadata = [mdata
            for mdata in re.split('[|][|][$][$][|][|]', metadata)
            if (mdata)
         ]
         self.filename = metadata[0]
         self.data_size = int(metadata[1])
         
         return True
      else:
         return None
      
      return None

class Connection:
   def __init__ (self,
      mode='client', ip_addr='0.0.0.0', port=22002, waitcon=1
   ):
      if (not port):
         port = 22002
      
      if ((port > 1000) and (port < 36215)):
         self.serverport = int(port)
      else:
         self.serverport = 22002
      
      if (mode == 'client'):
         self.mode = 'client'
         self.serverip = str(ip_addr)
      elif (mode == 'server'):
         self.mode = 'server'
         self.serverip = '0.0.0.0'
         if ((waitcon > 0) and (waitcon < 20)):
            self.waitconnections = int(waitcon)
         else:
            self.waitconnections = 1
      else:
         raise Exception("Can't determine connection mode!")
      
      try:
         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      except:
         raise Exception("[Client]::Socket error!")
      
      if (mode == 'server'):
         self.socket.bind((self.serverip, self.serverport))
         self.socket.listen(self.waitconnections)
      
      self.ready = True
      self.connected = False
   
   def get_ipdetails (self, printipdetails=False):
      result = ''
      command = ''
      cmode = 0
      
      if (os.path.sep == '/'):
         command = 'ifconfig'
         cmode = 0
      else:
         command = 'ipconfig'
         cmode = 1
      
      if (printipdetails):
         try:
            os.system(command)
         except:
            pass
         
         print("Server IP can also be found by '"
            + str(command)
            + "' results shown above."
         )
      
      cresults = None
      
      try:
         proc = subprocess.Popen(command,
            stdout=subprocess.PIPE,
         )
         cresults, _ = proc.communicate()
         cresults = str(cresults.decode())
      except:
         pass
      
      if (cresults):
         if (cmode == 0):
            cresults = [cpara
               for cpara in re.split('[\n][ ]*[\n]', cresults)
               if (cpara)
            ]
            
            for cresult in cresults:
               if (
                  ('UP' in cresult)
                  and ('BROADCAST' in cresult)
                  and ('RUNNING' in cresult)
                  and ('MULTICAST' in cresult)
               ):
                  ipaddr = re.findall(
                     '[i][n][e][t][^0-9]+([0-9][0-9.]+)[^0-9.]*',
                     cresult
                  )
                  
                  if (len(ipaddr) > 0):
                     result = str(ipaddr[0])
         elif (cmode == 1):
            ipaddr = re.findall((
               '[iI][pP][vV][4][ ][aA][dD][dD][rR][eE][sS][sS][^0-9]*'
               + '([0-9][0-9.]+)[^0-9.]*'
            ), cresult)
            
            if (len(ipaddr) > 0):
               result = str(ipaddr[0])
      
      return result
   
   def connect (self):
      if ((not self.ready) or (self.connected)):
         return None
      
      try:
         if (self.mode == 'client'):
            self.socket.connect((self.serverip, self.serverport))
            self.connected = True
            return True
         elif (self.mode == 'server'):
            self.clientsocketconnection, self.clientaddress = (
               self.socket.accept()
            )
            self.connected = True
            return True
         else:
            return None
      except:
         raise Exception("[Connect]::Socket connection error!")
         return None
      
      return None
   
   def disconnect (self):
      if ((not self.ready) or (not self.connected)):
         return None
      
      try:
         self.connected = False
         self.ready = False
         if (self.mode == 'client'):
            try:
               self.socket.shutdown(socket.SHUT_RDWR)
            except: pass
            
            try:
               self.socket.close()
            except: pass
            
            return True
         elif (self.mode == 'server'):
            try:
               self.clientsocketconnection.shutdown(socket.SHUT_RDWR)
            except: pass
            
            try:
               self.clientsocketconnection.close()
            except: pass
            
            return True
         
         return None
      except:
         raise Exception("[Disconnect]::Socket disconnection error!")
         return None
      
      return None
   
   def get_socketconnection (self):
      if (self.ready and self.connected):
         if (self.mode == 'client'):
            return self.socket
         elif (self.mode == 'server'):
            return self.clientsocketconnection
         
         return None
      else:
         return None
      
      return None
   
   def recvall (self, socketconnection, size=30000):
      data = ''.encode()
      
      socketconnection.settimeout(0.8)
      retries = 4
      
      while True:
         breakme = False
         localdata = None
         
         try:
            localdata = socketconnection.recv(50000)
         except:
            retries -= 1
            if (retries < 1):
               breakme = True
         
         if (localdata):
            data = (''.encode()).join([data, localdata])
         
         if (((not localdata) or (localdata and (len(localdata) < 4)))
            and (len(data) > 1)
         ):
            breakme = True
         
         if (breakme):
            break
      
      socketconnection.settimeout(None)
      
      return data

class SelfShare:
   def __init__ (self, connection, socketconnection):
      self.connection = connection
      self.socketconnection = socketconnection
      
      filepath = os.path.abspath(__file__)
      
      self.data = None
      try:
         fh = open(os.path.abspath(filepath), 'rb')
         self.data = fh.read()
         fh.close()
      except:
         raise Exception("Can't read (self) file at '"+ str(filepath) + "'!")
      
      if (not self.data):
         raise ValueError("File is empty!")
      
      self.data_size = len(self.data)
      
      requestdata = None
      
      try:
         requestdata = self.socketconnection.recv(50000)
         requestdata = requestdata.decode()
      except:
         raise Exception("[SelfShare]: Communication Error !")
      
      if (requestdata and requestdata[:3] == 'GET'):
         self.transfer()
   
   def transfer (self):
      response = (
         'HTTP/1.1 200 OK\r\n'
         + 'Content-Length: ' + str(self.data_size) + '\r\n'
         + 'Content-Type: application/x-download\r\n'
         + 'Content-Disposition: attachment; filename="pcftp.py"\r\n'
         + '\r\n'
      )
      
      response = response.encode()
      rawresponse = (''.encode()).join([response, self.data])
      
      try:
         self.socketconnection.sendall(rawresponse)
      except:
         raise Exception("[SelfShare]: Transfer error!")
      
      print('Self Share successful !')
      return True

class QuickChat:
   def __init__ (self, connection, socketconnection):
      self.connection = connection
      self.socketconnection = socketconnection
      self.endchat = False
      
      self.recvthread = threading.Thread(
         target=self.recvremotechatstr,
      )
      
      try:
         self.recvthread.setDaemon(1)
      except:
         pass
      
      print(
         "\n\nQuick Chat\n----------\n"
         + "[Enter '$help' in chat to print help text.]\n"
         + "[Enter '$quit' in chat to quit / exit from chat.]\n"
      )
      
      self.recvthread.start()
      
      while (not self.endchat):
         try:
            userinput = str(raw_input('I>> '))
         except:
            try:
               userinput = str(input('I>> '))
            except:
               self.quitchat(True)
         
         self.processchatstr(userinput, False)
      
      try:
         self.recvthread.join(2)
      except:
         pass
   
   def recvremotechatstr (self):
      while (not self.endchat):
         chatstring = self.connection.recvall(self.socketconnection)
         
         if (chatstring):
            chatstring = chatstring.decode()
            self.processchatstr(chatstring, True)
      
      return None
   
   def quitchat (self, closedbyself=False):
      self.endchat = True
      
      if (closedbyself):
         try:
            self.socketconnection.sendall('$QUIT'.encode())
         except:
            pass
         
         print('\nQuick chat terminated !\nExiting ...')
      else:
         print('\nQuick chat terminated by remote !\nPress [Enter] to quit !')
   
   def printchat (self, chatstring, isremote=False):
      if (isremote):
         indicator = '\n(Remote) >: '
      else:
         indicator = '  (Self) #: '
      
      print(indicator + str(chatstring))
   
   def processchatstr (self, chatstring, isremote=False):
      chatstring = str(chatstring).strip()
      
      if ((not chatstring) or (chatstring and (len(chatstring) < 1))):
         return None
      
      if (not isremote):
         if (chatstring[0] == '$'):
            if (str(chatstring[1:5]).lower() in ['quit', 'exit']):
               self.quitchat(True)
               return True
            elif (str(chatstring[1:5]).lower() == 'help'):
               self.chathelp()
               return True
            else:
               try:
                  os.system(chatstring[1:])
                  return True
               except:
                  pass
            
            return None
         else:
            self.socketconnection.sendall(chatstring.encode())
      else:
         if (chatstring[0] == '$'):
            if (str(chatstring[1:5]).lower() == 'quit'):
               self.quitchat(False)
               return True
      
      self.printchat(chatstring, isremote)
      return True
   
   def chathelp (self):
      print(
         "\n----------------------------------------------------------------\n"
         + "             Quick Chat Help\n\n"
         + "DESCRIPTION\n"
         + "       This quick chat is for quickly communicating\n"
         + "       between two parties.\n\n"
         + "USAGE\n"
         + "       Type your message in message prompt (>>>)\n"
         + "       to send message to remote user.\n\n"
         + "WORKING\n"
         + "       Messages received through message prompts are\n"
         + "       passed to a special message processor / parser\n"
         + "       before being sent.\n"
         + "       The special parser distinguishes between a\n"
         + "       normal message (to be sent) and a special\n"
         + "       message (to be used as a command).\n"
         + "       \n"
         + "       Special messages (or commands) begin with a '$'\n"
         + "       sign as a first character, followed by <command>\n"
         + "       as '$ <command>'.\n"
         + "       example: '$ ls' or '$ dir'.\n\n"
         + "COMMANDS\n"
         + "     help\n"
         + "          Prints (this) help text.\n\n"
         + "     quit\n"
         + "          Terminates the chat for both parties.\n\n"
         + "     <command>\n"
         + "          Executes the command '<command>' in terminal\n"
         + "          (or cmd) and continues back with quick chat.\n\n"
         + "----------------------------------------------------------------\n"
      )

class TransferUI:
   def __init__ (self):
      self.autorun()
      
      sys.exit(0)
      return None
   
   def help (self):
      print(
         "\n----------------------------------------------------------------\n"
         + "       Private Communication and File Transfer Program\n\n"
         + "NAME\n"
         + "       pcftp - Private Communication and File Transfer Program\n\n"
         + "DESCRIPTION\n"
         + "       This program facilitates a single file sharing\n"
         + "       between two connected devices and also allows a\n"
         + "       two-way (full duplex) real-time chat communication.\n"
         + "       Only one mode can be activated at a time.\n\n"
         + "USAGE\n"
         + "       PROGRAM [OPTIONS]\n"
         + "       PROGRAM CONNECTIONMODE TRANSFERMODE\n\n"
         + "OPTIONS\n"
         + "     -h, --help\n"
         + "          Prints (this) help text and exits.\n\n"
         + "     -V, --version\n"
         + "          Prints version and exits.\n\n"
         + "CONNECTIONMODE\n"
         + "     -c IP[:PORT]\n"
         + "     --client IP[:PORT]\n"
         + "          Connects as a client to an established server\n"
         + "          using the IP (and PORT [if supplied]).\n\n"
         + "     -s [PORT]\n"
         + "     --server [PORT]\n"
         + "          Starts a server on the PORT (if supplied, else uses\n"
         + "          a default port) and waits for client's connection.\n\n"
         + "TRANSFERMODE\n"
         + "     -qc, --chat, --quick-chat\n"
         + "          Starts a two-way, full duplex chat communication.\n\n"
         + "     -ss, --self-share\n"
         + "          Starts a self sharing server to share this\n"
         + "          program with another device using http request.\n"
         + "          Successful share (upload) does not guarantee a\n"
         + "          successful download.\n\n"
         + "     -d, --download\n"
         + "          Starts downloading one file being uploaded by the\n"
         + "          uploader from the other end.\n"
         + "          The downloaded file is stored in a directory\n"
         + "          named 'TransferredFiles', located in same directory\n"
         + "          as this program.\n\n"
         + "     -u FILE\n"
         + "     --upload FILE\n"
         + "          Starts uploading one file to the connected party.\n"
         + "          If not connected, it waits till the connection\n"
         + "          establishes. Upon being connected, it starts\n"
         + "          upload irrespective of the state of receiver.\n"
         + "          Successful upload does not guarantee a successful\n"
         + "          download.\n\n"
         + "COMPATIBILITY\n"
         + "          Works on Python v2.4.3 +\n"
         + "          Tested for:\n"
         + "                * Python v2.4.3\n"
         + "                * Python v2.7.0\n"
         + "                * Python v3.7.4\n"
         + "                * Python v3.10.4\n"
         + "          \n"
         + "          Cross platform compatible.\n"
         + "          Tested on:\n"
         + "                * Ubuntu 16.04, 18.04, 20.04, 22.04\n"
         + "                * CentOS 5.4\n"
         + "                * Windows 7, 10, 11\n\n"
         + "AUTHOR\n"
         + "          CXINFINITE\n"
         + "          GitHub: https://github.com/CXINFINITE/\n"
         + "          File (Repo) link: https://github.com/CXINFINITE/ProjectEssentials-Python/blob/main/src/networking/pcftp.py\n\n"
         + "EXTRAS\n"
         + "          This program is made for devices in restricted\n"
         + "          environments and for running on outdated machines.\n"
         + "          Hence, this program has limited capabilities and\n"
         + "          features and so, it might not receive updates.\n\n"
         + "Designed and Developed by CXINFINITE !\n\n"
         + "----------------------------------------------------------------\n"
      )
   
   def printversion (self):
      print("Private Communication and File Transfer Program v0.0.0-dev")
      sys.exit(0)
   
   def usagehelp (self, invalid=False, error_str=None):
      if (invalid):
         print("Invalid run: '" + str(' '.join(sys.argv)) + "'")
      
      if (error_str):
         print("ERROR: '" + str(error_str) + "'")
      
      print(
         "\nPrivate Communication and File Transfer Program\n\n"
         + "Usage: run '" + str(sys.argv[0]) + " -h' for help.\n"
      )
      
      sys.exit(0)
   
   def starttransfer (
      self, connectionmode=None, transfermode=None, ip_port=None,
      filepath=None
   ):
      ipaddr = None
      port = None
      
      if (connectionmode == 'client'):
         if (ip_port):
            ip_port = [ipport
               for ipport in re.split(':', ip_port)
               if (ipport or len(ipport))
            ]
            
            ipaddr = str(ip_port[0])
            
            if (len(ip_port) > 1):
               try:
                  port = int(ip_port[1])
               except:
                  self.usagehelp(invalid=True, error_str='Invalid IP[:PORT]!')
      elif (connectionmode == 'server'):
         if (ip_port):
            try:
               port = int(ip_port)
            except:
               self.usagehelp(invalid=True, error_str='Invalid [PORT]!')
      
      if (transfermode != 'quickchat'):
         transferredfile = TransferredFile(
            filepath=filepath
         )
         
         if (not transferredfile):
            self.usagehelp(invalid=True)
      
      connection = Connection(
         mode=connectionmode,
         ip_addr=ipaddr,
         port=port,
      )
      
      if (not connection):
         self.usagehelp(invalid=True)
      
      if (transfermode == 'selfshare'):
         print(
            "Self Share server created !\n"
            + "Type 'http://"
            + str(connection.get_ipdetails(True)) + ":"
            + str(connection.serverport)
            + "/' (http://ip:port/)\n"
            + "in browser address bar (as URL) to start download !\n"
            + "(IP is ip address of this server (machine))\n"
         )
      else:
         if (connectionmode == 'server'):
            print("Server IP address: "
               + str(connection.get_ipdetails(True))
               + "; Port: "
               + str(connection.serverport)
            )
            print('Waiting for connection ...')
         else:
            print("Connecting ...")
      
      if (not connection.connect()):
         self.usagehelp(invalid=True)
      
      print("Connected")
      
      socketconnection = connection.get_socketconnection()
      
      if (not socketconnection):
         connection.disconnect()
         self.usagehelp(invalid=True)
      
      if (transfermode in ['download', 'upload']):
         print("Transferring metadata ...")
         
         if (not transferredfile.transfer_metadata(
               connection, socketconnection
            )):
            connection.disconnect()
            self.usagehelp(invalid=True)
         
         print("Metadata transferred !")
         print("Transferring file ...")
         
         if (not transferredfile.transfer_file(connection, socketconnection)):
            connection.disconnect()
            self.usagehelp(invalid=True)
      elif (transfermode == 'quickchat'):
         print('Starting quick chat ...')
         QuickChat(connection, socketconnection)
      elif (transfermode == 'selfshare'):
         print('Self Sharing ...')
         SelfShare(connection, socketconnection)
      
      connection.disconnect()
      
      sys.exit(0)
   
   def autorun (self, commands=sys.argv[1:]):
      if (len(commands) < 1):
         self.usagehelp()
      else:
         availableCommands = [
            '-c', '--client',
            '-s', '--server',
            '-ss', '--self-share',
            '-qc', '--chat', '--quick-chat',
            '-d', '--download',
            '-u', '--upload',
         ]
         if (
            ('-h' in commands)
            or ('--help' in commands)
         ):
            self.help()
         elif (
            ('-V' in commands)
            or ('--version' in commands)
         ):
            self.printversion()
         else:
            commandslength = len(commands) - 1
            connectionmode = None
            transfermode = None
            ip_port = None
            filepath = None
            
            for index, command in enumerate(commands):
               if (command in ['-c', '--client']):
                  if (connectionmode):
                     self.usagehelp(
                        invalid=True,
                        error_str='Multiple connection modes specified!'
                     )
                  
                  connectionmode = 'client'
                  
                  if (index < commandslength):
                     if (commands[(index + 1)] not in availableCommands):
                        ip_port = commands[(index + 1)]
                     else:
                        self.usagehelp(
                           invalid=True,
                           error_str='IP[:PORT] not specified!'
                        )
                  else:
                     self.usagehelp(
                        invalid=True,
                        error_str='IP[:PORT] not specified!'
                     )
               elif (command in ['-s', '--server']):
                  if (connectionmode):
                     self.usagehelp(
                        invalid=True,
                        error_str='Multiple connection modes specified!'
                     )
                  
                  connectionmode = 'server'
                  
                  if (index < commandslength):
                     if (commands[(index + 1)] not in availableCommands):
                        ip_port = commands[(index + 1)]
               elif (command in ['-u', '--upload']):
                  if (transfermode):
                     self.usagehelp(
                        invalid=True,
                        error_str='Multiple transfer modes specified!'
                     )
                  
                  transfermode = 'upload'
                  
                  if (index < commandslength):
                     if (commands[(index + 1)] not in availableCommands):
                        filepath = commands[(index + 1)]
                        
                        if (not os.path.isfile(os.path.abspath(filepath))):
                           self.usagehelp(invalid=True, error_str=(
                              "FILE '" + str(filepath)
                              + "' does not exists / is not readable!"
                           ))
                     else:
                        self.usagehelp(
                           invalid=True,
                           error_str='FILE not specified!'
                        )
                  else:
                     self.usagehelp(
                        invalid=True,
                        error_str='FILE not specified!'
                     )
               elif (command in ['-d', '--download']):
                  if (transfermode):
                     self.usagehelp(
                        invalid=True,
                        error_str='Multiple transfer modes specified!'
                     )
                  
                  transfermode = 'download'
               elif (command in ['-qc', '--chat', '--quick-chat']):
                  if (transfermode):
                     self.usagehelp(
                        invalid=True,
                        error_str='Multiple transfer modes specified!'
                     )
                  
                  transfermode = 'quickchat'
               elif (command in ['-ss', '--self-share']):
                  if (transfermode):
                     self.usagehelp(
                        invalid=True,
                        error_str='Multiple transfer modes specified!'
                     )
                  
                  transfermode = 'selfshare'
            
            if (connectionmode and transfermode): pass
            else:
               self.usagehelp(invalid=True)
            
            if ((transfermode == 'selfshare')
               and (connectionmode != 'server')
            ):
               self.usagehelp(
                  invalid=True,
                  error_str="Self share works only in 'server' mode!"
               )
            
            self.starttransfer(
               connectionmode=connectionmode,
               transfermode=transfermode,
               ip_port=ip_port,
               filepath=filepath,
            )
            
            self.usagehelp(invalid=True)

if (__name__ == '__main__'):
   TransferUI()
