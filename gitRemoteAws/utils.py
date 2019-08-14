# RuntimeError: Click will abort further execution because Python 3 was configured to use ASCII as encoding for the environment. 
# Consult https://click.palletsprojects.com/en/7.x/python3/ for mitigation steps.
def mygetlocale():
  import locale
  l_av = [x.lower() for x in locale.locale_alias.values()]                                                                                                                                                              
  l_pref = ['c.utf-8', 'c.utf8', 'en_us.utf-8', 'en_us.utf8']
  for li in l_pref:
    if li in l_av:
      return li
      
  return None
  

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