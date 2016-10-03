from .maps import MemoryMappedRegion, Permission
from ._become import become_impl as _become_impl


def become(ob, to_become):
    """Turn one object into another.

    Parameters
    ----------
    ob : heaptype
        The object to replace. The object must be an instance of a heaptype.
    to_become : heaptype
        The object to replace ``ob`` with. This must also be an instance of a
        heaptype.

    Returns
    -------
    replacement_count : int
        The number of places whee ``ob`` was replaced with ``to_become``.
        This is not the refcount of ``ob`` because this counts every change

    Notes
    -----
    A heaptype is a type which was allocated on the heap, as opposed to a type
    which was allocated statically in the interpreter or some C extension.
    Any class created with the ``class`` statement, or by calling :func:`type`
    will be a heaptype.
    """
    memory_slices = [
        (region.start, region.stop)
        for region in MemoryMappedRegion.from_proc_maps()
        if (region.permissions & Permission.read and
            region.permissions & Permission.write)
    ]

    return _become_impl(ob, to_become, memory_slices)
