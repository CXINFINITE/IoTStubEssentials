from .flags import Flags as flags
from .descriptors import Descriptors as descriptors

import time
from threading import (
   Lock,
   Event,
   Thread,
)
from functools import wraps

import libcommon

class Trigger:
   """Trigger progress mechanism.
   
   Provides simultaneous, controlled activation of functions at specified
   time or interval in order to streamline program's progression.
   
   Attributes
   ----------
   _interval_trigger_activation : int, float
      Trigger's pre-active duration.
   _interval_trigger : int, float
      Trigger's active duration.
   _interval_min : int, float
      Minimum duration before next trigger can run.
   _interval_max : int, float
      Duration after which max exceed event is fired.
   _interval_critical : int, float
      Duration after which critical exceed event is fired.
   _interval_trigger_auto_add : int, float
      Duration after which a new trigger is queued if no trigger exists.
   _retries_trigger_auto_add : int
      Number of retries for auto trigger queuing before firing error event.
   _clock_interval : int, float
      Duration after which clock is updated.
   _clock_step : int, float
      Amount by which clock is updated.
   _interval_exceed_action_min : int
      Exceed action for min interval exceed.
   _interval_exceed_action_max : int
      Exceed action for max interval exceed.
   _interval_exceed_action_critical : int
      Exceed action for critical interval exceed.
   _list_notification : dict
      List of callbacks registered for notification.
   _list_blocking : dict
      List of identifiers holding block for next trigger event.
   _list_waiting : list
      List of identifiers waiting for next trigger event.
   _mode : int
      Current execution mode.
   _mode_next : int, NoneType
      Next execution mode, to be activated on switch.
   _active : bool
      System's state.
   _trigger_event : int
      Active event for trigger.
   _trigger_event_time : float
      Instantaneous time at last event for trigger.
   _trigger_event_description : str
      Description for active event for trigger.
   _lock_list_notification : Lock
      Concurrency lock for _list_notification.
   _lock_list_blocking : Lock
      Concurrency lock for _list_blocking.
   _lock_list_waiting : Lock
      Concurrency lock for _list_waiting.
   _lock_notify : Lock
      Concurrency lock for _nofify.
   _lock_trigger : Lock
      Concurrency lock for _trigger.
   _lock_trigger_event : Lock
      Concurrency lock for _trigger_event.
   _lock_error : Lock
      Concurrency lock for _error.
   _lock_mode : Lock
      Concurrency lock for _mode.
   _event_trigger_activation : Event
      Concurrent event variable for pre-active trigger.
   _event_trigger_trigger : Event
      Concurrent event variable for active trigger.
   _event_trigger_pre_min_force : Event
      Concurrent event variable for pre-min force for trigger.
   _event_trigger_pre_min_flush : Event
      Concurrent event variable for pre-min flush for trigger.
   _event_interval_trigger : Event
      Concurrent event variable for trigger.
   _event_interval_trigger_force : Event
      Concurrent event variable for trigger force.
   _event_interval_trigger_flush : Event
      Concurrent event variable for trigger flush.
   _event_clock_reset : Event
      Concurrent event variable for clock reset.
   _thread_trigger : Thread
      Thread of last active trigger.
   _thread_clock : Thread
      Thread of active clock.
   _clock_time : int, float
      Current system time (elapsed) since last trigger.
   _clock_active : bool
      Clock's state.
   _error_error : bool
      Active errors.
   _error_raisable : bool
      Active raisable errors.
   _error_time : int, float
      Instantaneous time at last error.
   _error_description : str
      Description of active errors.
   _error_values : dict
      Active custom description for errors.
   
   Methods
   -------
   __init__ (mode, **intervals, **clock_resolution, **exceed_actions)
      Init trigger system with specified configurations.
   state ()
      Interact with system's state.
   mode ()
      Interact with system's operation mode.
   notification_alert ()
      Handles registration for event based notfications.
   trigger_bind ()
      Binds functions to system for automated execution, threading capable.
   _trigger_bind ()
      Binds functions to system for automated execution.
   _trigger_bind_execute ()
      Execute function with trigger operations.
   wait ()
      Wait for next trigger event to occur.
   block ()
      Add a block preventing next trigger event, until released.
   release ()
      Release the block for next trigger event.
   notify ()
      Send a manual notification alert to all registered receivers.
   trigger_force ()
      Force activate next trigger, overriding active blocks.
   trigger_flush ()
      Flush queued triggers.
   trigger ()
      Manually enqueue a trigger.
   """
   
   def __init__ (
      self,
      
      mode                            = flags.MODE_NONE,
      
      interval_trigger_activation     =  0.1,
      interval_trigger                =  0.2,
      interval_min                    =  1,
      interval_max                    =  4,
      interval_critical               = 10,
      interval_trigger_auto_add       = 20,
      
      retries_trigger_auto_add        =  3,
      
      clock_interval                  =  0.2,
      clock_step                      =  0.2,
      
      interval_exceed_action_min      = flags.INTERVAL_EXCEED_ACTION_IGNORE,
      interval_exceed_action_max      = flags.INTERVAL_EXCEED_ACTION_NOTIFY,
      interval_exceed_action_critical = (
           flags.INTERVAL_EXCEED_ACTION_NOTIFY
         | flags.INTERVAL_EXCEED_ACTION_ERROR_RAISE
         | flags.INTERVAL_EXCEED_ACTION_HALT
      ),
      
      debug_log                       = False,
      debug_trace                     = True,
   ):
      """Init trigger system with specified configurations.
      
      Parameters
      ----------
      mode : int, default=flags.MODE_NONE
         Mode to queue for next activation.
      interval_trigger_activation : int, float, default=0.1
         Trigger's pre-active duration.
      interval_trigger : int, float, default=0.4
         Trigger's active duration.
      interval_min : int, float, default=1.0
         Minimum duration before next trigger can run.
      interval_max : int, float, default=4.0
         Duration after which max exceed event is fired.
      interval_critical : int, float, default=10
         Duration after which critical exceed event is fired.
      interval_trigger_auto_add : int, float, default=20
         Duration after which a new trigger is queued if no trigger exists.
      retries_trigger_auto_add : int, default=3
         Number of retries for auto trigger queuing before firing error event.
      clock_interval : int, float, default=0.2
         Duration after which clock is updated.
      clock_step : int, float, default=0.2
         Amount by which clock is updated.
      interval_exceed_action_min : int, default=IGNORE
         Exceed action for min interval exceed.
      interval_exceed_action_max : int, default=NOTIFY
         Exceed action for max interval exceed.
      interval_exceed_action_critical : int, default=(IGNORE|NOTIFY|HALT)
         Exceed action for critical interval exceed.
      
      Raises
      ------
      Exception
         *  Non positive intervals.
         *  Non increasing intervals.
      """
      
      self._interval_trigger_activation     = abs(float(
                                                 interval_trigger_activation
                                              ))
      self._interval_trigger                = abs(float(interval_trigger))
      self._interval_min                    = abs(float(interval_min))
      self._interval_max                    = abs(float(interval_max))
      self._interval_critical               = abs(float(interval_critical))
      self._interval_trigger_auto_add       = abs(float(
                                                 interval_trigger_auto_add
                                              ))
      
      self._retries_trigger_auto_add        = abs(int(
                                                 retries_trigger_auto_add
                                              ))
      
      self._clock_interval                  = abs(float(clock_interval))
      self._clock_step                      = abs(float(clock_step))
      
      if (not (
         0
         <  self._interval_trigger_activation
         <= self._interval_trigger
      )):
         raise Exception((
                 '{0}::\n'
              + 'interval_trigger_activation: {1}\n'
              + 'interval_trigger           : {2}\n'
            ).format(
               descriptors.ERROR_INTERVALS_NOT_MONOTONIC,
               self._interval_trigger_activation,
               self._interval_trigger,
         ))
      elif (not (
         0
         <  self._interval_trigger_activation
         <= self._interval_min
         <= self._interval_max
         <= self._interval_critical
         <= self._interval_trigger_auto_add
      )):
         raise Exception((
                 '{0}::\n'
              + 'interval_trigger_activation: {0}\n'
              + 'interval_min               : {1}\n'
              + 'interval_max               : {2}\n'
              + 'interval_critical          : {3}\n'
              + 'interval_trigger_auto_add  : {4}\n'
            ).format(
               descriptors.ERROR_INTERVALS_NOT_MONOTONIC,
               self._interval_trigger_activation,
               self._interval_min,
               self._interval_max,
               self._interval_critical,
               self._interval_trigger_auto_add,
         ))
      elif (not (
         0
         <= self._retries_trigger_auto_add
      )):
         raise Exception((
                 '{0}::\n'
              + 'retries_trigger_auto_add: {1}\n'
            ).format(
               descriptors.ERROR_RETRIES_TRIGGER_AUTO_ADD_INVALID,
               self._retries_trigger_auto_add,
         ))
      elif (not (
         0
         <= self._clock_interval
      )):
         raise Exception((
                 '{0}::\n'
              + 'clock_interval: {0}\n'
            ).format(
               descriptors.ERROR_CLOCK_INTERVAL_INVALID,
               self._clock_interval,
         ))
      elif (not (
         0
         <  self._clock_step
      )):
         raise Exception((
                 '{0}::\n'
              + 'clock_step: {0}\n'
            ).format(
               descriptors.ERROR_CLOCK_STEP_INVALID,
               self._clock_step,
         ))
      
      self._interval_exceed_action_min      = interval_exceed_action_min
      self._interval_exceed_action_max      = interval_exceed_action_max
      self._interval_exceed_action_critical = interval_exceed_action_critical
      
      self._list_notification               = dict() # {
                                                     #    id: [
                                                     #       events,
                                                     #       times, # -1 : ULD
                                                     #       callback,
                                                     #    ],
                                                     # }
      self._list_blocking                   = dict() # {
                                                     #    id: times_retain
                                                     #           # -1 : ULD
                                                     # }
      self._list_waiting                    = list() # [
                                                     #    id,
                                                     #    id,
                                                     # ]
      
      if (mode not in (
         flags.MODE_NONE,
         flags.MODE_AUTO,
         flags.MODE_MANUAL,
         flags.MODE_HYBRID,
      )):
         mode = flags.MODE_NONE
      
      self._mode                            = flags.MODE_NONE
      self._mode_next                       = mode
      
      self._active                          = False
      
      self._trigger_event                   = flags.INTERVAL_EVENT_NONE
      self._trigger_event_time              = 0.0
      self._trigger_event_description       = descriptors.INTERVAL_EVENT_NONE
      
      self._lock_list_notification          = Lock()
      self._lock_list_blocking              = Lock()
      self._lock_list_waiting               = Lock()
      self._lock_notify                     = Lock()
      self._lock_trigger                    = Lock()
      self._lock_trigger_event              = Lock()
      self._lock_error                      = Lock()
      self._lock_mode                       = Lock()
      self._lock_debug_log                  = Lock()
      self._lock_debug_trace                = Lock()
      
      self._event_trigger_activation        = Event()
      self._event_trigger_trigger           = Event()
      self._event_trigger_pre_min_force     = Event()
      self._event_trigger_pre_min_flush     = Event()
      self._event_interval_trigger          = Event()
      self._event_interval_trigger_force    = Event()
      self._event_interval_trigger_flush    = Event()
      self._event_clock_reset               = Event()
      
      self._debug_allow_log                 = bool(debug_log)
      self._debug_allow_trace               = bool(debug_trace)
      
      self._debug_data_log                  = list()  # [
                                                      #    trace,
                                                      #    trace,
                                                      # ]
      self._debug_data_trace                = dict()  # {
                                                      #    originator:
                                                      #       trace,
                                                      # }
      self._debug_data_origin_tracker       = dict()  # {
                                                      #    originator: [
                                                      #       log.index,
                                                      #       log.index,
                                                      #    ],
                                                      # }
      
      self._debug_notify                    = None
      self._debug_trigger                   = None
      
      self._thread_trigger                  = None
      self._thread_clock                    = None
      
      self._clock_time                      = 0.0
      self._clock_active                    = False
      
      self._error_error                     = False
      self._error_raisable                  = False
      self._error_time                      = 0.0
      self._error_description               = ''
      self._error_values                    = dict()
      
      '''
      INFO: [plan]
         trigger:
            trigger_activation.set()
               # thread: wait_1() -> granted
            
            time.sleep(interval_trigger)
            
            trigger_activation.clear()
               # thread: wait_1() -> blocked
            
            trigger.set()
               # thread: wait_2() -> granted
            
            clock.reset()
               # clock: reset & resume
            
            time.sleep(interval_trigger_activation)
            trigger.clear()
         
         thread:
            task:
               wait:
                  wait_1()
                  wait_2()
               
               block()
                  work
               release()
            
            task:
               wait:
                  wait_1() -> blocked until next trigger
         
         issue.previous:
            code:
               if (trigger.enabled())
                  # trigger_id        = 1
                  # trigger_time_left = 0.2
               work1()
               if (trigger.enabled())
                  # trigger_id        = 1
                  # trigger_time_left = 0.01
               work2()
               if (trigger.enabled())
                  # trigger_id        = 2
                  # trigger_time_left = 0.0
               work3()
                  # blocked until next trigger
            issue:
               multiple triggers achieved due to:
                  *  short exec time
                  *  trigger enabled for long duration
            ideal:
               *  only 1 trigger per wait
               *  not < 1
               *  not > 1
               *  prevent spill to next trigger
            resolution_requirement:
               *  only 1 wait() should guarantee next / ongoing trigger
               *  block all wait() for next trigger
               *  allow all wait() for current trigger
               *  wait() should be a one-time mechanism, not to be called
                  multiple times
      '''
   
   def _identifier_validate (
      self,
      identifier      = None,
      required        = True,
      force_use       = False,
      regenerate      = False,
      list_validation = [],
      owner           = None,
   ):
      """Validates and/or regerates identifiers as required.
      
      Parameters
      ----------
      identifier : str, NoneType, default=None
         Custom identifier to use, else auto-generate.
      required : bool, default=True
         Is identifier required for process ? If not, bypass process.
      regenerate : bool, default=False
         Allow identifier regeneration upon in-validity of supplied one.
      force_use : bool, default=False
         Force use supplied identifier even if in-valid, overriding existing.
      list_validation : tuple, list, default=[]
         List to utilize for checking uniqueness with.
      owner : str, NoneType, default=None
         Owner for regenerated identifier, else auto-generate as anonymous.
      
      Returns
      -------
      tuple
         Returns tuple containing supplied or new identifier and validity.
      """
      
      if (not required):
         return (identifier, True)
      
      regenerate_identity = False
      
      if (identifier in list_validation):
         if (regenerate):
            regenerate_identity = True
         elif (force_use):
            regenerate_identity = False
         else:
            return (identifier, False)
      
      if ((not identifier) or (regenerate_identity)):
         identifier = libcommon.identifier.generate(
            owner=(owner or (
               'libprogress.trigger[{0}].anonymous'.format(
                  self,
               )
            )),
         )
      
      return (identifier, True)
   
   def state (
      self,
      activate       = None,
      reactivate     = None,
      non_blocking   = False,
      thread_timeout = None,
      errors         = False,
      errors_raise   = False,
      describe       = True,
   ):
      """Interact with system's state.
      
      Parameters
      ----------
      activate : bool, NoneType, default=None
         Set True or False to activate or deactivate system.
      reactivate : bool, NoneType, default=None
         Set True to re-activate system.
      non_blocking : bool, default=False
         Run current interaction in non-blocking mode ?
      thread_timeout : int, float, NoneType, default=None
         Thread timeout if running in blocking mode.
      errors : bool, default=False
         Surface active errors ?
      errors_raise : bool, default=False
         Surface active errors along with raisable ones ?
      describe : bool, default=True
         Describe system state using descriptors ?
      
      Raises
      ------
      Exception
         Exceptions are raised if errors or errors_raise is set, if occurred.
      
      Returns
      -------
      str
         Returns description of system's active state.
      bool
         Returns system's active state, else True on normal run.
      """
      
      error_raisable       = None
      
      if (errors or errors_raise):
         error_raisable    = self._errors(
            finalize        = True,
            return_raisable = errors_raise,
         )
      
      if (activate is not None):
         self.mode(
            activate        = bool(activate),
         )
         
         error_raisable    = self._errors(
            finalize        = True,
            return_raisable = errors_raise,
         )
      elif (reactivate):
         mode              = self.modes()
         
         self.mode(
            activate        = False,
            non_blocking    = non_blocking,
            thread_timeout  = thread_timeout,
         )
         
         error_raisable    = self._errors(
            finalize        = True,
            return_raisable = errors_raise,
         )
         
         self.mode(
            mode            = mode,
            activate        = True,
            non_blocking    = non_blocking,
            thread_timeout  = thread_timeout,
         )
      elif (errors or errors_raise):
         if (error_raisable is not None):
            raise (error_raisable)
      else:
         active            = self._active
         
         if (describe):
            active         = (
               descriptors.STATE_ACTIVE
               if (active)
               else
               descriptors.STATE_INACTIVE
            )
         
         return active
      
      if (error_raisable is not None):
         raise (error_raisable)
      
      return True
   
   def mode (
      self,
      mode           = None,
      activate       = None,
      non_blocking   = False,
      thread_timeout = None,
      describe       = True,
      ignore_active  = True,
   ):
      """Interact with system's operation mode.
      
      Parameters
      ----------
      mode : int, NoneType, default=None
         Execution mode, either to activate or queue for next activation.
      activate : bool, NoneType, default=None
         Set True or False to activate or deactivate execution mode.
      non_blocking : bool, default=False
         Run current interaction in non-blocking mode ?
      thread_timeout : int, float, NoneType, default=None
         Thread timeout if running in blocking mode.
      describe : bool, default=True
         Describe system mode using descriptors ?
      ignore_active : bool, default=True
         Describe system's valid working mode, ignoring system's state.
      
      Returns
      -------
      int
         Returns system's currently active execution mode.
      str
         Returns description of system's currently active execution mode.
      bool
         Returns True on normal run.
      """
      
      if (mode not in (
         flags.MODE_NONE,
         flags.MODE_AUTO,
         flags.MODE_MANUAL,
         flags.MODE_HYBRID,
      )):
         mode = None
      
      if (mode is not None):
         self._mode_next     = mode
      
      mode_thread            = None
      
      if (activate):
         '''
         if (
                (mode is not None)
            and (self._active)
         ):
         '''
         if (self._active):
            '''
            self.mode(
               activate       = False,
               non_blocking   = non_blocking,
               thread_timeout = thread_timeout,
            )
            
            self._mode_next  = mode
            '''
            
            Thread(
               target            = self._modes,
               kwargs            = {
                  'mode'          : flags.MODE_NONE,
               },
               daemon            = False,
            ).start()
         
         mode_thread         = Thread(
            target            = self._modes,
            kwargs            = {
               'mode'          : (mode or None), # self._mode_next,
            },
            daemon            = False,
         )
         
         mode_thread.start()
      elif (activate is False):
         '''
         if (mode is None):
            self._mode_next  = self._mode
         elif (mode is not None):
            self._mode_next  = mode
         '''
         
         mode_thread         = Thread(
            target            = self._modes,
            kwargs            = {
               'mode'          : flags.MODE_NONE,
            },
            daemon            = False,
         )
         
         mode_thread.start()
      else:
         mode                = self._mode
         
         if (
                 ignore_active
            and (not self._active)
         ):
            mode             = self._mode_next
         
         if (describe):
            if (mode        == flags.MODE_NONE):
               mode          = descriptors.MODE_NONE
            elif (mode      == flags.MODE_AUTO):
               mode          = descriptors.MODE_AUTO
            elif (mode      == flags.MODE_MANUAL):
               mode          = descriptors.MODE_MANUAL
            elif (mode      == flags.MODE_HYBRID):
               mode          = descriptors.MODE_HYBRID
            else:
               mode          = descriptors.MODE_SET_UNSET
         elif (mode is None):
            mode             = flags.MODE_NONE
         
         return mode
      
      if (mode_thread):
         if (not non_blocking):
            mode_thread.join(timeout=thread_timeout)
      
      return True
   
   def _modes (
      self,
      mode=flags.MODE_NONE,
   ):
      """Switch system's operation mode.
      
      Performs switch operation only if the target mode is not active.
      Can only switch to/from MODE_NONE to any other mode.
      
      Parameters
      ----------
      mode : int, NoneType, default=flags.MODE_NONE
         Execution mode, to switch to. Use None to switch to next queued mode.
      
      Returns
      -------
      bool
         Returns switch's success.
      """
      
      self._lock_mode.acquire()
      
      if (mode not in (
         flags.MODE_NONE,
         flags.MODE_AUTO,
         flags.MODE_MANUAL,
         flags.MODE_HYBRID,
      )):
         mode = None
      
      if (mode is None):
         mode = self._mode_next
      
      try:
         if (mode not in (
            flags.MODE_NONE,
            flags.MODE_AUTO,
            flags.MODE_MANUAL,
            flags.MODE_HYBRID,
         )):
            return False
         elif (mode           != self._mode):
            if (mode          == flags.MODE_NONE):
               self._mode_next = self._mode
               
               if (self._mode  & flags.MODE_AUTO):
                  self._clock_active    = False
                  
                  self._event_trigger_pre_min_force.clear()
                  self._event_trigger_pre_min_flush.set()
                  
                  self._event_interval_trigger_force.clear()
                  self._event_interval_trigger_flush.set()
                  
                  try:
                     self._thread_clock.join()
                  except:
                     pass
                  
                  try:
                     self._thread_trigger.join()
                  except:
                     pass
                  
                  self._event_trigger_pre_min_flush.clear()
                  self._event_interval_trigger_flush.clear()
                  self._event_clock_reset.clear()
                  
                  self._clock_time      = 0.0
                  self._thread_clock    = None
                  self._thread_trigger  = None
               
               if (self._mode  & flags.MODE_MANUAL):
                  self._event_interval_trigger_force.clear()
                  self._event_interval_trigger_flush.set()
                  
                  try:
                     self._thread_trigger.join()
                  except:
                     pass
                  
                  self._event_interval_trigger_flush.clear()
                  
                  self._thread_trigger  = None
               
               if (self._mode  & flags.MODE_HYBRID):
                  pass
               
               self._event_trigger_activation.clear()
               self._event_trigger_trigger.clear()
               
               self._event_trigger_pre_min_force.clear()
               self._event_trigger_pre_min_flush.clear()
               
               self._event_interval_trigger_force.clear()
               self._event_interval_trigger_flush.clear()
               
               self._event_interval_trigger.clear()
               
               self._active             = False
            elif (self._mode  != flags.MODE_NONE):
               return False
            elif (self._mode  == flags.MODE_NONE):
               self._errors(
                  reset = True,
               )
               self._trigger_events(
                  reset = True,
               )
               
               self._event_trigger_activation.clear()
               self._event_trigger_trigger.clear()
               
               self._event_trigger_pre_min_force.clear()
               self._event_trigger_pre_min_flush.clear()
               
               self._event_interval_trigger_force.clear()
               self._event_interval_trigger_flush.clear()
               
               self._event_interval_trigger.clear()
               
               if (mode        & flags.MODE_MANUAL):
                  self._thread_trigger  = None
               
               if (mode        & flags.MODE_AUTO):
                  self._event_clock_reset.set()
                  
                  self._clock_time      = 0.0
                  self._clock_active    = True
                  
                  thread_clock          = Thread(
                     target=self._clock_thread,
                  )
                  self._thread_clock    = thread_clock
                  
                  thread_clock.start()
                  
                  self._event_trigger_pre_min_force.set()
               
               if (mode        & flags.MODE_HYBRID):
                  pass
               
               self._event_interval_trigger_force.set()
               
               self._active             = True
            
            self._mode                  = mode
      finally:
         self._lock_mode.release()
      
      return True
   
   def notification_alert (
      self,
      identifier          = None,
      callback            = None,
      unregister          = False,
      events              = flags.INTERVAL_EVENT_ALL,
      times               = -1, # unlimited
      identity_regenerate = False,
      identity_force_use  = False,
   ):
      """Handles registration for event based notfications.
      
      Registers or un-registers for notification alert by appending or removing
      details from notification list.
      
      Parameters
      ----------
      identifier : str, NoneType, default=None
         Custom identifier to register callback with, else auto-generate.
      callback : callable, NoneType, default=None
         Callback, used upon alert generation.
      unregister : bool, default=False
         Unregister alert bound to callback with specified identifier.
      events : int, default=flags.INTERVAL_EVENT_ALL
         Events upon which notification alert is to be sent.
      times : int, default=-1
         Number of times to service alerts, upon expiry auto-unregister.
      identity_regenerate : bool, default=False
         Allow identifier regeneration upon in-validity of supplied one.
      identity_force_use : bool, default=False
         Force use supplied identifier even if in-valid, overriding existing.
      
      Returns
      -------
      str
         Returns identifier used upon successful registration.
      bool
         Returns success as bool on unregistration or registration, if failed.
      """
      
      if (unregister):
         if (not identifier):
            return False
         
         self._lock_list_notification.acquire()
         
         try:
            self._list_notification.pop(identifier)
         except:
            pass
         finally:
            self._lock_list_notification.release()
         
         return True
      elif ((not callback)
         or (not callable(callback))
      ):
         return False
      elif (not times):
         return False
      else:
         times = int(times)
      
      identifier, proceed = self._identifier_validate(
         identifier      = identifier,
         required        = True,
         force_use       = identity_force_use,
         regenerate      = identity_regenerate,
         list_validation = self._list_notification.keys(),
         owner           = (
            'libprogress.trigger[{0}].notification_alert.anonymous'.format(
               self,
            )
         ),
      )
      
      if (not proceed):
         return False
      
      self._lock_list_notification.acquire()
      
      try:
         self._list_notification[identifier] = [
            events,
            times,
            callback,
         ]
      finally:
         self._lock_list_notification.release()
      
      return identifier
   
   def trigger_bind (
      self,
      
      trigger_bound_function,
      args           = [],
      kwargs         = {},
      
      identifier     = None,
      times_retain   = -1,
      times_recurse  = -1,
      
      non_blocking   = True,
      thread_timeout = None,
      thread_daemon  = True,
   ):
      """Binds functions to system for automated execution, threading capable.
      
      Allows trigger_bound_function's repeated execution as per standard
      procedures of trigger mechanism.
      
      Parameters
      ----------
      trigger_bound_function : callable
         Function to be bound for automated execution.
      args : tuple, list, default=[]
         Args to be supplied to trigger_bound_function during execution.
      kwargs : dict, default={}
         Kwargs to be supplied to trigger_bound_function during execution.
      identifier : str, NoneType, default=None
         Custom identifier for waits and blocks, else auto-generate.
      times_retain : int, default=-1
         Times to force-retain block for next trigger, remove upon expiry.
      times_recurse : int, default=-1
         Number of times to execute function, upon expiry auto-unbound.
      non_blocking : bool, default=True
         Execute function in non-blocking mode ?
      thread_timeout : int, float, NoneType, default=None
         Thread timeout if running in blocking mode.
      thread_daemon : bool, default=True
         Run executor thread as daemon ?
      
      Returns
      -------
      bool
         Returns True or alive status for executor thread.
      """
      
      thread_trigger_bind = Thread(
         target = self._trigger_bind,
         kwargs = {
            'trigger_bound_function' : trigger_bound_function,
            
            'identifier'             : identifier,
            'times_retain'           : times_retain,
            'times_recurse'          : times_recurse,
            
            'args'                   : args,
            'kwargs'                 : kwargs,
         },
         daemon = bool(thread_daemon),
      )
      thread_trigger_bind.start()
      
      if (not non_blocking):
         thread_trigger_bind.join(timeout=thread_timeout)
         
         return (not thread_trigger_bind.is_alive())
      
      return True
   
   def _trigger_bind (
      self,
      
      trigger_bound_function,
      args           = [],
      kwargs         = {},
      
      identifier     = None,
      times_retain   = -1,
      times_recurse  = -1,
   ):
      """Binds functions to system for automated execution.
      
      Allows trigger_bound_function's repeated execution as per standard
      procedures of trigger mechanism.
      
      Parameters
      ----------
      trigger_bound_function : callable
         Function to be bound for automated execution.
      args : tuple, list, default=[]
         Args to be supplied to trigger_bound_function during execution.
      kwargs : dict, default={}
         Kwargs to be supplied to trigger_bound_function during execution.
      identifier : str, NoneType, default=None
         Custom identifier for waits and blocks, else auto-generate.
      times_retain : int, default=-1
         Times to force-retain block for next trigger, remove upon expiry.
      times_recurse : int, default=-1
         Number of times to execute function, upon expiry auto-unbound.
      
      Returns
      -------
      NoneType
         Returns None.
      """
      
      while (times_recurse):
         times_recurse -= 1
         
         if (times_recurse < 0):
            times_recurse = -1
         
         try:
            self._trigger_bind_execute(
               trigger_bound_function = trigger_bound_function,
               args                   = args,
               kwargs                 = kwargs,
               
               identifier             = identifier,
               times_retain           = times_retain,
            )
         except:
            pass
      
      return None
   
   def _trigger_bind_execute (
      self,
      
      trigger_bound_function,
      args           = [],
      kwargs         = {},
      
      identifier     = None,
      times_retain   = -1,
   ):
      """Execute function with trigger operations.
      
      Executes trigger_bound_function with trigger mechanism's standard
      procedures - wait, block and release.
      
      Parameters
      ----------
      trigger_bound_function : callable
         Function to be bound for automated execution.
      args : tuple, list, default=[]
         Args to be supplied to trigger_bound_function during execution.
      kwargs : dict, default={}
         Kwargs to be supplied to trigger_bound_function during execution.
      identifier : str, NoneType, default=None
         Custom identifier for waits and blocks, else auto-generate.
      times_retain : int, default=-1
         Times to force-retain block for next trigger, remove upon expiry.
      
      Raises
      ------
      Exception
         Exceptions as raised by trigger_bound_function during execution.
      
      Returns
      -------
      object
         Returns trigger_bound_function's return value.
      NoneType
         Returns None on pre-mature termination.
      """
      
      try:
         identifier_wait  = self.wait(
            identifier   = identifier,
         )
      except:
         return None
      
      try:
         identifier_block = self.block(
            identifier   = identifier_wait,
            times_retain = times_retain,
         )
      except:
         if (identifier  != identifier_wait):
            libcommon.identifier.delete(identifier_wait)
         
         return None
      
      try:
         return trigger_bound_function(*args, **kwargs)
      finally:
         self.release(
            identifier = identifier_block,
         )
         
         if (identifier  != identifier_wait):
            libcommon.identifier.delete(identifier_wait)
         
         if (identifier  != identifier_block):
            libcommon.identifier.delete(identifier_block)
      
      return None
   
   def wait (
      self,
      identifier          = None,
      identity_regenerate = False,
      identity_force_use  = False,
   ):
      """Wait for next trigger event to occur.
      
      Waits are meant to ensure that all dependent functions wait for trigger
      event to start their tasks, providing synchronized progress.
      This should be called before starting task, even before calling block.
      
      Parameters
      ----------
      identifier : str, NoneType, default=None
         Custom identifier to use while waiting, else auto-generate.
      identity_regenerate : bool, default=False
         Allow identifier regeneration upon in-validity of supplied one.
      identity_force_use : bool, default=False
         Force use supplied identifier even if in-valid, overriding existing.
      
      Returns
      -------
      bool
         Returns False if invalid parameters.
      str
         Returns identifier used while waiting, upon success.
      """
      
      identifier, proceed = self._identifier_validate(
         identifier      = identifier,
         required        = True,
         force_use       = identity_force_use,
         regenerate      = identity_regenerate,
         list_validation = self._list_waiting,
         owner           = (
            'libprogress.trigger[{0}].wait.anonymous'.format(
               self,
            )
         ),
      )
      
      if (not proceed):
         return False
      
      self._lock_list_waiting.acquire()
      
      try:
         self._list_waiting.append(identifier)
      finally:
         self._lock_list_waiting.release()
      
      try:
         self._event_trigger_activation.wait()
         self._event_trigger_trigger.wait()
      finally:
         self._lock_list_waiting.acquire()
         
         try:
            self._list_waiting.remove(identifier)
         except:
            pass
         finally:
            self._lock_list_waiting.release()
      
      return identifier
   
   def block (
      self,
      identifier          = None,
      times_retain        = -1, # unlimited
      identity_regenerate = False,
      identity_force_use  = False,
   ):
      """Add a block preventing next trigger event, until released.
      
      Blocks are a means to ensure that all dependent functions are activated
      simultaneously (in sync).
      Blocks are registered by appending identifier to blocking list.
      This should be called before starting task, right after wait is over.
      
      Parameters
      ----------
      identifier : str, NoneType, default=None
         Custom identifier to use for block, else auto-generate.
      times_retain : int, default=-1
         Times to force-retain block for next trigger, remove upon expiry.
      identity_regenerate : bool, default=False
         Allow identifier regeneration upon in-validity of supplied one.
      identity_force_use : bool, default=False
         Force use supplied identifier even if in-valid, overriding existing.
      
      Returns
      -------
      bool
         Returns False if invalid parameters.
      str
         Returns identifier for block added.
      """
      
      times_retain = int(times_retain)
      
      identifier, proceed = self._identifier_validate(
         identifier      = identifier,
         required        = True,
         force_use       = identity_force_use,
         regenerate      = identity_regenerate,
         list_validation = self._list_blocking.keys(),
         owner           = (
            'libprogress.trigger[{0}].block.anonymous'.format(
               self,
            )
         ),
      )
      
      if (not proceed):
         return False
      
      self._lock_list_blocking.acquire()
      
      try:
         self._list_blocking[identifier] = times_retain
      finally:
         self._lock_list_blocking.release()
      
      return identifier
   
   def release (
      self,
      identifier,
   ):
      """Release the block for next trigger event.
      
      Blocks are released by removing identifiers from blocking list.
      This should be called after completion of task.
      
      Parameters
      ----------
      identifier : str
         Identifier to used for block to be released.
      
      Returns
      -------
      bool
         Returns False if invalid parameters.
      str
         Returns identifier mapped to block, upon successful removal.
      """
      
      if (not identifier):
         return False
      
      self._lock_list_blocking.acquire()
      
      try:
         self._list_blocking.pop(identifier)
      except:
         pass
      finally:
         self._lock_list_blocking.release()
      
      return identifier
   
   def notify (self, *args, **kwargs):
      """Send a manual notification alert to all registered receivers.
      
      Sends notification alerts to all registered receivers whose registered
      events matches currently active events.
      
      Parameters
      ----------
      event : int, default=flags.INTERVAL_EVENT_NONE
         Event for which the notification has to be triggered.
      event_time : int, float, default=0.0
         Instantaneous time for event.
      event_description : str, default=descriptors.INTERVAL_EVENT_NONE
         Description for event for which notification has to be triggered.
      non_blocking : bool, default=True
         Run notification callbacks in non-blocking mode ?
      thread_timeout : int, float, NoneType, default=None
         Thread timeout if running in blocking mode.
      
      Returns
      -------
      NoneType
         Returns None if incompatible mode.
      bool
         Returns True if success.
      """
      
      if (not (self._mode & flags.MODE_MANUAL)):
         return None
      
      return self._notify(*args, **kwargs)
   
   def _notify (
      self,
      event             = flags.INTERVAL_EVENT_NONE,
      event_time        = 0.0,
      event_description = descriptors.INTERVAL_EVENT_NONE,
      non_blocking      = True,
      thread_timeout    = None,
   ):
      """Send a notification alert to all registered receivers.
      
      Sends notification alerts to all registered receivers whose registered
      events matches currently active events.
      
      Parameters
      ----------
      event : int, default=flags.INTERVAL_EVENT_NONE
         Event for which the notification has to be triggered.
      event_time : int, float, default=0.0
         Instantaneous time for event.
      event_description : str, default=descriptors.INTERVAL_EVENT_NONE
         Description for event for which notification has to be triggered.
      non_blocking : bool, default=True
         Run notification callbacks in non-blocking mode ?
      thread_timeout : int, float, NoneType, default=None
         Thread timeout if running in blocking mode.
      
      Returns
      -------
      bool
         Returns True.
      """
      
      self._lock_notify.acquire()
      
      notification_threads   = list()
      notification_callbacks = list()
      
      try:
         self._lock_list_notification.acquire()
         
         try:
            for identifier in self._list_notification.keys():
               if (
                  (
                     self._list_notification[identifier][0]
                     & event
                  )
                  and self._list_notification[identifier][1]
               ):
                  if (self._list_notification[identifier][1] < 0):
                     self._list_notification[identifier][1]  = -1 # un_limited
                  elif (self._list_notification[identifier][1] in (0, 1,)):
                     if (self._list_notification[identifier][1] == 1):
                        notification_callbacks.append(
                           self._list_notification[identifier][-1],
                        )
                     
                     try:
                        self._list_notification.pop(identifier)
                     except:
                        pass
                     
                     continue
                  else:
                     self._list_notification[identifier][1] -=  1 #    limited
                  
                  notification_callbacks.append(
                     self._list_notification[identifier][-1],
                  )
         finally:
            self._lock_list_notification.release()
         
         for callback in notification_callbacks:
            if (non_blocking is False):
               callback(
                  clock_time        = self._clock_time,
                  event             = event,
                  event_time        = event_time,
                  event_description = event_description,
               )
            else:
               notification_threads.append(Thread(
                  target=callback,
                  kwargs={
                     'clock_time'       : self._clock_time,
                     'event'            : event,
                     'event_time'       : event_time,
                     'event_description': event_description,
                  },
                  daemon=False,
               ))
               notification_threads[-1].start()
      finally:
         self._lock_notify.release()
      
      if (non_blocking is None):
         while (notification_threads):
            notification_threads[-1].join(timeout=thread_timeout)
            notification_threads.pop()
      
      return True
   
   def trigger_force (
      self,
      force         = None,
      force_pre_min = None,
   ):
      """Force activate next trigger, overriding active blocks.
      
      Used to force fire a trigger even if a task is blocking.
      
      Parameters
      ----------
      force : bool, NoneType, default=None
         If bool, enable or disable trigger's normal force state.
      force_pre_min : bool, NoneType, default=None
         If bool, enable or disable trigger's pre-min force state.
      
      Returns
      -------
      NoneType
         Returns None if incompatible mode.
      bool
         Returns True if success.
      """
      
      if (not (self._mode & flags.MODE_MANUAL)):
         return None
      
      if (force_pre_min):
         self._event_trigger_pre_min_force.set()
      elif (force_pre_min is False):
         self._event_trigger_pre_min_force.clear()
      
      if (force):
         self._event_interval_trigger_force.set()
      elif (force is False):
         self._event_interval_trigger_force.clear()
      
      return True
   
   def trigger_flush (
      self,
      flush         = None,
      flush_pre_min = None,
   ):
      """Flush queued triggers.
      
      Used to cancel queued triggers if the need arise.
      
      Parameters
      ----------
      flush : bool, NoneType, default=None
         If bool, enable or disable trigger's normal flush state.
      flush_pre_min : bool, NoneType, default=None
         If bool, enable or disable trigger's pre-min flush state.
      
      Returns
      -------
      NoneType
         Returns None if incompatible mode.
      bool
         Returns True if success.
      """
      
      if (not (self._mode & flags.MODE_MANUAL)):
         return None
      
      if (flush_pre_min):
         self._event_trigger_pre_min_flush.set()
      elif (flush_pre_min is False):
         self._event_trigger_pre_min_flush.clear()
      
      if (flush):
         self._event_interval_trigger_flush.set()
      elif (flush is False):
         self._event_interval_trigger_flush.clear()
      
      return True
   
   def trigger (self, non_blocking=True, thread_timeout=None):
      """Manually enqueue a trigger.
      
      Parameters
      ----------
      non_blocking : bool, default=True
         Run trigger process in non-blocking mode ?
      thread_timeout : int, float, NoneType, default=None
         Thread timeout if running in blocking mode.
      
      Returns
      -------
      NoneType
         Returns None if incompatible mode.
      bool
         Returns True or alive status for executor thread if success.
      """
      
      if (not (self._mode & flags.MODE_MANUAL)):
         return None
      
      thread_trigger = Thread(
         target = self._trigger,
         daemon = False,
      )
      thread_trigger.start()
      
      self._thread_trigger = thread_trigger
      
      if (not non_blocking):
         thread_trigger.join(timeout=thread_timeout)
         
         return (not thread_trigger.is_alive())
      
      return True
   
   def _trigger (self):
      """Processes individual trigger's pre-trigger process.
      
      Keeps next trigger from firing until unti minimum duration is acheived
      and until no task is blocking.
      Also, keeps on checking whether trigger is to be flushed or force fired.
      
      Returns
      -------
      bool
         Returns True or False depending on success.
      """
      
      self._lock_trigger.acquire()
      
      try:
         if (self._mode & flags.MODE_AUTO):
            while (not self._event_interval_trigger.wait(timeout=0.0)):
               if (self._event_trigger_pre_min_force.wait(timeout=0.0)):
                  self._event_trigger_pre_min_force.clear()
                  
                  self._trigger_events(
                     event             = (
                        flags.INTERVAL_EVENT_TRIGGER_PRE_MIN_FORCE
                     ),
                     event_description = (
                        descriptors.INTERVAL_EVENT_TRIGGER_PRE_MIN_FORCE
                     ),
                     combine           = True,
                  )
                  
                  break
               elif (self._event_trigger_pre_min_flush.wait(timeout=0.0)):
                  return False
         
         if (self._event_interval_trigger_flush.wait(timeout=0.0)):
            return False
         
         self._lock_list_blocking.acquire()
         
         try:
            while (self._list_blocking):
               if (self._event_interval_trigger_force.wait(timeout=0.0)):
                  self._event_interval_trigger_force.clear()
                  
                  self._trigger_events(
                     event             = flags.INTERVAL_EVENT_TRIGGER_FORCE,
                     event_description = (
                        descriptors.INTERVAL_EVENT_TRIGGER_FORCE
                     ),
                     combine           = True,
                  )
                  
                  for identifier, times_retain in self._list_blocking.items():
                     if (times_retain < 0):
                        self._list_blocking[identifier]  = -1
                     elif (times_retain > 0):
                        self._list_blocking[identifier] -=  1
                     else:
                        self._list_blocking.pop(identifier)
                  
                  break
               elif (self._event_interval_trigger_flush.wait(timeout=0.0)):
                  return False
         finally:
            self._lock_list_blocking.release()
         
         self._trigger_trigger()
      finally:
         self._lock_trigger.release()
      
      return True
   
   def _trigger_trigger (self):
      """Processes individual trigger and handles post-trigger.
      
      Performs core trigger mechanism - pre-active and active trigger states.
      Then, starts notification thread.
      
      Returns
      -------
      bool
         Returns True.
      """
      
      try:
         try:
            event, event_time, event_description = self._trigger_events(
               finalize=True,
            )
            self._trigger_events(reset=True)
         except:
            pass
         
         self._event_trigger_activation.set()
         
         time.sleep(self._interval_trigger)
         
         self._event_trigger_activation.clear()
         self._event_trigger_trigger.set()
         
         try:
            self._notify(
               event             = event,
               event_time        = event_time,
               event_description = event_description,
               non_blocking      = True,
            )
         except:
            pass
         
         self._event_clock_reset.set()
         time.sleep(self._interval_trigger_activation)
         
         self._event_trigger_trigger.clear()
      finally:
         self._event_trigger_activation.clear()
         self._event_trigger_trigger.clear()
      
      return True
   
   def _trigger_events (
      self,
      event             =       flags.INTERVAL_EVENT_NONE,
      event_description = descriptors.INTERVAL_EVENT_NONE,
      reset             = False,
      change            = False,
      combine           = False,
      remove            = False,
      check             = False,
      finalize          = False,
   ):
      """Interact with system's trigger events.
      
      Provides centralized event handling capabilities for trigger related
      events to internal operations.
      
      Parameters
      ----------
      event : int, default=flags.INTERVAL_EVENT_NONE
         Event to be marked.
      event_description : str, default=descriptors.INTERVAL_EVENT_NONE
         Description of event to be marked.
      reset : bool, default=False
         Reset trigger events' state.
      change : bool, default=False
         Change trigger event to specified event.
      combine : bool, default=False
         Combine specified event with currently active trigger events.
      remove : bool, default=False
         Remove specified event from currently active trigger events.
      check : bool, default=False
         Check specified event's presence in currently active trigger events.
      finalize : bool, default=False
         Finalize currently active trigger events, for final use, and return.
      
      Returns
      -------
      bool
         Returns True on successful alterations.
      tuple
         Returns tuple of (event, event_time, event_descriptions) if unaltered.
      """
      
      self._lock_trigger_event.acquire()
      
      try:
         if (reset):
            self._trigger_event              = flags.INTERVAL_EVENT_NONE
            self._trigger_event_time         = 0.0
            self._trigger_event_description  = descriptors.INTERVAL_EVENT_NONE
         elif (change):
            self._trigger_event              = event
            self._trigger_event_time         = self._clock_time
            self._trigger_event_description  = event_description
         elif (combine):
            self._trigger_event             |= event
            self._trigger_event_time         = self._clock_time
            self._trigger_event_description  = (
               libcommon.descriptoroperations.combine(
                  self._trigger_event_description,
                  event_description,
               )
            )
         elif (remove):
            if (self._trigger_event & event):
               self._trigger_event          ^= event
            
            self._trigger_event_description  = (
               libcommon.descriptoroperations.remove(
                  event_description,
                  self._trigger_event_description,
               )
            )
         elif (check):
            return (self._trigger_event & event)
         elif (finalize):
            if ((
                  self._trigger_event 
                  & flags.INTERVAL_EVENT_TRIGGER
               )
               and (not (
                  self._trigger_event
                  & flags.INTERVAL_EVENT_TRIGGER_PRE_MIN_FORCE
               ))
               and (not (
                  self._trigger_event
                  & flags.INTERVAL_EVENT_TRIGGER_FORCE
               ))
            ):
               self._trigger_event_time = self._clock_time
            
            return (
               self._trigger_event,
               self._trigger_event_time,
               self._trigger_event_description,
            )
         else:
            return (
               self._trigger_event,
               self._trigger_event_time,
               self._trigger_event_description,
            )
      finally:
         self._lock_trigger_event.release()
      
      return True
   
   def _clock_thread (self):
      """Processes clock related and core functionality for trigger system.
      
      Core clock functionality for automatic operation modes.
      Responsible for most of the automated operations like firing trigger,
      resetting clock on trigger, checking when to fire which event, and more.
      
      Returns
      -------
      NoneType
         Returns None.
      """
      
      retries_trigger_auto_add = self._retries_trigger_auto_add
      
      while (self._clock_active):
         event             =       flags.INTERVAL_EVENT_NONE
         event_description = descriptors.INTERVAL_EVENT_NONE
         error_description = None
         
         if (self._event_clock_reset.wait(timeout=0.0)):
            self._event_clock_reset.clear()
            self._event_interval_trigger.clear()
            
            self._clock_time         = 0.0
            retries_trigger_auto_add = self._retries_trigger_auto_add
            
            thread_trigger           = Thread(
               target = self._trigger,
               daemon = False,
            )
            self._thread_trigger     = thread_trigger
            
            self._trigger_events(
               event             =       flags.INTERVAL_EVENT_TRIGGER,
               event_description = descriptors.INTERVAL_EVENT_TRIGGER,
               change            = True,
            )
            self._errors(
               reset             = True,
            )
            
            thread_trigger.start()
         elif (
                (self._clock_time >= self._interval_trigger_auto_add)
            and (not self._lock_trigger.locked())
            and (not retries_trigger_auto_add)
         ):
            error_description = (
               descriptors.ERROR_RETRIES_TRIGGER_AUTO_ADD_EXHAUSTED
            )
         elif (
                (self._clock_time >= self._interval_trigger_auto_add)
            and (not self._lock_trigger.locked())
            and retries_trigger_auto_add
         ):
            retries_trigger_auto_add -= 1
            
            self._event_trigger_pre_min_force.clear()
            self._event_trigger_pre_min_flush.clear()
            
            self._event_interval_trigger_force.clear()
            self._event_interval_trigger_flush.clear()
            
            thread_trigger       = Thread(
               target = self._trigger,
               daemon = False,
            )
            self._thread_trigger = thread_trigger
            
            self._trigger_events(
               event             =       flags.INTERVAL_EVENT_TRIGGER,
               event_description = descriptors.INTERVAL_EVENT_TRIGGER,
               change            = True,
            )
            
            thread_trigger.start()
         elif (
                (self._clock_time >= self._interval_min)
            and (not self._trigger_events(
               event               = flags.INTERVAL_EVENT_EXCEED_MIN,
               check               = True,
            ))
         ):
            event             =       flags.INTERVAL_EVENT_EXCEED_MIN
            event_description = descriptors.INTERVAL_EVENT_EXCEED_MIN
            
            self._event_interval_trigger.set()
         elif (
                (self._clock_time >= self._interval_max)
            and (not self._trigger_events(
               event               = flags.INTERVAL_EVENT_EXCEED_MAX,
               check               = True,
            ))
         ):
            event             =       flags.INTERVAL_EVENT_EXCEED_MAX
            event_description = descriptors.INTERVAL_EVENT_EXCEED_MAX
         elif (
                (self._clock_time >= self._interval_critical)
            and (not self._trigger_events(
               event               = flags.INTERVAL_EVENT_EXCEED_CRITICAL,
               check               = True,
            ))
         ):
            event             =       flags.INTERVAL_EVENT_EXCEED_CRITICAL
            event_description = descriptors.INTERVAL_EVENT_EXCEED_CRITICAL
         
         if (error_description is not None):
            self._errors(
               error_description    = descriptors.ERROR_INTERVAL_EXCEEDED,
               combine              = True,
            )
            self._errors(
               error_description    = error_description,
               combine              = True,
            )
         
         if (event != flags.INTERVAL_EVENT_NONE):
            self._trigger_events(
               event             = event,
               event_description = event_description,
               combine           = True,
            )
            
            self._clock_interval_exceed_action(
               event             = event,
               event_description = event_description,
            )
         
         time.sleep(self._clock_interval)
         self._clock_time += self._clock_step
      
      return None
   
   def _clock_interval_exceed_action (
      self,
      event             =       flags.INTERVAL_EVENT_NONE,
      event_description = descriptors.INTERVAL_EVENT_NONE,
   ):
      """Process system's interval exceed actions.
      
      Performs actions based on exceed events.
      
      Parameters
      ----------
      event : int, default=flags.INTERVAL_EVENT_NONE
         Event to be processed.
      event_description : str, default=descriptors.INTERVAL_EVENT_NONE
         Description of event to be processed.
      
      Returns
      -------
      NoneType
         Returns None on no-action required.
      bool
         Returns True on successful actions.
      """
      
      interval_exceed_actions     = flags.INTERVAL_EXCEED_ACTION_NONE
      
      if (event & flags.INTERVAL_EVENT_EXCEED_MIN):
         interval_exceed_actions  = self._interval_exceed_action_min
      elif (event & flags.INTERVAL_EVENT_EXCEED_MAX):
         interval_exceed_actions  = self._interval_exceed_action_max
      elif (event & flags.INTERVAL_EVENT_EXCEED_CRITICAL):
         interval_exceed_actions  = self._interval_exceed_action_critical
      else:
         return None
      
      if (interval_exceed_actions & flags.INTERVAL_EXCEED_ACTION_NONE):
         return None
      
      if (interval_exceed_actions & flags.INTERVAL_EXCEED_ACTION_IGNORE):
         pass
      
      if (interval_exceed_actions & flags.INTERVAL_EXCEED_ACTION_NOTIFY):
         self._notify(
            event                  = event,
            event_time             = self._clock_time,
            event_description      = event_description,
            non_blocking           = True,
         )
      
      if (interval_exceed_actions & flags.INTERVAL_EXCEED_ACTION_TRIGGER_FORCE):
         self._event_interval_trigger_force.set()
      
      if (interval_exceed_actions & flags.INTERVAL_EXCEED_ACTION_ERROR_RAISE):
         self._errors(
            error_description      = descriptors.ERROR_INTERVAL_EXCEEDED,
            combine                = True,
         )
         self._errors(
            error_description      = event_description,
            combine                = True,
         )
         self._errors(
            raisable               = True,
         )
      
      if (interval_exceed_actions & flags.INTERVAL_EXCEED_ACTION_HALT):
         self._errors(
            error_description      = descriptors.ERROR_INTERVAL_EXCEEDED,
            combine                = True,
         )
         self._errors(
            error_description      = event_description,
            combine                = True,
         )
         
         Thread(
            target                 = self.state,
            kwargs                 = {
               'activate'           : False,
               'non_blocking'       : False,
               'errors'             : True,
            },
            daemon                 = False,
         ).start()
      
      return True
   
   def _errors (
      self,
      error_description = None,
      error_keys        = [],
      reset             = False,
      raisable          = None,
      change            = False,
      combine           = False,
      remove            = False,
      check             = False,
      finalize          = False,
      return_raisable   = False,
      **error_values,
   ):
      """Interact with system's error states.
      
      Provides centralized error handling capability to internal operations.
      
      Parameters
      ----------
      error_description : str, default=None
         Description of error to be marked.
      error_keys : tuple, list, default=[]
         Keys to interact with error_values.
      reset : bool, default=False
         Reset errors' state.
      raisable : bool, NoneType, default=None
         Mark or unmark errors as raisable.
      change : bool, default=False
         Change error description to specified.
      combine : bool, default=False
         Combine specified error description with currently active ones.
      remove : bool, default=False
         Remove specified error description from currently ones.
      check : bool, default=False
         Check specified error description's presence in currently active ones.
      finalize : bool, default=False
         Finalize currently active errors, for final use, and return.
      return_raisable : bool, default=False
         Return raisable active errors, if exists.
      error_values : kwargs, dict, default={}
         Key-Value pairs to be set with errors' state.
      
      Returns
      -------
      NoneType
         Return None if no errors or un-raisable errors during finalize.
      Exception
         Returns raisable Exception with current error state upon finalize.
      bool
         Returns errors' presence or raisability as required, else True.
      """
      
      self._lock_error.acquire()
      
      try:
         if (reset):
            self._error_error       = False
            self._error_raisable    = False
            self._error_time        = 0.0
            self._error_description = ''
            self._error_values      = dict()
         elif (raisable is not None):
            self._error_raisable    = bool(raisable)
         elif (change):
            self._error_error       = True
            self._error_time        = self._clock_time
            self._error_description = error_description
            self._error_values      = error_values
         elif (combine):
            self._error_error       = True
            self._error_time        = self._clock_time
            self._error_description = (
               libcommon.descriptoroperations.combine(
                  self._error_description,
                  error_description,
               )
            )
            self._error_values.update(error_values)
         elif (remove):
            self._error_description = (
               libcommon.descriptoroperations.remove(
                  error_description,
                  self._error_description,
               )
            )
            
            for error_key in error_keys:
               try:
                  self._error_values.pop(error_key)
               except:
                  pass
         elif (check):
            return (libcommon.descriptoroperations.check(
               error_description,
               self._error_description,
            ))
         elif (finalize):
            if (not self._error_error):
               return None
            
            if (not (self._error_raisable or return_raisable)):
               return None
            
            error_string          = 'ERROR:\n{0}\nValues:\n'.format(
               '\n'.join(
                  libcommon.descriptoroperations.extract(
                     self._error_description,
                  )
               ),
            )
            
            error_values_max_len  = len(max([
               'clock_time',
               'error_time',
               *self._error_values.keys()
            ]))
            
            error_string         += (
                 'clock_time{0}: {1}\n'
               + 'error_time{0}: {2}\n'
               + '{3}{4}'
            ).format(
               (' ' * (error_values_max_len - 10)),
               self._clock_time,
               self._error_time,
               '\n'.join([
                  '{0}{1}: {2}'.format(
                     error_values_key,
                     (' ' * (error_values_max_len - len(error_values_key))),
                     error_values_value,
                  )
                  for error_values_key, error_values_value
                  in self._error_values.items()
               ]),
               (
                  '\n'
                  if (self._error_values)
                  else
                  ''
               ),
            )
            
            return (Exception(error_string))
         elif (return_raisable):
            return (self._error_raisable)
         else:
            return (self._error_error)
      finally:
         self._lock_error.release()
      
      return True
   
   def _debug (
      self,
      debug_originator='libprogress.trigger.debug.trace.anonymous',
      **kwargs,
   ):
      if (not self._debug_allow_trace):
         return None
      
      try:
         debug_originator = str(debug_originator)
      except:
         self._debug(
            debug_originator = 'libprogress.trigger.debug.trace.str_failure',
            originator       = debug_originator,
            **kwargs,
         )
         
         return False
      
      debug_trace = {
         'clock_time': self._clock_time,
         'originator': debug_originator,
         'data'      : kwargs,
      }
      
      self._lock_debug_trace.acquire()
      
      try:
         self._debug_data_trace[originator] = debug_trace
      finally:
         self._lock_debug_trace.release()
      
      self._debug_log(
         originator  = debug_originator,
         debug_trace = debug_trace,
      )
      
      return True
   
   def _debug_log (
      self,
      originator,
      debug_trace,
   ):
      if (not self._debug_allow_log):
         return None
      
      try:
         originator = str(originator)
      except:
         self._debug(
            debug_originator = 'libprogress.trigger.debug.log.str_failure',
            originator       = originator,
            debug_trace      = debug_trace,
         )
         
         return False
      
      self._lock_debug_log.acquire()
      
      try:
         if (type(self._debug_data_origin_tracker[originator]).__name__
            not in ('list',)
         ):
            self._debug_data_origin_tracker[originator] = list()
         
         self._debug_data_origin_tracker[originator].append(
            len(self._debug_data_log)
         )
         self._debug_data_log.append(debug_trace)
      finally:
         self._lock_debug_log.release()
      
      return True
