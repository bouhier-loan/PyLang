from Error import Error
######################
# ! RUNTIME RESULT ! #
######################

class RTResult:
    def __init__(self) -> None:
        self.value = None
        self.error : Error = None

    def register(self, result : RTResult):
        if result.error: self.error = result.error
        return result.value
    
    def success(self, value) -> RTResult:
        self.value = value
        return self
    
    def failure(self, error : Error) -> RTResult:
        self.error = error
        return self