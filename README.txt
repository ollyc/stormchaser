Stormchaser
===========

Track changes to your storm model objects with stormchaser.

Usage
-----

Create a history table to store changes in::
    
        >>> from storm.locals import *
        >>> database = create_database('sqlite:')
        >>> store = Store(database)
        >>> store.execute("""
            CREATE table history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ref_class VARCHAR(200),
                ref_pk VARCHAR(200),
                ref_attr VARCHAR(200),
                new_value VARCHAR(200),
                ctime DATETIME,
                user VARCHAR(200)
            )""")

Now configure a Changelog class that uses the history table::

    >>> changelog_cls = Changelog.configure(table='history')

And add it to your model class columns as a validator::

    >>> class Article(object):
    ...     __storm_table__ = 'articles'
    ...     content = Unicode(validator=ChangelogTracker(changelog_cls))
    ...

