class _DBModel:
   class _Table:
      def _create (dbengine, metadata):
         return dbengine.execute_raw(
            (
               'CREATE TABLE IF NOT EXISTS {0} ('.format(metadata._tablename)
               + ', '.join(['{0} {1}'.format(
                     attribute, declaration,
                  )
                  for attribute, declaration in metadata._fields.items()
               ])
               + ');'
            ),
            commit=True,
            errorstatus=True,
         )
      
      def _drop (dbengine, metadata):
         return dbengine.execute_raw(
            (
               'DROP TABLE {0};'.format(metadata._tablename)
            ),
            commit=True,
            errorstatus=True,
         )
   
   class _Record:
      class AGGREGATE:
         MAX = 'MAX'
         MIN = 'MIN'
         SUM = 'SUM'
         COUNT = 'COUNT'
         UNIQUE = 'UNIQUE'
         AVERAGE = 'AVERAGE'
      
      class SearchCondition:
         class CONCAT:
            NORMAL = ', '
            AND = ' AND '
            OR = ' OR '
         
         def __init__ (
            self, *searchconditions, metadata=None, concat=None, **conditions,
         ):
            if (concat not in (
               _DBModel._Record.SearchCondition.CONCAT.NORMAL,
               _DBModel._Record.SearchCondition.CONCAT.AND,
               _DBModel._Record.SearchCondition.CONCAT.OR,
            )):
               concat = _DBModel._Record.SearchCondition.CONCAT.NORMAL
            
            self.concat = concat
            
            if (not (len(searchconditions) or len(conditions))):
               return None
               # raise error
            
            self.metadata = metadata
            self.searchconditions = list()
            
            for searchcondition in searchconditions:
               if (isinstance(
                  searchcondition,
                  _DBModel._Record.SearchCondition,
               )):
                  self.searchconditions.append(searchcondition)
               else:
                  return None
                  # raise error
            
            self.searchconditions = searchconditions
            conditionslist = conditions.keys()
            
            self.conditions = dict([[condition, conditions[condition]]
               for condition in conditionslist
            ])
         
         def _resolve (self, metadata=None):
            metadata = metadata or self.metadata
            queries = list()
            parameters = list()
            
            for searchcondition in self.searchconditions:
               searchconditionresult = searchcondition._resolve(model=model)
               queries.append('({0})'.format(searchconditionresult[0]))
               parameters.extend(searchconditionresult[-1])
            
            if (metadata):
               if (len(
                  set(self.conditions.keys())
                  - set(metadata._fields.keys())
               )):
                  raise KeyError(
                     'database.modelenginebridges.sqlite3bridge:_DBModel:: '
                     + 'undeclared condition name(s) supplied {0}'.format(
                        tuple(
                           set(self.conditions.keys())
                           - set(metadata._fields.keys())
                        ),
                     )
                  )
            
            for key, value in self.conditions.items():
               queries.append('{0} = ?'.format(key))
               parameters.append(value)
            
            queries = (self.concat).join(queries)
            
            return (queries, parameters)
         
         def __str__ (self):
            resolved = self._resolve()
            
            result = '{0}'.format(resolved[0])
            
            for parameter in resolved[1]:
               parameter = ('"{0}"'.format(parameter)
                  if (type(parameter).__name__ == 'str')
                  else
                  '{0}'.format(parameter)
               )
               
               result = result.replace('?', parameter, 1)
            
            return result
      
      def _insert (dbengine, metadata, **kwargs):
         if (len(set(kwargs.keys()) - set(metadata._fields.keys()))):
            return None
            # raise error
         
         if (not len(kwargs.keys())):
            return None
            # raise error
         
         attributelist = kwargs.keys()
         
         return dbengine.execute_raw(
            (
               'INSERT INTO {0} ('.format(metadata._tablename)
               + ', '.join(['{0}'.format(attributename)
                  for attributename in attributelist
               ])
               + ') VALUES ('
               + ', '.join(['?'
                  for attributename in attributelist
               ])
               + ');'
            ),
            *(
               [[kwargs[attributename]
                  for attributename in attributelist
               ]]
               if (kwargs.values())
               else
               []
            ),
            commit=True,
            errorstatus=True,
         )
      
      def _update (dbengine, metadata, searchconditions=None, **kwargs):
         if (len(set(kwargs.keys()) - set(metadata._fields.keys()))):
            return None
            # raise error
         
         if (not (len(kwargs.keys()))):
            return None
            # raise error
         
         if (
            (searchconditions is not None)
            and (not isinstance(
               searchconditions,
               _DBModel._Record.SearchCondition,
            ))
         ):
            return None
            # raise error
         
         resolvedsearchconditions = (
            searchconditions._resolve(metadata=metadata)
            if (searchconditions)
            else
            [None, [],]
         )
         
         attributelist = kwargs.keys()
         
         return dbengine.execute_raw(
            (
               'UPDATE {0} SET '.format(metadata._tablename)
               + ', '.join(['{0} = ?'.format(attributename)
                  for attributename in attributelist
               ])
               + (' WHERE ({0})'.format(resolvedsearchconditions[0])
                  if (resolvedsearchconditions[0])
                  else ''
               )
               + ';'
            ),
            *(
               [[kwargs[attributename]
                     for attributename in attributelist
                  ]
                  + resolvedsearchconditions[-1]
               ]
               if (kwargs.values() or resolvedsearchconditions[-1])
               else
               []
            ),
            commit=True,
            errorstatus=True,
         )
      
      def _select (
         dbengine, metadata,
         selects=[], searchconditions=None, fetch=None, **kwargs,
      ):
         if (len(set(selects) - set(metadata._fields.keys()) - set(['*',]))):
            return None
            # raise error
         
         if (not len(selects)):
            return None
            # raise error
         
         if (('*' in selects) and (len(selects) > 1)):
            return None
            # raise error
         
         if (
            (searchconditions is not None)
            and (not isinstance(
               searchconditions,
               _DBModel._Record.SearchCondition,
            ))
         ):
            return None
            # raise error
         
         if (fetch not in (
            dbengine.FETCH.RAW,
            dbengine.FETCH.ONE,
            dbengine.FETCH.ALL,
         )):
            fetch = dbengine.FETCH.RAW
         
         resolvedsearchconditions = (
            searchconditions._resolve(metadata=metadata)
            if (searchconditions)
            else
            [None, [],]
         )
         
         attributelist = kwargs.keys()
         
         result, error = dbengine.execute_raw(
            (
               'SELECT '
               + ', '.join(['{0}'.format(selectattribute)
                  for selectattribute in selects
                  if (selectattribute)
               ])
               + ' FROM {0}'.format(metadata._tablename)
               + (' WHERE ({0})'.format(resolvedsearchconditions[0])
                  if (resolvedsearchconditions[0])
                  else ''
               )
               + ';'
            ),
            *(
               [resolvedsearchconditions[-1]]
               if (resolvedsearchconditions[-1])
               else
               []
            ),
            fetch=fetch,
            commit=False,
            errorstatus=True,
         )
         
         if (
            (fetch != dbengine.FETCH.RAW)
            and result
            and ('*' not in selects)
         ):
            if (fetch != dbengine.FETCH.ALL):
               result = [result,]
            
            fresult = list()
            
            for iresult in result:
               sresult = dict()
               
               attributeindex = -1
               
               for attributename in selects:
                  if (not attributename):
                     continue
                  
                  attributeindex += 1
                  
                  try:
                     sresult[attributename] = iresult[attributeindex]
                  except:
                     sresult[attributename] = None
               
               fresult.append(sresult)
            
            result = fresult
            
            if (fetch != dbengine.FETCH.ALL):
               result = result[0]
         
         return (result, error)
      
      def _aggregate (
         dbengine, metadata,
         select, aggregate=None, searchconditions=None, fetch=None,
      ):
         if (len(set([select]) - set(metadata._fields.keys()) - set(['*',]))):
            return None
            # raise error
         
         if (not select):
            return None
            # raise error
         
         if (
            (searchconditions is not None)
            and (not isinstance(
               searchconditions,
               _DBModel._Record.SearchCondition,
            ))
         ):
            return None
            # raise error
         
         if (aggregate not in (
            _DBModel._Record.AGGREGATE.MAX,
            _DBModel._Record.AGGREGATE.MIN,
            _DBModel._Record.AGGREGATE.SUM,
            _DBModel._Record.AGGREGATE.COUNT,
            _DBModel._Record.AGGREGATE.UNIQUE,
            _DBModel._Record.AGGREGATE.AVERAGE,
         )):
            return None
            # raise error
         
         if (fetch not in (
            dbengine.FETCH.RAW,
            dbengine.FETCH.ONE,
            dbengine.FETCH.ALL,
         )):
            fetch = dbengine.FETCH.RAW
         
         resolvedsearchconditions = (
            searchconditions._resolve(metadata=metadata)
            if (searchconditions)
            else
            [None, [],]
         )
         
         result, error = dbengine.execute_raw(
            (
               'SELECT {0}({1})'.format(aggregate, select)
               + ' FROM {0}'.format(metadata._tablename)
               + (' WHERE ({0})'.format(resolvedsearchconditions[0])
                  if (resolvedsearchconditions[0])
                  else ''
               )
               + ';'
            ),
            *(
               [resolvedsearchconditions[-1]]
               if (resolvedsearchconditions[-1])
               else
               []
            ),
            fetch=fetch,
            commit=False,
            errorstatus=True,
         )
         
         if (
            (fetch != dbengine.FETCH.RAW)
            and result
            and (select != '*')
         ):
            if (fetch != dbengine.FETCH.ALL):
               result = [result,]
            
            fresult = list()
            
            for iresult in result:
               fresult.append(dict([[select, iresult[0]]]))
            
            result = fresult
            
            if (fetch != dbengine.FETCH.ALL):
               result = result[0]
         
         return (result, error)
      
      def _delete (dbengine, metadata, searchconditions=None):
         if (
            (searchconditions is not None)
            and (not isinstance(
               searchconditions,
               _DBModel._Record.SearchCondition,
            ))
         ):
            return None
            # raise error
         
         resolvedsearchconditions = (
            searchconditions._resolve(metadata=metadata)
            if (searchconditions)
            else
            [None, [],]
         )
         if (searchconditions):
            searchconditions.metadata = searchconditions.metadata or metadata
            resolvedsearchconditions = [str(searchconditions), None]
         else:
            resolvedsearchconditions = [None, None]
         
         return dbengine.execute_raw(
            (
               'DELETE FROM {0}'.format(metadata._tablename)
               + (' WHERE ({0})'.format(resolvedsearchconditions[0])
                  if (resolvedsearchconditions[0])
                  else ''
               )
               + ';'
            ),
            *(
               [resolvedsearchconditions[-1]]
               if (resolvedsearchconditions[-1])
               else
               []
            ),
            commit=True,
            errorstatus=True,
         )
