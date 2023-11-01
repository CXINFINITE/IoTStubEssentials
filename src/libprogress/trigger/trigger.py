import time
import threading

from .flags import Flags as flags
from .descriptors import Descriptors as descriptors

import libcommon

class Trigger:
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
      
      self._mode                            = flags.MODE_NONE
      self._mode_next                       = mode
      
      self._active                          = False
      
      self._trigger_event                   = flags.INTERVAL_EVENT_NONE
      self._trigger_event_time              = 0.0
      self._trigger_event_description       = descriptors.INTERVAL_EVENT_NONE
      
      self._lock_list_notification          = threading.Lock()
      self._lock_list_blocking              = threading.Lock()
      self._lock_list_waiting               = threading.Lock()
      self._lock_notify                     = threading.Lock()
      self._lock_trigger                    = threading.Lock()
      self._lock_trigger_event              = threading.Lock()
      self._lock_error                      = threading.Lock()
      self._lock_mode                       = threading.Lock()
      self._lock_debug_log                  = threading.Lock()
      self._lock_debug_trace                = threading.Lock()
      
      self._event_trigger_activation        = threading.Event()
      self._event_trigger_trigger           = threading.Event()
      self._event_trigger_pre_min_force     = threading.Event()
      self._event_trigger_pre_min_flush     = threading.Event()
      self._event_interval_trigger          = threading.Event()
      self._event_interval_trigger_force    = threading.Event()
      self._event_interval_trigger_flush    = threading.Event()
      self._event_clock_reset               = threading.Event()
      
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
      if (mode is not None):
         self._mode_next     = mode
      
      mode_thread            = None
      
      if (activate):
         if (
                (mode is not None)
            and (self._active)
         ):
            self.mode(
               activate       = False,
               non_blocking   = non_blocking,
               thread_timeout = thread_timeout,
            )
            
            self._mode_next  = mode
         
         mode_thread         = threading.Thread(
            target            = self._modes,
            kwargs            = {
               'mode'          : self._mode_next,
            },
            daemon            = False,
         )
         
         mode_thread.start()
      elif (activate is False):
         if (mode is None):
            self._mode_next  = self._mode
         elif (mode is not None):
            self._mode_next  = mode
         
         mode_thread         = threading.Thread(
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
      self._lock_mode.acquire()
      
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
               
               if (self._mode == flags.MODE_HYBRID):
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
                  
                  thread_clock          = threading.Thread(
                     target=self._clock_thread,
                  )
                  self._thread_clock    = thread_clock
                  
                  thread_clock.start()
                  
                  self._event_trigger_pre_min_force.set()
               
               if (mode       == flags.MODE_HYBRID):
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
         return None
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
   
   def wait (
      self,
      identifier          = None,
      identity_regenerate = False,
      identity_force_use  = False,
   ):
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
               notification_threads.append(threading.Thread(
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
      if (not (self._mode & flags.MODE_MANUAL)):
         return None
      
      thread_trigger = threading.Thread(
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
            self._trigger_event_description  = descriptors.combine(
               self._trigger_event_description,
               event_description,
            )
         elif (remove):
            if (self._trigger_event & event):
               self._trigger_event          ^= event
            
            self._trigger_event_description  = descriptors.remove(
               event_description,
               self._trigger_event_description,
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
            
            thread_trigger           = threading.Thread(
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
            
            thread_trigger       = threading.Thread(
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
         
         threading.Thread(
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
            self._error_description = descriptors.combine(
               self._error_description,
               error_description,
            )
            self._error_values.update(error_values)
         elif (remove):
            self._error_description = descriptors.remove(
               error_description,
               self._error_description,
            )
            
            for error_key in error_keys:
               try:
                  self._error_values.pop(error_key)
               except:
                  pass
         elif (check):
            return (descriptors.check(
               error_description,
               self._error_description,
            ))
         elif (finalize):
            if (not self._error_error):
               return None
            
            if (not (self._error_raisable or return_raisable)):
               return None
            
            error_string          = 'ERROR:\n{0}\nValues:\n'.format(
               '\n'.join(descriptors.extract(self._error_description)),
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
