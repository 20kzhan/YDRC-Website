import logging
import pprint



class P(pprint.PrettyPrinter):
  def _format(self, object, *args, **kwargs):
    if isinstance(object, str):
      if len(object) > 20:
        object = object[:20] + '...'
    return pprint.PrettyPrinter._format(self, object, *args, **kwargs)