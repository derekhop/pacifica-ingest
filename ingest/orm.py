#!/usr/bin/python
"""ORM for index server."""
import os
import peewee

DB = peewee.MySQLDatabase(os.getenv('MYSQL_ENV_MYSQL_DATABASE', 'pacifica_ingest'),
                          host=os.getenv('MYSQL_PORT_3306_TCP_ADDR', '127.0.0.1'),
                          port=int(os.getenv('MYSQL_PORT_3306_TCP_PORT', 3306)),
                          user=os.getenv('MYSQL_ENV_MYSQL_USER', 'ingest'),
                          passwd=os.getenv('MYSQL_ENV_MYSQL_PASSWORD', 'ingest'))


# pylint: disable=too-few-public-methods
class BaseModel(peewee.Model):
    """Auto-generated by pwiz."""

    class Meta(object):
        """Map to the database connected above."""

        database = DB


class IngestState(BaseModel):
    """Map a python record to a mysql table."""

    job_id = peewee.BigIntegerField(primary_key=True, db_column='id')
    state = peewee.CharField(db_column='state')
    task = peewee.CharField(db_column='task')
    task_percent = peewee.DecimalField(db_column='task_percent')

    @classmethod
    def atomic(cls):
        """Do the DB atomic bits."""
        # pylint: disable=no-member
        return cls._meta.database.atomic()
        # pylint: enable=no-member

    @classmethod
    def database_connect(cls):
        """
        Make sure database is connected.

        Trying to connect a second
        time doesnt cause any problems.
        """
        # pylint: disable=no-member
        cls._meta.database.connect()
        # pylint: enable=no-member

    @classmethod
    def database_close(cls):
        """
        Close the database connection.

        Closing already closed database
        throws an error so catch it and continue on.
        """
        try:
            # pylint: disable=no-member
            cls._meta.database.close()
            # pylint: enable=no-member
        except peewee.ProgrammingError:
            # error for closing an already closed database so continue on
            return

    class Meta(object):
        """Map to uniqueindex table."""

        db_table = 'ingeststate'
# pylint: enable=too-few-public-methods


def update_state(job_id, state, task, task_percent):
    """Update the state of an ingest job."""
    if job_id and job_id >= 0:
        IngestState.database_connect()
        record = IngestState.get_or_create(job_id=job_id,
                                           defaults={'task': '', 'task_percent': 0, 'state': ''})[0]

        record.state = state
        record.task = task
        record.task_percent = task_percent
        record.save()
        IngestState.database_close()


def read_state(job_id):
    """Return the state of an ingest job as a json object."""
    IngestState.database_connect()
    if job_id and job_id >= 0:
        record = IngestState.get(job_id=job_id)
    else:
        record = IngestState()
        record.state = 'DATA_ACCESS_ERROR'
        record.task = 'read_state'
        record.task_percent = 0
    IngestState.database_close()
    return record
