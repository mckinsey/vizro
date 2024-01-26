# REQUIREMENTS & THOUGHTS
# User must be able to create a Python function (=`python_function`) and at most decorate it -> for a plotly chart, absolutely, for tables and grid as well
# Only fiddle with callable classes and attributes, if you want custom behaviour/new component in the callable

# If that is the case, then the ONE decorator must tranform the `python_function` (i.e. the plain function that returns e.g. a go.Figure) into a CallableClass with appropriate attributes
# if the user uses a standard callable (e.g. OUR dash_datatable, or technically any px.function), that callable could already be the CallableClass

# Few ideas
# Would it make sense to have a new mode?
# New arguments in the capture decorator
import functools
from vizro.models.types import CapturedCallable
import inspect

# This is our current capture decorator in pure form (except the attempted change), something like this must do the transformation of python_function into a CallableClass given the requirements above
class capture:
    def __call__(self, func, /):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            # Something like this must be done, but currently 2nd line fails - see below
            callable_class_instance_of_python_function = CallableClass(func)
            return CapturedCallable(callable_class_instance_of_python_function, *args, **kwargs)

        return wrapped

# This is my first attempt at a CallableClass, but it fails because of the *args in the __call__ method
# This is where the action info, it the information about specific implementations of actions for that callable would be stored, if we could make the instantiation work in the decorator
class CallableClass:
    def __init__(self, func):
        self.func = func
    def __call__(self,*args, **kwargs):
        return self.func(*args, **kwargs)
    # Started fiddling with the signature bit
    # def __signature__(self):
    #     return inspect.signature(self.func)


# This is the python_function that we want to decorate/transform
def python_function(a, b=2):
    print("This is returning say a dash.datatable!",a,b)

callable_class_instance_of_python_function = CallableClass(python_function) # creating the equi
callable_class_instance_of_python_function(4,5) # this behaves like a normal `python_function`

@capture()
def another_python_function_but_decorated(a=1, b=2):
    print("Whoo!",a,b)

try:
    another_python_function_but_decorated(2, b=3) # this does not work, for the reason shown below (it complains about *args)
except Exception as e:
    print("Exception",e)

# One can comment out the other line to see why the CapturedCallable does not work
parameters = inspect.signature(callable_class_instance_of_python_function.func).parameters # this works
# parameters = inspect.signature(function).parameters # this does not as it complains about *args

invalid_params = {
    param.name
    for param in parameters.values()
    if param.kind in [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.VAR_POSITIONAL]
}

print("Params",parameters)
print("Invalid",invalid_params)


