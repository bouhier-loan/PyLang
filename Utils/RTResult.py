from __future__ import annotations

from Errors.Error import Error

######################
# ! RUNTIME RESULT ! #
######################

class RTResult:
    def __init__(self) -> None:
        self.reset()

    def reset(self):
        self.value = None
        self.error : Error = None
        self.func_return_value = None
        self.loop_continue : bool = False
        self.loop_break : bool = False

    def register(self, result : RTResult):
        self.error = result.error
        self.func_return_value = result.func_return_value
        self.loop_continue = result.loop_continue
        self.loop_break = result.loop_break
        return result.value
    
    def success(self, value) -> RTResult:
        self.reset()
        self.value = value
        return self
    
    def success_return(self, value) -> RTResult:
        self.reset()
        self.func_return_value = value
        return self

    def success_continue(self) -> RTResult:
        self.reset()
        self.loop_continue = True
        return self

    def success_break(self) -> RTResult:
        self.reset()
        self.loop_break = True
        return self
    
    def failure(self, error : Error) -> RTResult:
        self.reset()
        self.error = error
        return self
    
    def should_return(self) -> bool:
        return (
            self.error or
            self.func_return_value or
            self.loop_continue or
            self.loop_break
        )