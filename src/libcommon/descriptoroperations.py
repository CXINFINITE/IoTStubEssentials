class DescriptorOperations:
   """Collection of basic operations on descriptors.
   
   Methods
   -------
   combine ()
      Combines multiple descriptors into one.
   extract ()
      Seperates combined descriptors.
   remove ()
      Removes specified descriptor from combined descriptors.
   check ()
      Checks if the specified descriptor is a part of combined descriptors.
   """
   
   def combine (*descriptors, separator='||'):
      """Combine multiple descriptors into one.
      
      Combines multiple descriptors by utilizing extract function and string
      joins.
      
      Parameters
      ----------
      descriptors: str
         Descriptors to be combined into one.
      separator: str, default='||'
         Separator to use to combine descriptors.
      
      Returns
      -------
      str
         Returns combined str of descriptors.
      """
      
      available_descriptors = list()
      
      for descriptor in descriptors:
         if (descriptor):
            available_descriptors.extend(DescriptorOperations.extract(
               descriptor,
               separator=separator,
            ))
      
      return str(
         str(separator).join(
            list(set(available_descriptors)),
         )
      )
   
   def extract (descriptor, separator='||'):
      """Seperates combined descriptors.
      
      Simply splits descriptor string into set to get unique descriptors.
      
      Parameters
      ----------
      descriptor: str
         Descriptor to be separated.
      separator: str, default='||'
         Separator used to extract descriptors.
      
      Returns
      -------
      list
         Returns list of individual descriptors (str).
      """
      
      return ([
         idescriptor
         for idescriptor in descriptor.split(separator)
         if (idescriptor)
      ])
   
   def remove (descriptor, descriptors, separator='||'):
      """Removes specified descriptor from combined descriptors.
      
      Removes specified descriptor from combined descriptors by utilizing
      extract and combine functions.
      
      Parameters
      ----------
      descriptor: str
         Descriptor to be removed from descriptors.
      descriptors: str
         Combined descriptor, from which descriptor will be removed.
      separator: str, default='||'
         Separator used to extract and combine descriptors.
      
      Returns
      -------
      str
         Returns combined str of descriptors, with descriptor removed.
      """
      
      descriptors = DescriptorOperations.extract(
         descriptor = descriptors,
         separator  = separator,
      )
      
      try:
         descriptors.remove(descriptor)
      except:
         pass
      
      descriptors = DescriptorOperations.combine(
         *descriptors,
         separator=separator,
      )
      
      return descriptors
   
   def check (descriptor, descriptors):
      """Checks if the specified descriptor is a part of combined descriptors.
      
      Checks specified descriptor's presence in combined descriptors by using
      (sub) string matching.
      
      Parameters
      ----------
      descriptor: str
         Descriptor to check for presence in descriptors.
      descriptors: str
         Combined descriptor, from which descriptor's presence will be checked.
      
      Returns
      -------
      bool
         Returns bool for whether descriptor is a part of descriptors or not.
      """
      return (descriptor in descriptors)
