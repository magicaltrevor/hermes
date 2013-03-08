from hermes.engines.databases import *


class AwaitingJobs(SQLObject):
	_connection = hermes_read_db
	class sqlmeta:
		table="jobs"
	plugin = StringCol(length=45, default=None)
	to_address = StringCol(length=255, default=None)
	from_address = StringCol(length=255, default=None)
	subject = StringCol(length=255, default=None)
	message = StringCol(length=40000, default=None)
	created_at = DateTimeCol(default=None)
	login = StringCol(length=255, default=None)
	password = StringCol(length=255, default=None)
	info = StringCol(length=255, default=None)
	times_processed = IntCol(length=3, default=None)
	priority = IntCol(length=1, default=5)
	
	
class ProcessingJobs(SQLObject):
	_connection = hermes_read_db
	class sqlmeta:
		table="in_process"
	plugin = StringCol(length=45, default=None)
	to_address = StringCol(length=255, default=None)
	from_address = StringCol(length=255, default=None)
	subject = StringCol(length=255, default=None)
	message = StringCol(length=40000, default=None)
	pickedup_at = DateTimeCol(default=None)
	login = StringCol(length=255, default=None)
	password = StringCol(length=255, default=None)
	info = StringCol(length=255, default=None)
	times_processed = IntCol(length=3, default=None)
	priority = IntCol(length=1, default=5)


class CompletedJobs(SQLObject):
	_connection = hermes_read_db
	class sqlmeta:
		table="completed"
	plugin = StringCol(length=45, default=None)
	to_address = StringCol(length=255, default=None)
	from_address = StringCol(length=255, default=None)
	subject = StringCol(length=255, default=None)
	message = StringCol(length=40000, default=None)
	completed_at = DateTimeCol(default=None)
	login = StringCol(length=255, default=None)
	password = StringCol(length=255, default=None)
	info = StringCol(length=255, default=None)
	times_processed = IntCol(length=3, default=None)
	priority = IntCol(length=1, default=5)


class FailedJobs(SQLObject):
	_connection = hermes_read_db
	class sqlmeta:
		table="failed"
	plugin = StringCol(length=45, default=None)
	to_address = StringCol(length=255, default=None)
	from_address = StringCol(length=255, default=None)
	subject = StringCol(length=255, default=None)
	message = StringCol(length=40000, default=None)
	failed_at = DateTimeCol(default=None)
	login = StringCol(length=255, default=None)
	password = StringCol(length=255, default=None)
	info = StringCol(length=255, default=None)
	times_processed = IntCol(length=3, default=None)
	priority = IntCol(length=1, default=5)