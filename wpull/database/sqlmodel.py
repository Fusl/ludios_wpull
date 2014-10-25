'''Database SQLAlchemy model.'''

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, Enum, Boolean, String
import sqlalchemy.ext.declarative

from wpull.item import Status, URLRecord, LinkType


DBBase = sqlalchemy.ext.declarative.declarative_base()


class URL(DBBase):
    '''URL table containing each URL to be downloaded.'''
    __tablename__ = 'urls'

    id = Column(Integer, primary_key=True, autoincrement=True)

    url_str_id = Column(
        Integer, ForeignKey('url_strings.id'),
        nullable=False, unique=True, index=True
    )
    url_str_record = relationship(
        'URLString', uselist=False, foreign_keys=[url_str_id]
    )
    url = association_proxy('url_str_record', 'url')

    status = Column(
        Enum(
            Status.done, Status.error, Status.in_progress,
            Status.skipped, Status.todo,
        ),
        index=True,
        default=Status.todo,
        nullable=False,
    )
    try_count = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=0)

    top_url_str_id = Column(
        Integer, ForeignKey('url_strings.id'))
    top_url_record = relationship(
        'URLString', uselist=False, foreign_keys=[top_url_str_id])
    top_url = association_proxy('top_url_record', 'url')

    status_code = Column(Integer)

    referrer_id = Column(Integer, ForeignKey('url_strings.id'))
    referrer_record = relationship(
        'URLString', uselist=False, foreign_keys=[referrer_id])
    referrer = association_proxy('referrer_record', 'url')
    inline = Column(Boolean)
    link_type = Column(Enum(LinkType.html, LinkType.css, LinkType.javascript))
    post_data = Column(String)
    filename = Column(String)

    def to_plain(self):
        return URLRecord(
            self.url,
            self.status,
            self.try_count,
            self.level,
            self.top_url,
            self.status_code,
            self.referrer,
            self.inline,
            self.link_type,
            self.post_data,
            self.filename,
        )


class URLString(DBBase):
    '''Table containing the URL strings.

    The :class:`URL` references this table.
    '''
    __tablename__ = 'url_strings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True, index=True)


class Visit(DBBase):
    '''Standalone table for ``--cdx-dedup`` feature.'''
    __tablename__ = 'visits'

    url = Column(String, primary_key=True, nullable=False)
    warc_id = Column(String, nullable=False)
    payload_digest = Column(String, nullable=False)


__all__ = ('DBBase', 'URL', 'URLString', 'Visit')