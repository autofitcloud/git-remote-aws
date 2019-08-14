# RuntimeError: Click will abort further execution because Python 3 was configured to use ASCII as encoding for the environment. 
# Consult https://click.palletsprojects.com/en/7.x/python3/ for mitigation steps.

# This sucks because it doesn't work on lambda. Just setting en_US.utf8 blindly
"""
def mygetlocale():
  import locale
  l_av = locale.locale_alias.keys()
  # l_pref = ['c.utf8', 'en_US.utf8']
  l_pref = ['en_US.utf8', 'c.utf8'] # because locale_alias sucks (https://stackoverflow.com/questions/53320311/how-do-i-find-all-available-locales-in-python#comment93521010_53320311), put en_US first, then c
  l_ok = [x for x in l_pref if x in l_av]
  if len(l_ok)==0: return None
  return l_ok[0]
  

def mysetlocale():
  li = mygetlocale()
  if li is None:
      return
  
  #import logging
  #logger = logging.getLogger('git-remote-aws')
  #logger.warning("Setting locale to %s"%li)
  
  import os
  os.environ["LC_ALL"] = li
  os.environ["LANG"]   = li
"""

def mysetlocale():
  li = 'en_US.utf8'
  import os
  os.environ["LC_ALL"] = li
  os.environ["LANG"]   = li