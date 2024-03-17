class Descriptors:
   """Descriptors for trigger progress mechanism.
   """
   
   MODE_NONE                            = 'mode.none'
   MODE_AUTO                            = 'mode.auto'
   MODE_MANUAL                          = 'mode.manual'
   MODE_HYBRID                          = 'mode.hybrid'
   
   MODE_SET_UNSET                       = 'mode.set.unset'
   MODE_SET_SUCCESS                     = 'mode.set.success'
   MODE_SET_FAILURE                     = 'mode.set.failure'
   
   STATE_ACTIVE                         = 'state.active'
   STATE_INACTIVE                       = 'state.inactive'
   
   INTERVAL_EXCEED_ACTION_NONE          = 'interval.exceed.action.none'
   INTERVAL_EXCEED_ACTION_IGNORE        = 'interval.exceed.action.ignore'
   INTERVAL_EXCEED_ACTION_NOTIFY        = 'interval.exceed.action.notify'
   INTERVAL_EXCEED_ACTION_TRIGGER_FORCE = 'interval.exceed.action.trigger_force'
   INTERVAL_EXCEED_ACTION_ERROR_RAISE   = 'interval.exceed.action.error_raise'
   INTERVAL_EXCEED_ACTION_HALT          = 'interval.exceed.action.halt'
   
   INTERVAL_EVENT_NONE                  = 'interval.event.none'
   INTERVAL_EVENT_TRIGGER               = 'interval.event.trigger'
   INTERVAL_EVENT_TRIGGER_PRE_MIN_FORCE = 'interval.event.trigger_pre_min_force'
   INTERVAL_EVENT_TRIGGER_FORCE         = 'interval.event.trigger_force'
   
   INTERVAL_EVENT_EXCEED_MIN            = 'interval.event.exceed.min'
   INTERVAL_EVENT_EXCEED_MAX            = 'interval.event.exceed.max'
   INTERVAL_EVENT_EXCEED_CRITICAL       = 'interval.event.exceed.critical'
   
   (
      ERROR_RETRIES_TRIGGER_AUTO_ADD_INVALID
   )                                    = (
      'error.retries.trigger_auto_add.invalid'
   )
   (
      ERROR_RETRIES_TRIGGER_AUTO_ADD_EXHAUSTED
   )                                    = (
      'error.retries.trigger_auto_add.exhausted'
   )
   ERROR_CLOCK_INTERVAL_INVALID         = 'error.clock.interval.invalid'
   ERROR_CLOCK_STEP_INVALID             = 'error.clock.step.invalid'
   ERROR_INTERVAL_EXCEEDED              = 'error.interval.exceeded'
   ERROR_INTERVALS_NOT_MONOTONIC        = 'error.intervals.not_monotonic'
