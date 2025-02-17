class File(object):
    def __init__(self, filename: str,_filepath: str,size: str | None) -> None:
        self.filename = filename
        self._filepath = _filepath
        self.size = size
        self._state = "Załadowany"
        self._complete = str(False)
    
    def __iter__(self):
          for each in self.__dict__.values():
              yield each    

