# RuntimeError: Click will abort further execution because Python 3 was configured to use ASCII as encoding for the environment. 
# Consult https://click.palletsprojects.com/en/7.x/python3/ for mitigation steps.
def mygetlocale():
  import locale
  l_av = locale.locale_alias.keys()
  l_pref = ['c.utf8', 'en_US.utf8']
  l_ok = [x for x in l_pref if x in l_av]
  if len(l_ok)==0: return None
  return l_ok[0]
  

def mysetlocale():
  li = mygetlocale()
  if li is None:
      return
  
  import os
  #import logging
  #logger = logging.getLogger('git-remote-aws')

  # logger.warning("Setting locale to %s"%li)
  os.environ["LC_ALL"] = li
  os.environ["LANG"]   = li