from .dbmodel import _DBModel
from .dbtable import _DBTable

import genericflaskwebapp as app

class Fields:
   class _DESCRIPTION:
      STR = 'TEXT'
      INT = 'INTEGER'
      FLOAT = 'REAL'
      
      MAIN = 'PRIMARY KEY'
      UNIQUE = 'UNIQUE'
      NOTNONE = 'NOT NULL'
      AUTOINCREMENT = 'AUTOINCREMENT'
   
   class Int:
      def __init__ (
         self, fieldname=None,
         main=False, autoincrement=False, unique=False, notnone=False,
      ):
         if (autoincrement and (not main)):
            raise ValueError(
               'database.modelenginebridges.sqlite3bridge.models:Fields.Int.'
               + '__init__:: \'autoincrement\' requires \'main\' to be set'
            )
         
         self._fieldname = str(fieldname or '')
         self._main = main
         self._autoincrement = autoincrement
         self._unique = unique
         self._notnone = notnone
      
      def _description (self, fieldname=None):
         fieldname = fieldname or self._fieldname
         
         description = {
            'fieldtype': 'int',
            'main': self._main,
            'autoincrement': self._autoincrement,
            'unique': self._unique,
            'notnone': self._notnone,
         }
         
         return (fieldname, description)
      
      def _resolve (self, fieldname=None):
         fieldname = fieldname or self._fieldname
         
         result = [
            Fields._DESCRIPTION.INT,
         ]
         
         if (self._main):
            result.append(Fields._DESCRIPTION.MAIN)
            
            if (self._autoincrement):
               result.append(Fields._DESCRIPTION.AUTOINCREMENT)
         
         if (self._unique):
            result.append(Fields._DESCRIPTION.UNIQUE)
         
         if (self._notnone):
            result.append(Fields._DESCRIPTION.NOTNONE)
         
         result = ' '.join(result)
         
         return (fieldname, result)
      
      def __str__ (self):
         return (self._resolve()[-1])
      
      def __get__ (self, instance, owner=None):
         return getattr(
            instance,
            '__Model_Fields_Int_{0}'.format(self._fieldname),
         )
      
      def __set__ (self, instance, newvalue):
         value = getattr(
            instance,
            '__Model_Fields_Int_{0}'.format(self._fieldname),
         )
         
         if (value != newvalue):
            result = instance._update(
               **{
                  self._fieldname: newvalue,
               },
            )
            
            if (result and (self._fieldname in result.keys())):
               setattr(
                  instance,
                  '__Model_Fields_Int_{0}'.format(self._fieldname),
                  result.get(self._fieldname),
               )
   
   class Float:
      def __init__ (
         self, fieldname=None,
         notnone=False,
      ):
         self._fieldname = str(fieldname or '')
         self._notnone = notnone
      
      def _description (self, fieldname=None):
         fieldname = fieldname or self._fieldname
         
         description = {
            'fieldtype': 'float',
            'notnone': self._notnone,
         }
         
         return (fieldname, description)
      
      def _resolve (self, fieldname=None):
         fieldname = fieldname or self._fieldname
         
         result = [
            Fields._DESCRIPTION.FLOAT,
         ]
         
         if (self._notnone):
            result.append(Fields._DESCRIPTION.NOTNONE)
         
         result = ' '.join(result)
         
         return (fieldname, result)
      
      def __str__ (self):
         return (self._resolve()[-1])
      
      def __get__ (self, instance, owner=None):
         return getattr(
            instance,
            '__Model_Fields_Float_{0}'.format(self._fieldname),
         )
      
      def __set__ (self, instance, newvalue):
         value = getattr(
            instance,
            '__Model_Fields_Float_{0}'.format(self._fieldname),
         )
         
         if (value != newvalue):
            result = instance._update(
               **{
                  self._fieldname: newvalue,
               },
            )
            
            if (result and (self._fieldname in result.keys())):
               setattr(
                  instance,
                  '__Model_Fields_Float_{0}'.format(self._fieldname),
                  result.get(self._fieldname),
               )
   
   class Str:
      def __init__ (
         self, fieldname=None,
         main=False, unique=False, notnone=False,
      ):
         self._fieldname = str(fieldname or '')
         self._main = main
         self._unique = unique
         self._notnone = notnone
      
      def _description (self, fieldname=None):
         fieldname = fieldname or self._fieldname
         
         description = {
            'fieldtype': 'str',
            'main': self._main,
            'unique': self._unique,
            'notnone': self._notnone,
         }
         
         return (fieldname, description)
      
      def _resolve (self, fieldname=None):
         fieldname = fieldname or self._fieldname
         
         result = [
            Fields._DESCRIPTION.STR,
         ]
         
         if (self._main):
            result.append(Fields._DESCRIPTION.MAIN)
         
         if (self._unique):
            result.append(Fields._DESCRIPTION.UNIQUE)
         
         if (self._notnone):
            result.append(Fields._DESCRIPTION.NOTNONE)
         
         result = ' '.join(result)
         
         return (fieldname, result)
      
      def __str__ (self):
         return (self._resolve()[-1])
      
      def __get__ (self, instance, owner=None):
         return getattr(
            instance,
            '__Model_Fields_Str_{0}'.format(self._fieldname),
         )
      
      def __set__ (self, instance, newvalue):
         value = getattr(
            instance,
            '__Model_Fields_Str_{0}'.format(self._fieldname),
         )
         
         if (value != newvalue):
            result = instance._update(
               **{
                  self._fieldname: newvalue,
               },
            )
            
            if (result and (self._fieldname in result.keys())):
               setattr(
                  instance,
                  '__Model_Fields_Str_{0}'.format(self._fieldname),
                  result.get(self._fieldname),
               )

