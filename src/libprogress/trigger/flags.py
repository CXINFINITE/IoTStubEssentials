class Flags:
   MODE_NONE                                          =   1
   MODE_AUTO                                          =   2
   MODE_MANUAL                                        =   4
   MODE_HYBRID                                        =   6
   
   INTERVAL_EXCEED_ACTION_NONE                        =   1
   INTERVAL_EXCEED_ACTION_IGNORE                      =   2
   INTERVAL_EXCEED_ACTION_NOTIFY                      =   4
   INTERVAL_EXCEED_ACTION_TRIGGER_FORCE               =   8
   INTERVAL_EXCEED_ACTION_ERROR_RAISE                 =  16
   INTERVAL_EXCEED_ACTION_HALT                        =  32
   
   INTERVAL_EVENT_NONE                                =   1
   INTERVAL_EVENT_TRIGGER                             =   2
   INTERVAL_EVENT_TRIGGER_PRE_MIN_FORCE               =   4
   INTERVAL_EVENT_TRIGGER_FORCE                       =   8
   INTERVAL_EVENT_EXCEED_MIN                          =  16
   INTERVAL_EVENT_EXCEED_MAX                          =  32
   INTERVAL_EVENT_EXCEED_CRITICAL                     =  64
   INTERVAL_EVENT_ALL                                 = 126
