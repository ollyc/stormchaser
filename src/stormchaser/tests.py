from datetime import datetime
from nose.tools import assert_equal
from storm.locals import create_database, Store, Unicode, Int
from stormchaser import ChangeHistory, ChangeTracker, getpk, getclassname

class TestSupportFunctions(object):

    def test_getpk_returns_single_pk_values(self):

        class A(object):
            __storm_table__ = 'A'
            id = Int(primary=True)

        a = A()
        a.id = 42
        assert_equal(getpk(a), (42,))

    def test_getpk_returns_multi_pk_values(self):

        class A(object):
            __storm_table__ = 'A'
            id1 = Int(primary=1)
            id2 = Int(primary=2)

        a = A()
        a.id1 = 4
        a.id2 = 2
        assert_equal(getpk(a), (4, 2))

    def test_getclassname_returns_fq_name(self):
        from random import Random
        assert_equal(getclassname(Random()), 'random.Random')

class TestChangeHistory(object):

    def test_configure_returns_instance_with_correct_storm_table(self):
        mychangehistory = ChangeHistory.configure('xyzzy')
        assert issubclass(mychangehistory, ChangeHistory)
        assert_equal(mychangehistory.__storm_table__, 'xyzzy')

class TestChangeTracker(object):


    class A(object):
        __storm_table__ = 'testob'
        clt = ChangeTracker(ChangeHistory.configure("history"))
        id = Int(primary=1)
        textval = Unicode(validator=clt)
        intval = Int(validator=clt)

    def setUp(self):
        database = create_database('sqlite:')
        self.store = Store(database)
        self.store.execute("""
            CREATE table history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ref_class VARCHAR(200),
                ref_pk VARCHAR(200),
                ref_attr VARCHAR(200),
                new_value VARCHAR(200),
                ctime DATETIME,
                cuser INT
            )
        """)
        self.store.execute("""
            CREATE TABLE testob (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                textval VARCHAR(200),
                intval INT,
                dateval DATETIME
            )""")

    def tearDown(self):
        self.store.rollback()

    def test_calls_next_validator(self):
        clt = ChangeTracker(ChangeHistory.configure("history"), next_validator = lambda ob, attr, v: v*2)

        class B(self.A):
            textval = Unicode(validator=clt)

        b = B()
        b.textval = u'bork'
        assert b.textval == u'borkbork'

    def test_adds_log_entries(self):

        class B(self.A):
            clt = ChangeTracker(ChangeHistory.configure("history"))
            textval = Unicode(validator=clt)

        b = self.store.add(B())
        b.textval = u'pointless'
        b.textval = u'aimless'
        changes = list(self.store.find(b.clt.change_cls))
        assert_equal(len(changes), 2)
        assert_equal(changes[0].new_value, 'pointless')
        assert_equal(changes[1].new_value, 'aimless')

    def test_value_type_preserved(self):
        a = self.store.add(self.A())
        a.textval = u'one'
        a.intval = 1
        changes = list(self.store.find(a.clt.change_cls))
        assert_equal(type(changes[0].new_value), unicode)
        assert_equal(type(changes[1].new_value), int)

    def test_ctime_set(self):
        start = datetime.now()
        a = self.store.add(self.A())
        a.textval = u'x'
        changes = list(self.store.find(a.clt.change_cls))
        assert_equal(type(changes[0].ctime), datetime)
        assert start < changes[0].ctime < datetime.now()

    def test_cuser_set(self):
        def getuser():
            return u'Fred'

        history = ChangeHistory.configure("history", getuser=getuser, usertype=Unicode)
        class B(self.A):
            textval = Unicode(validator=ChangeTracker(history))

        b = self.store.add(B())
        b.textval = u'foo'
        changes = self.store.find(history)
        assert_equal(changes[0].cuser, u'Fred')