class _MetaData:
   def __init__ (self, tablename, fields, fieldattributes):
      self._tablename = tablename
      self._fields = fields
      self._fieldattributes = fieldattributes

class _BaseModel (type):
   def __new__ (cls, clsname, bases, attrs, **kwargs):
      if ((
            '__database_modelenginebridges_sqlite3bridge_models_Model__'
            in attrs
         )
         and (not _DBTable._base_mainmodel_exempted)
      ):
         _DBTable._base_mainmodel_exempted = True
         attrs.pop(
            '__database_modelenginebridges_sqlite3bridge_models_Model__'
         )
         return super().__new__(cls, clsname, bases, attrs)
      
      tablename = str(clsname)
      fields = dict()
      fieldattributes = dict()
      
      mainfieldname = None
      mainfielddone = False
      
      attributes = dict()
      
      for attributename, attributevalue in attrs.items():
         if (isinstance(attributevalue, (
            Fields.Int,
            Fields.Float,
            Fields.Str,
         ))):
            attributevalue._fieldname = attributevalue._fieldname or (
               attributename
            )
            resolvedfield = attributevalue._resolve()
            
            if (resolvedfield[0] in fields):
               raise ValueError(
                  'database.modelenginebridges.sqlite3bridge.models:_BaseModel'
                  + '.__new__:: duplicate field \'{0}\' found !'.format(
                     resolvedfield[0],
                  )
               )
            
            fields[resolvedfield[0]] = resolvedfield[-1]
            
            resolvedfield = attributevalue._description()
            fieldattributes[resolvedfield[0]] = resolvedfield[-1]
            
            attributes[resolvedfield[0]] = attributevalue
            
            if (resolvedfield[-1]['main']):
               if (not mainfielddone):
                  mainfieldname = str(resolvedfield[0])
                  mainfielddone = True
               else:
                  raise Exception(
                     'database.modelenginebridges.sqlite3bridge.models:'
                     + '_BaseModel.__new__:: multiple main fields declared, '
                     + 'only one main field per model allowed '
                     + '(\'{0}\', \'{1}\')'.format(
                        mainfieldname,
                        resolvedfield[0],
                     )
                  )
         elif ((attributename == 'modelname')
            and (attributevalue and type(attributevalue).__name__ == 'str')
         ):
            tablename = attributevalue or tablename
         elif (attributename == '_metadata'):
            raise ValueError(
               'database.modelenginebridges.sqlite3bridge.models:_BaseModel'
               + '.__new__:: variable name \'_metadata\' not allowed'
            )
         else:
            if (attributename in fields):
               raise ValueError(
                  'database.modelenginebridges.sqlite3bridge.models:_BaseModel'
                  + '.__new__:: attempt to overwrite model field '
                  + '\'{0}\' !'.format(
                     attributename,
                  )
               )
            
            attributes[attributename] = attributevalue
      
      if (not mainfielddone):
         raise Exception(
            'database.modelenginebridges.sqlite3bridge.models:_BaseModel.'
            + '.__new__:: no main field declared, [only] one required'
         )
      
      if (not _DBTable._register(tablename, fields)):
         raise Exception(
            'database.modelenginebridges.sqlite3bridge.models:_BaseModel'
            + '.__new__:: error registering model \'{0}\' !'.format(
               tablename,
            )
         )
      
      attributes['_metadata'] = _MetaData(tablename, fields, fieldattributes)
      
      result = _DBModel._Table._create(
         app.database.engine,
         attributes['_metadata'],
      )
      
      if ((not result) or (result and (result[-1]))):
         raise Exception(
            'database.modelenginebridges.sqlite3bridge.models:_BaseModel'
            + '.__new__:: error creating model \'{0}\' !'.format(
               tablename,
            )
         )
      
      return super().__new__(cls, clsname, bases, attributes)

