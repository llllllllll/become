from enum import IntEnum, unique
import re

_permissions_pattern = re.compile(r'^(r|-)(w|-)(x|-)(p|s)$')


@unique
class Permission(IntEnum):
    """Flags denoting the permission types a mapped region can have.
    """
    read = 0x0001
    write = 0x0002
    execute = 0x0004
    shared = 0x0008
    private = 0x0010

    @classmethod
    def parse(cls, permissions):
        """Parse permissions from a string.

        Parameters
        ----------
        line : str
            The formatted permissions.

        Returns
        -------
        p : Permissions
            The permission mask defined by this string.

        Raises
        ------
        ValueError
            Raised when the string does not define a permission mask.
        """
        m = _permissions_pattern.match(permissions)
        if m is None:
            raise ValueError('could not parse permissions: %s' % permissions)

        return (
            (cls.read if m.group(1) == 'r' else 0) |
            (cls.write if m.group(2) == 'w' else 0) |
            (cls.execute if m.group(3) == 'x' else 0) |
            (cls.shared if m.group(4) == 's' else cls.private)
        )


def format_permissions(permissions):
    """Format a permission bitmask into a human readable string.

    Parameters
    ----------
    permissions : Permission
        The bitmask to format.

    Returns
    -------
    as_string : str
        The string form of the mask.
    """
    if permissions & Permission.shared and permissions & Permission.private:
        raise ValueError(
            'invalid permissions flags, cannot be private and shared'
        )

    return ''.join((
        'r' if permissions & Permission.read else '-',
        'w' if permissions & Permission.write else '-',
        'x' if permissions & Permission.execute else '-',
        'p' if permissions & Permission.private else 's',
    ))


class MemoryMappedRegion:
    """A representation of a memory mapped region from /proc/<pid>/maps.

    Parameters
    ----------
    start : int
        The start of the mapped region.
    stop : int
        The end of the mapped region.
    permissions : Permission
        The bitmask for the permissions of this mapping.
    offset : int
        The offset into the file or whatever file-like thing this mapping
        occupies.
    dev : str
        The device this mapping is in in the format (major:minor.
    inode : str
        The inode on the device this mapping is on. 0 indicates that no
        inode is associated with this memory region.
    pathname : str
        The name of the file backing the mapping. This may also be one of:

         - [stack]: The initial process's (also known as the main thread's)
            stack.
         - [stack:<tid>]: (since Linux 3.4) A thread's stack (where the <tid>
           is a thread ID).  It corresponds to the /proc/[pid]/task/[tid]/
           path.
         - [vdso]: The virtual dynamically linked shared object.
         - [heap]: The process's heap.

         If this is blank, the mapping is an anonymous mapping from ``mmap``.
    """
    _pattern = re.compile(
        r'^([0-9A-Fa-f]+)-([0-9A-Fa-f]+)'  # start-stop
        r' (.{4})'                         # permissions
        r' ([0-9A-Fa-f]+)'                 # offset
        r' ([0-9]{2}:[0-9]{2})'            # dev
        r' ([0-9]+)'                       # inode
        r' (                   )?(.*)$'    # path
    )

    def __init__(self, start, stop, permissions, offset, dev, inode, pathname):
        self.start = start
        self.stop = stop
        self.permissions = permissions
        self.offset = offset
        self.dev = dev
        self.inode = inode
        self.pathname = pathname

    @classmethod
    def parse(cls, line):
        """Parse a mapped region from a string.

        Parameters
        ----------
        line : str
            The formatted memory mapped region.

        Returns
        -------
        m : MemoryMappedRegion
            The region defined by the string.

        Raises
        ------
        ValueError
            Raised when the string does not define a memory region.
        """
        m = cls._pattern.match(line)
        if m is None:
            raise ValueError('could not parse the given line: %s' % line)

        return cls(
            int(m.group(1), 16),
            int(m.group(2), 16),
            Permission.parse(m.group(3)),
            int(m.group(4), 16),
            m.group(5),
            m.group(6),
            m.group(8),
        )

    @classmethod
    def from_proc_maps(cls):
        """Loads a list of memory mapped regions from ``/proc/self/maps``

        Returns
        -------
        regions : list[MemoryMappedRegion]
            The regions mapped in this process.
        """
        with open('/proc/self/maps') as f:
            return list(map(cls.parse, f.readlines()))

    def __eq__(self, other):
        return (
            isinstance(other, MemoryMappedRegion) and
            self.start == other.start and
            self.stop == other.stop and
            self.permissions == other.permissions and
            self.offset == other.offset and
            self.dev == other.dev and
            self.inode == other.inode and
            self.pathname == other.pathname
        )

    def __str__(self):
        return '%s-%s %s %s %s %s%s' % (
            hex(self.start)[2:],
            hex(self.stop)[2:],
            format_permissions(self.permissions),
            hex(self.offset)[2:].rjust(8, '0'),
            self.dev,
            str(self.inode).ljust(8),
            ('                    ' + self.pathname) if self.pathname else '',
        )

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self)
