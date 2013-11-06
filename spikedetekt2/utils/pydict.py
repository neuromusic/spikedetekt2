"""Handle user-specified and default dictionaries."""
# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import os

from six import string_types, iteritems


# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------
def to_str(val):
    """Get a string representation of any Python variable."""
    if isinstance(val, string_types):
        return "'{0:s}'".format(val)
    else:
        return str(val)

def to_lower(d):
    return {key.lower(): val for key, val in iteritems(d)}
    

# -----------------------------------------------------------------------------
# Python script <==> dictionaries conversion
# -----------------------------------------------------------------------------
def python_to_pydict(script_contents):
    """Load a Python script with dictionaries into a dictionary."""
    pydict = {}
    exec script_contents in {}, pydict
    return to_lower(pydict)
    
def pydict_to_python(pydict):
    """Convert a dictionaries dictionary into a Python script."""
    return "\n".join(["{0:s} = {1:s}".format(key, to_str(val))
        for key, val in sorted(pydict.iteritems())])

def get_pydict(filename=None, pydict_default={}, **kwargs):
    pydict_final = pydict_default.copy()
    if isinstance(filename, string_types):
        # Path to pydict file.
        with open(filename, 'r') as f:
            pydict_prm = python_to_pydict(f.read())
            pydict_final.update(pydict_prm)
    pydict_final.update(kwargs)
    return to_lower(pydict_final)
