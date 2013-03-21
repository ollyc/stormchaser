"""\
Track changes to storm objects via Storm's validator API
"""

from datetime import datetime
from storm.locals import Store, Unicode, Int, DateTime, JSON
from storm.info import get_obj_info


def getclassname(ob):
    """\
    Return the fully qualified class name of instance ``ob``
    """
    cls = ob.__class__
    return u'%s.%s' % (cls.__module__, cls.__name__)


def getpk(ob):
    """\
    Return a tuple of primary key values for ``ob``
    """

    return tuple(n.get() for n in get_obj_info(ob).primary_vars)


class ChangeHistory(object):
    """\
    Model a change history entry.

    Each entry comprises a reference to the changed model class and attribute,
    the primary key value associated with the change, the new value, the
    time of the change and (optionally) the user associated with the change
    """
    __storm_order__ = "ctime"

    #: Primary key of the change history entry
    id = Int(primary=1)

    #: A string reference to the changed class
    ref_class = Unicode()

    #: A reference to the primary key of the changed object. JSON is used so
    #: that compound primary keys can be handled
    ref_pk = JSON()

    #: The name of the changed attribute
    ref_attr = Unicode()

    #: The new value
    new_value = JSON()

    #: Creation time of the log entry
    ctime = DateTime()

    #: User associated with the log entry
    cuser = Int()

    # Callable that takes the changed object and returns a string reference to
    # the class
    _getclassref = None

    # Callable that takes the changed object and returns its primary key values
    _getpk = None

    # Callable returning the user associated with the change, or None.
    _getuser = None

    def __init__(self, ob, attr, value):
        self.ref_class = self._getclassref(ob)
        self.ref_pk = self._getpk(ob)
        self.ref_attr = unicode(attr)
        self.new_value = value
        self.ctime = datetime.now()
        self.cuser = self._getuser()

    @classmethod
    def configure(cls, table, getuser=None, usertype=Int,
                  getclassref=getclassname,
                  getpk=getpk, **kwargs):
        """\
        Return a subclass of ChangeHistory configured to store data in
        ``table``.

        :param table: name of the table to use for storing the changelog data
        :param getuser: (optional) a function returning a user identifier for
                        each change. The function must take no arguments and
                        return a JSON serializable object.
        :param usertype: The column type for the user identifier, which must
                         agree with the return value of getuser. Defaults to
                         ``Int``.
        :param kwargs: Any other keyword arguments will be added as class
                       attributes to the generated class
        """
        class ChangeHistory(cls):
            __storm_table__ = table
            cuser = usertype()
            _getuser = staticmethod(getuser or (lambda: None))
            _getclassref = staticmethod(getclassref)
            _getpk = staticmethod(getpk)

        for name, value in kwargs.items():
            if callable(value):
                value = staticmethod(value)
            setattr(ChangeHistory, name, value)

        return ChangeHistory

    @classmethod
    def changes_for(cls, ob):
        """
        Return a :class:`storm.store.ResultSet` of ChangeHistory objects for
        the given object
        """
        return Store.of(ob).find(cls,
                                 ref_class=cls._getclassref(ob),
                                 ref_pk=cls._getpk(ob))


class ChangeTracker(object):
    """\
    Hook into changes to storm objects via the Storm validation API
    """

    def __init__(self, change_cls, next_validator=None):
        self.change_cls = change_cls
        self.next_validator = next_validator

    def __call__(self, ob, attr, value):
        if self.next_validator:
            value = self.next_validator(ob, attr, value)

        store = Store.of(ob)
        if store:
            store.add(self.change_cls(ob, attr, value))
        return value
