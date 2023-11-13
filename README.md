# tournament-timer
This software helps with timer in badminton tournament (could be used for other applications)
It is mainly intended for SJSU badminton tournament, and me the author to be there to help explain how the app work.
The basic functions of this software:
- allows you to keep track of
  - how long each court has been used with a match
  - countdown for warm up
  - flashes court when countdown finishes
- have a queue for called matches
  - Each called match participant will have CALL_TIME minutes before getting DQ
  - keep tracks of how long each participant have after being called
  - when the time runout, it will flash blue
- Google slides specified in PRESENTATION_ID (currently for https://tinyurl.com/SJSUFall23)
  - automatically add matches that are called onto the google slide
  - every UPDATE_THRESHOLD, the app will auto update the time on google slide
