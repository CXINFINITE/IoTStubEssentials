import os

class OSCommands:
   OS = None
   
   commands = dict()
   
   def start ():
      if (os.path.sep == '/'):
         OSCommands.OS = 'Linux'
         
         OSCommands.commands = {
            'clear': 'clear',
            'cd': 'cd',
            'cp': 'cp',
            'cp -r': 'cp -r',
            'rm': 'rm',
            'rm -r': 'rm -r',
            'mv': 'mv',
            'mkdir': 'mkdir',
         }
      elif (os.path.sep == '\\'):
         OSCommands.OS = 'Windows'
         
         OSCommands.commands = {
            'clear': 'cls',
            'cd': 'cd',
            'cp': 'copy',
            'cp -r': 'Xcopy /E /I',
            'rm': 'del',
            'rm -r': 'rmdir /Q /S',
            'mv': 'move',
            'mkdir': 'mkdir',
         }
         
         App.Configuration.tempDirFormat = "TEMP{0}DIR"
   
   def getCommand (command, default=False):
      if (type(command).__name__ != 'str'):
         return None
      
      if (command not in OSCommands.commands.keys()):
         return default
      else:
         return OSCommands.commands.get(command)
   
   def command (command=None, arguments=[], *args, run=True,
         quoteStr=False, addSep=False,
      ):
      if (type(command).__name__ != 'str'):
         return None
      
      command = OSCommands.getCommand(command, None)
      
      if (type(arguments).__name__ not in ('tuple', 'list')):
         arguments = [arguments]
      
      arguments.extend(args)
      
      if (not command):
         return None
      
      runnablecommand = ('{0}{1}'.format(
         command,
         ''.join([((' {0}'.format(argument)
                  if ((type(argument).__name__ in ('int', 'float'))
                        or (not quoteStr)
                     )
                  else ' "{0}{1}"'.format(
                     argument,
                     (os.path.sep
                        if (addSep)
                        else ''
                     )
                  )
               )
               if (argument != None)
               else ''
            ) for argument in arguments
         ]),
      ))
      
      if (run):
         try: result = os.system(runnablecommand)
         except: result = None
         return result
      
      return runnablecommand

OSCommands.start()