class MODE:
   NEW = 1
   EXISTING = 2

class STATE:
   INIT = 1
   READY = 2
   DELETED = 3

AGGREGATE = _DBModel._Record.AGGREGATE
SearchCondition = _DBModel._Record.SearchCondition

class Model (object, metaclass=_BaseModel):
   def __database_modelenginebridges_sqlite3bridge_models_Model__ (self):
      # This function is for tracking this model to exempt from db table
      # creation.
      # This function will be removed by metaclass once done.
      pass
   
   MODE = MODE
   STATE = STATE
   AGGREGATE = _DBModel._Record.AGGREGATE
   SearchCondition = _DBModel._Record.SearchCondition
   
   def __init__ (self, dbengine, autosave=None, mode=None, **kwargs):
      if (len(set(kwargs.keys()) - set(self._metadata._fields.keys()))):
         raise KeyError(
            'database.modelenginebridges.sqlite3bridge.models:Model'
            + '.__init__:: undeclared field(s) {0} !'.format(
               tuple(
                  set(kwargs.keys())
                  - set(self._metadata._fields.keys())
               ),
            )
         )
      
      if (mode not in (
         MODE.NEW,
         MODE.EXISTING,
      )):
         mode = MODE.NEW
      
      self._dbengine = dbengine
      self._state = STATE.INIT
      self._modified = False
      self._modifieddata = dict()
      self._modelindatabase = True
      self.autosave = False
      
      if (mode == MODE.NEW):
         self._modelindatabase = False
         self._modified = True
      
      for fieldname, fieldattribute in self._metadata._fieldattributes.items():
         setattr(
            self,
            '__Model_Fields_{0}_{1}'.format(
               str(fieldattribute.get('fieldtype')).title(),
               fieldname,
            ),
            (
               None
               if (not fieldattribute.get('notnone'))
               else (
                  int(0)
                  if (fieldattribute.get('fieldtype') == 'int')
                  else (float(0)
                     if (fieldattribute.get('fieldtype') == 'float')
                     else (
                        str('')
                        if (fieldattribute.get('fieldtype') == 'str')
                        else
                        None
                     )
                  )
               )
            ),
         )
      self.set_values(autosave=autosave, **kwargs)
      
      self.autosave = autosave
      
      if (autosave):
         self.save()
      
      self._state = STATE.READY
   
   def __del__ (self):
      try:
         if (self._state not in (
               STATE.INIT,
               STATE.DELETED,
            )
            and self.autosave
         ):
            self.save()
      except: pass
   
   def to_dict (self):
      result = dict()
      
      for key in self._metadata._fields.keys():
         if (self._modified and (key in self._modifieddata)):
            result[key] = self._modifieddata.get(key)
         else:
            result[key] = getattr(self, key)
      
      return result
   
   def __str__ (self):
      result = self.to_dict()
      
      mainfield = None
      otherfields = list()
      
      for key, value in self._metadata._fieldattributes.items():
         if (value.get('main')):
            mainfield = key
         else:
            otherfields.append(key)
      
      result = '[ {0}[{1}]: {2} ]'.format(
         mainfield,
         result.get(mainfield),
         ', '.join([
            '{0}={1}'.format(
               field,
               (("'{0}'"
                     if (self._metadata._fieldattributes.get(field).get(
                        'fieldtype'
                     ) == 'str')
                     else
                     '{0}'
                  ).format(
                     result.get(field),
               )),
            )
            for field in otherfields
         ]),
      )
      
      return result
   
   def __eq__ (self, other):
      selfdict = self.to_dict()
      otherdict = other.to_dict()
      
      result = False
      
      for field in selfdict.keys():
         if (selfdict.get(field) == otherdict.get(field)):
            result = True
         else:
            result = False
            break
      
      return result
   
   def _update (self, **kwargs):
      if (len(set(kwargs.keys()) - set(self._metadata._fields.keys()))):
         raise KeyError(
            'database.modelenginebridges.sqlite3bridge.models:Model'
            + '._update:: undeclared field(s) {0} !'.format(
               tuple(
                  set(kwargs.keys())
                  - set(self._metadata._fields.keys())
               ),
            )
         )
      
      if (not kwargs):
         raise KeyError(
            'database.modelenginebridges.sqlite3bridge.models:Model'
            + '._update:: no field-value pair received !'
         )
      
      returnargs = dict()
      
      if ((self._state in (
            STATE.INIT,
         ))
         and (self._modelindatabase)
      ):
         for key, value in kwargs.items():
            returnargs[key] = value
      elif ((self._state not in (
            STATE.INIT,
            STATE.DELETED,
         ))
         or (
            (self._state in (
               STATE.INIT,
            ))
            and (not self._modelindatabase)
         )
      ):
         for key, value in kwargs.items():
            nvalue = value
            
            try:
               nvalue = getattr(self, '_set_{0}'.format(key))(value)
            except:
               nvalue = value
            
            ovalue = getattr(self, key)
            
            # Attribute - metadata checks
            
            if ((nvalue is None)
               and (self._metadata._fieldattributes.get(key).get(
                  'notnone',
               ))
            ):
               raise ValueError(
                  'database.modelenginebridges.sqlite3bridge.models:Model'
                  + '._update:: field \'{0}\' does not allow NoneType'.format(
                     key,
                  )
               )
            
            if ((nvalue is not None)
               and (self._metadata._fieldattributes.get(key).get(
                  'fieldtype',
               ) != type(nvalue).__name__)
            ):
               raise TypeError(
                  'database.modelenginebridges.sqlite3bridge.models:Model'
                  + '._update:: field \'{0}\' requires \'{1}\', '.format(
                     key,
                     self._metadata._fieldattributes.get(key).get('fieldtype'),
                  )
                  + 'supplied \'{0}\''.format(
                     type(nvalue).__name__,
                  )
               )
            
            if ((nvalue is not None)
               and (nvalue != ovalue)
               and ((self._metadata._fieldattributes.get(key).get(
                     'main',
                  ))
                  or (self._metadata._fieldattributes.get(key).get(
                     'unique',
                  ))
               )
               and (not self._metadata._fieldattributes.get(key).get(
                  'autoincrement',
               ))
            ):
               searchresult = self.search_aggregate(
                  select=key,
                  aggregate=self.AGGREGATE.COUNT,
                  findall=False,
                  **{
                     key: nvalue,
                  },
               )
               
               if (searchresult and (searchresult[key])):
                  raise ValueError(
                     'database.modelenginebridges.sqlite3bridge.models:Model'
                     + '._update:: field \'{0}\' requires unique '.format(
                        key,
                     )
                     + 'value, supplied duplicate one !'
                  )
            
            if (ovalue != nvalue):
               if (key not in self._modifieddata):
                  self._modifieddata[key] = ovalue
               
               self._modified = True
            
            returnargs[key] = nvalue
      
      return returnargs
   
   def set_values (self, autosave=None, **kwargs):
      if (len(set(kwargs.keys()) - set(self._metadata._fields.keys()))):
         raise KeyError(
            'database.modelenginebridges.sqlite3bridge.models:Model'
            + '.set_values:: undeclared field(s) {0} !'.format(
               tuple(
                  set(kwargs.keys())
                  - set(self._metadata._fields.keys())
               ),
            )
         )
      
      if (not kwargs):
         raise KeyError(
            'database.modelenginebridges.sqlite3bridge.models:Model'
            + '.set_values:: no field-value pair received !'
         )
      
      if (autosave is None):
         autosave = self.autosave
      
      result = False
      
      oldautosave = self.autosave
      self.autosave = False
      
      try:
         for key, value in kwargs.items():
            setattr(self, key, value)
         
         result = True
      except:
         raise
      finally:
         self.autosave = oldautosave
      
      if (result and autosave):
         result = self.save()
      
      return result
   
   def save (self):
      result = False
      
      if (self._state not in (
            STATE.DELETED,
         )
         and self._modified
      ):
         newvalues = dict([
            [key, getattr(self, key)]
            for key in self._modifieddata.keys()
            if (
               not self._metadata._fieldattributes.get(key).get('autoincrement')
            )
         ])
         
         if (self._modelindatabase):
            oldvalues = dict()
            
            for key, value in self._metadata._fieldattributes.items():
               if (value.get('main')):
                  if (key in self._modifieddata):
                     oldvalues[key] = self._modifieddata.get(key)
                  else:
                     oldvalues[key] = getattr(self, key)
            
            retresult = _DBModel._Record._update(
               self._dbengine,
               self._metadata,
               searchconditions=self.SearchCondition(
                  concat=self.SearchCondition.CONCAT.AND,
                  **oldvalues,
               ),
               **newvalues,
            )
            
            if (retresult and (not retresult[-1])):
               result = True
         elif (not self._modelindatabase):
            retresult = _DBModel._Record._insert(
               self._dbengine,
               self._metadata,
               **newvalues,
            )
            
            if (retresult and (not retresult[-1])):
               result = True
               
               autoincrementfields = [
                  key
                  for key, value in self._metadata._fieldattributes.items()
                  if (value.get('autoincrement'))
               ]
               
               if (autoincrementfields):
                  fetchresult = self.search(
                     selects=autoincrementfields,
                     findall=True,
                     **dict([
                        [
                           fieldname,
                           getattr(
                              self,
                              fieldname,
                           ),
                        ]
                        for fieldname, fieldattribute  in (
                           self._metadata._fieldattributes.items()
                        )
                        if (not fieldattribute.get('autoincrement'))
                     ]),
                  )
                  
                  if (fetchresult):
                     fetchresult = fetchresult[-1]
                     
                     for key, value in fetchresult.items():
                        setattr(
                           self,
                           key,
                           value,
                        )
      
      if (result):
         self._modified = False
         self._modifieddata.clear()
         self._modelindatabase = True
         self._state = STATE.READY
      
      return result
   
   def delete (self):
      result = False
      
      if (self._state not in (
            STATE.INIT,
            STATE.DELETED,
         )
         and self._modelindatabase
      ):
         oldvalues = dict()
         
         for key, value in self._metadata._fieldattributes.items():
            if (value.get('main')):
               if (self._modified and (key in self._modifieddata)):
                  oldvalues[key] = self._modifieddata.get(key)
               else:
                  oldvalues[key] = getattr(self, key)
         
         retresult = _DBModel._Record._delete(
            self._dbengine,
            self._metadata,
            searchconditions=self.SearchCondition(
               concat=self.SearchCondition.CONCAT.AND,
               **oldvalues,
            ),
         )
         
         if (retresult and (not retresult[-1])):
            result = True
      
      if (result):
         self._modified = False
         self._modifieddata.clear()
         self._modelindatabase = False
         self._state = STATE.DELETED
      
      return result
   
   @classmethod
   def search (cls, selects=[], searchconditions=None, findall=None, **kwargs):
      if (len(set(kwargs.keys()) - set(cls._metadata._fields.keys()))):
         raise KeyError(
            'database.modelenginebridges.sqlite3bridge.models:Model'
            + '.search:: undeclared field(s) {0} !'.format(
               tuple(
                  set(kwargs.keys())
                  - set(cls._metadata._fields.keys())
               ),
            )
         )
      
      if ((not kwargs) and (not searchconditions)):
         raise KeyError(
            'database.modelenginebridges.sqlite3bridge.models:Model'
            + '.search:: no field-value pair or search-conditions received !'
         )
      
      if (len(set(selects) - set(cls._metadata._fields.keys()) - set(['*']))):
         raise KeyError(
            'database.modelenginebridges.sqlite3bridge.models:Model'
            + '.search:: undeclared field(s) {0} !'.format(
               tuple(
                  set(selects)
                  - set(cls._metadata._fields.keys())
               ),
            )
         )
      
      result = None
      
      if (not selects):
         selects = [key for key in cls._metadata._fields.keys()]
      
      if (not searchconditions):
         searchconditions = cls.SearchCondition(
            concat=cls.SearchCondition.CONCAT.AND,
            **kwargs,
         )
      
      retresult = _DBModel._Record._select(
         app.database.engine,
         cls._metadata,
         selects=selects,
         searchconditions=searchconditions,
         fetch=(app.database.engine.FETCH.ONE
            if (not findall)
            else
            app.database.engine.FETCH.ALL
         ),
      )
      
      if (retresult and (not retresult[-1])):
         result = retresult[0]
      
      return result
   
   @classmethod
   def search_aggregate (
      cls,
      select=None, aggregate=None,
      searchconditions=None, findall=None, **kwargs,
   ):
      if (len(set(kwargs.keys()) - set(cls._metadata._fields.keys()))):
         raise KeyError(
            'database.modelenginebridges.sqlite3bridge.models:Model'
            + '.search_aggregate:: undeclared field(s) {0} !'.format(
               tuple(
                  set(kwargs.keys())
                  - set(cls._metadata._fields.keys())
               ),
            )
         )
      
      if (len(set([select]) - set(cls._metadata._fields.keys()) - set(['*']))):
         raise KeyError(
            'database.modelenginebridges.sqlite3bridge.models:Model'
            + '.search_aggregate:: undeclared field {0} !'.format(
               select,
            )
         )
      
      result = None
      
      if (not select):
         select = '*'
      
      if (aggregate not in (
         cls.AGGREGATE.MAX,
         cls.AGGREGATE.MIN,
         cls.AGGREGATE.SUM,
         cls.AGGREGATE.COUNT,
         cls.AGGREGATE.UNIQUE,
         cls.AGGREGATE.AVERAGE,
      )):
         aggregate = cls.AGGREGATE.COUNT
      
      if (not searchconditions):
         searchconditions = cls.SearchCondition(
            concat=cls.SearchCondition.CONCAT.AND,
            **kwargs,
         )
      
      retresult = _DBModel._Record._aggregate(
         app.database.engine,
         cls._metadata,
         select=select,
         aggregate=aggregate,
         searchconditions=searchconditions,
         fetch=(app.database.engine.FETCH.ONE
            if (not findall)
            else
            app.database.engine.FETCH.ALL
         ),
      )
      
      if (retresult and (not retresult[-1])):
         result = retresult[0]
      
      return result
   
   @classmethod
   def find (cls, searchconditions=None, findall=None, **kwargs):
      if (len(set(kwargs.keys()) - set(cls._metadata._fields.keys()))):
         raise KeyError(
            'database.modelenginebridges.sqlite3bridge.models:Model'
            + '.find:: undeclared field(s) {0} !'.format(
               tuple(
                  set(kwargs.keys())
                  - set(cls._metadata._fields.keys())
               ),
            )
         )
      
      if ((not kwargs) and (not searchconditions)):
         raise KeyError(
            'database.modelenginebridges.sqlite3bridge.models:Model'
            + '.find:: no field-value pair or search-conditions received !'
         )
      
      result = None
      
      if (not searchconditions):
         searchconditions = cls.SearchCondition(
            concat=cls.SearchCondition.CONCAT.AND,
            **kwargs,
         )
      
      retresult = _DBModel._Record._select(
         app.database.engine,
         cls._metadata,
         selects=[key for key in cls._metadata._fields.keys()],
         searchconditions=searchconditions,
         fetch=(app.database.engine.FETCH.ONE
            if (not findall)
            else
            app.database.engine.FETCH.ALL
         ),
      )
      
      if (retresult and (not retresult[-1]) and retresult[0]):
         if (not findall):
            result = [retresult[0],]
         else:
            result = retresult[0]
         
         modelresult = list()
         
         for res in result:
            modelresult.append(cls(
               dbengine=app.database.engine,
               mode=cls.MODE.EXISTING,
               autosave=True,
               **res,
            ))
         
         if (not findall):
            result = modelresult[0]
         else:
            result = modelresult
      
      return result
