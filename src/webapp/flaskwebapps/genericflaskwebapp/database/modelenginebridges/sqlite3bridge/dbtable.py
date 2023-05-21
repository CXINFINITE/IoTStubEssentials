class _DBTable:
   _base_mainmodel_exempted = False
   _tables = dict()
   
   def _register (tablename, fields):
      if (not tablename):
         raise ValueError(
            'database.modelenginebridges.sqlite3bridge:_DBTable:: '
            + 'attempt to create model without modelname'
         )
      
      tablename = str(tablename)
      
      if (tablename in _DBTable._tables.keys()):
         raise ValueError(
            'database.modelenginebridges.sqlite3bridge:_DBTable:: '
            + 'model \'{0}\' already exists, cannot create duplicate'.format(
               tablename,
            )
         )
      
      if ((not fields) or (not (len(fields)))):
         raise ValueError(
            'database.modelenginebridges.sqlite3bridge:_DBTable:: '
            + 'cannot create model (\'{0}\') without fields'.format(
               tablename,
            )
         )
      
      _DBTable._tables[tablename] = fields
      
      return True
