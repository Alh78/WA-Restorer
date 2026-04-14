import wa_r.exceptions
import sqlite3 as sql
import wa_r.parsing
import wa_r.types
import datetime
import logging
import typing
import os


class SendersCache:
    def __init__(self):
        self.__message_senders_dict = dict() # {name:id}
        self.__message_senders_dict_reversed = dict() # {id:name}

    @property
    def message_senders_dict(self):
        return self.__message_senders_dict
    
    @property
    def message_senders_dict_reversed(self):
        return self.__message_senders_dict_reversed

    @property
    def message_senders(self):
        return list(self.__message_senders_dict.items())

    @property
    def message_senders_reversed(self):
        return list(self.__message_senders_dict_reversed.items())

    @property
    def message_senders_names(self):
        return list(self.__message_senders_dict.keys())
    
    @property
    def message_senders_ids(self):
        return list(self.__message_senders_dict.values())
    
    def get_message_sender_name(self, sender_id: int) -> str:
        return self.message_senders_dict_reversed[sender_id]

    def get_message_sender_id(self, sender_name: str) -> int:
        return self.__message_senders_dict[sender_name]

    def add_message_sender(self, sender_name: str, sender_id: int):        
        if sender_id in self.message_senders_ids:
            raise ValueError("Specified Sender ID already has been added to cache.")
        
        if sender_name in self.message_senders_names:
            raise KeyError("Specified Sender name already has been added to cache.")

        self.__message_senders_dict[sender_name] = sender_id
        self.__message_senders_dict_reversed[sender_id] = sender_name

    def remove_message_sender_by_name(self, sender_name: str):
        if not isinstance(sender_name, str):
            raise TypeError("Invalid argument type.")
        
        self.__message_senders_dict_reversed.pop(self.__message_senders_dict[sender_name])
        self.__message_senders_dict.pop(sender_name)       
        
    def remove_message_sender_by_id(self, sender_id: int):
        if not isinstance(sender_id, int):
            raise TypeError("Invalid argument type.")

        self.__message_senders_dict.pop(self.message_senders_dict_reversed[sender_id])
        self.__message_senders_dict_reversed.pop(self.message_senders_dict[sender_id])
    
    def reset_cache(self): # Use this only when needed.
        self.__message_senders_dict = dict()
        self.__message_senders_dict_reversed = dict()


class AttachedMessagesDatabaseProcessor:

    def __init__(self, file_name: str):
        self.__file_name = os.path.basename(file_name)
        self.__file_path = os.path.dirname(file_name)

        self.__full_file_path = os.path.abspath(file_name)

        self.senders = SendersCache()

        self.database_log = logging.getLogger("AttachedMessagesDatabaseProcessor") # We will add handlers in main flow.

        #self.database_log.warning("Before doing any operation on this database, please ensure you've copied initial database file to prevent potential data loss.")

        self.database_log.info(f"Reading database file...", extra = {"path": self.__full_file_path})
        
        if not os.path.exists(self.__full_file_path):
            self.database_log.critical("Specified database file doesn't exist!")
            raise FileNotFoundError(self.__full_file_path)

        self._media_hash_column_exists = False

        self.__conn = sql.connect(self.__full_file_path)
        self.__cursor = self.__conn.cursor()

        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.database_log.info("SQLite database initialization successful!")

        self.database_log.info(f"Loading cache automatically...")
        self.load_cache()
    
    @property
    def file_name(self):
        return self.__file_name
    
    @property
    def file_path(self):
        return self.__file_path
    
    @property
    def conn(self):
        return self.__conn
    
    @property
    def cursor(self):
        return self.__cursor

    def load_cache(self) -> None:
        self.database_log.info("Loading senders cache from database on memory...")
        self.database_log.debug("Sending SELECT query to database...")

        self.cursor.execute("SELECT * FROM SENDERS")
        senders_information = self.cursor.fetchall()

        self.database_log.debug("Fetched senders from DB!")

        for sender_name, sender_id in senders_information:
            self.database_log.debug(f"Trying to add Sender(name=\"{sender_name}\", id={sender_id}) to the cache...")
            # We're putting try except stage here to be able to handle the situation more way better
            try:
                self.senders.add_message_sender(sender_name, sender_id) #!

            except KeyError: # This sender is already placed in cache, so we can pass it. TODO: give detailed logs here
                self.database_log.debug(f"Sender(name=\"{sender_name}\", id={sender_id}) already exists in cache, skipping")

            except ValueError: #This means there's a conflict between cache and database, so cache must be cleaned to prevent wrong write operations on DB.
                self.database_log.warning(f"Conflict between database and cache has been detected on Sender(name=\"{sender_name}\", id={sender_id})")
                self.database_log.info("Due to conflict between database and cache, resetting senders cache and reloading...")

                self.senders.reset_cache()
                self.load_cache()

            else:
                self.database_log.debug(f"Sender(name=\"{sender_name}\", id={sender_id}) has been succesfully added to cache!")
        
        self.database_log.info("Cache load from database successfully!")

    def commit_changes(self) -> None:
        self.database_log.info("Committing changes not committed yet...")

        self.cursor.execute("VACUUM")
        self.conn.commit()

        self.database_log.info("Committing successful.")

    def revert_changes(self) -> None:
        self.database_log.info("Reverting changes not committed yet...")
        self.conn.rollback()
        self.database_log.info("Reverting successful.")

    def filter_media_messages(self):
        self.database_log.info("Filtering messages containing media...")
        self.cursor.execute("DELETE FROM MEDIA_FILES WHERE FILE_TYPE NOT IN (?, ?)",
                            (wa_r.types.WPFileTypes.IMAGE_FILE_TYPE, wa_r.types.WPFileTypes.VIDEO_FILE_TYPE))
        self.cursor.execute("DELETE FROM MESSAGES WHERE MESSAGE_ID NOT IN (SELECT DISTINCT MESSAGE_ID FROM MEDIA_FILES)")

    def filter_media_origin_messages(self): # Destructive. This method cannot be done without applying origination.
        self.database_log.info("Filtering origin media messages...")
        self.cursor.executescript("""DELETE FROM MEDIA_FILES
                                        WHERE rowid NOT IN (
                                            SELECT mf.rowid
                                            FROM MEDIA_FILES mf
                                            JOIN MESSAGES m ON m.MESSAGE_ID = mf.MESSAGE_ID
                                            WHERE (m.MESSAGE_TIMESTAMP, mf.FILE_NAME_TIMESTAMP, m.LINE_INDEX) = (
                                                SELECT 
                                                    MIN(m2.MESSAGE_TIMESTAMP),
                                                    MIN(mf2.FILE_NAME_TIMESTAMP),
                                                    MIN(m2.LINE_INDEX)
                                                FROM MEDIA_FILES mf2
                                                JOIN MESSAGES m2 ON m2.MESSAGE_ID = mf2.MESSAGE_ID
                                                WHERE mf2.FILE_HASH = mf.FILE_HASH
                                            )
                                        );

                                     DELETE FROM MESSAGES
                                        WHERE MESSAGE_ID NOT IN (
                                            SELECT DISTINCT MESSAGE_ID
                                            FROM MEDIA_FILES
                                        );""")

    def filter_media_messages_manually(self, included_files_list: typing.Iterable[str]): # Destructive, WIP
        self.database_log.info("Filtering manually...")
        self.database_log.debug("Filtering whitelist", extra = {"included_files": included_files_list})
        self.cursor.executescript("""DROP TABLE IF EXISTS INCLUDED_FILES;
                                     CREATE TEMPORARY TABLE INCLUDED_FILES (FILE_NAME TEXT UNIQUE);""")
        self.cursor.executemany("INSERT INTO INCLUDED_FILES VALUES (?)", [(i,) for i in included_files_list])

        self.cursor.execute("SELECT FILE_NAME FROM INCLUDED_FILES EXCEPT SELECT FILE_NAME FROM MEDIA_FILES")
        included_files_missing_in_db = [file_name[0] for file_name in self.cursor.fetchall()]
    
        if included_files_missing_in_db:
            self.database_log.warning(f"{len(included_files_missing_in_db)} files in whitelist don't exist in database.", extra = {"missing_whitelist_files_preview": included_files_missing_in_db[:25]})

            if len(included_files_missing_in_db) > 25:
                self.database_log.warning("For seeing other whitelist files missing in database, set logging level to DEBUG.")
                self.database_log.debug("Full list of missing files:", extra = {"missing_whitelist_files": included_files_missing_in_db})


        self.cursor.executescript("""DELETE FROM MEDIA_FILES WHERE FILE_NAME NOT IN (SELECT FILE_NAME FROM INCLUDED_FILES);
                                     DELETE FROM MESSAGES WHERE MESSAGE_ID NOT IN (SELECT MESSAGE_ID FROM MEDIA_FILES);
                                     DROP TABLE INCLUDED_FILES;
                                  """)

    def _ensure_media_hash_column(self):
        if self._media_hash_column_exists:
            return

        self.cursor.execute("PRAGMA table_info(MEDIA_FILES)")
        media_files_columns = {column[1] for column in self.cursor.fetchall()}

        if "MEDIA_HASH" not in media_files_columns:
            self.cursor.execute("ALTER TABLE MEDIA_FILES ADD COLUMN MEDIA_HASH BLOB")

        self._media_hash_column_exists = True

    def add_attached_message_media_hash(self, message: wa_r.types.AttachedMessageData, media_hash: bytes):
        self._ensure_media_hash_column()
        self.cursor.execute("UPDATE MEDIA_FILES SET MEDIA_HASH = ? WHERE FILE_NAME = ?", (media_hash, message.file_data.file_name))

    def get_senders_message_count(self, sender_id: int, unique_media_messages: bool = False) -> int:
        if unique_media_messages:
            self.cursor.execute("SELECT COUNT(DISTINCT FILE_HASH) FROM MESSAGES m INNER JOIN MEDIA_FILES mf ON m.MESSAGE_ID = mf.MESSAGE_ID WHERE SENDER_ID = ?", (sender_id,))

        else:
            self.cursor.execute("SELECT COUNT(*) FROM MESSAGES WHERE SENDER_ID = ?", (sender_id,))

        return self.cursor.fetchone()[0]

    def get_all_message_count(self, unique_media_messages: bool = False) -> int:
        self.database_log.info(f"Getting {'unique' if unique_media_messages else ''} media messages count...")

        if unique_media_messages:
            self.cursor.execute("SELECT COUNT(DISTINCT FILE_HASH) FROM MESSAGES m INNER JOIN MEDIA_FILES mf ON m.MESSAGE_ID = mf.MESSAGE_ID")

        else:
            self.cursor.execute("SELECT COUNT(*) FROM MESSAGES")

        return self.cursor.fetchone()[0]


    def get_sender_message_by_attached_file_name(self, file_name: str) -> typing.Union[wa_r.types.AttachedMessageData,
                                                                                       typing.List[wa_r.types.AttachedMessageData]]:
        self.database_log.debug(f"Getting messages attached with \"{file_name}\" file...")
        self.database_log.debug("Sending SELECT query to database...")
        self.cursor.execute("""SELECT 
                                    s.SENDER_NAME,
                                    m.LINE_INDEX,
                                    m.MESSAGE_TIMESTAMP,
                                    mf.FILE_NAME,
                                    mf.FILE_TYPE,
                                    mf.FILE_NAME_TIMESTAMP,
                                    mf.FILE_HASH
                               FROM MESSAGES m
                               JOIN SENDERS s ON s.SENDER_ID = m.SENDER_ID
                               JOIN MEDIA_FILES mf ON m.MESSAGE_ID = mf.MESSAGE_ID
                               WHERE mf.FILE_NAME = ?""", (file_name,))

        self.database_log.debug("Fetching all messages specified with file...")
        messages_attached_with_specified_file = self.cursor.fetchall() # Assuming this data is small enough.

        self.database_log.debug("Parsing fetched datas from databases and converting to AttachedMessageData type...")
        specified_message_datas = [wa_r.parsing.package_message_data_raw(*message) for message in messages_attached_with_specified_file]

        return specified_message_datas if len(specified_message_datas) != 1 else specified_message_datas[0]

    def get_sender_media_messages_between_dates(self, start_date: datetime.datetime,
                                                      end_date: datetime.datetime,
                                                      sender_id: int) -> typing.Union[wa_r.types.AttachedMessageData,
                                                                                      typing.List[wa_r.types.AttachedMessageData]]:
        self.database_log.debug("Sending SELECT query to database...")                                                                                      
        self.cursor.execute("""SELECT 
                                    s.SENDER_NAME,
                                    m.LINE_INDEX,
                                    m.MESSAGE_TIMESTAMP,
                                    mf.FILE_NAME,
                                    mf.FILE_TYPE,
                                    mf.FILE_NAME_TIMESTAMP,
                                    mf.FILE_HASH
                               FROM MESSAGES m
                               JOIN SENDERS s ON s.SENDER_ID = m.SENDER_ID
                               JOIN MEDIA_FILES mf ON m.MESSAGE_ID = mf.MESSAGE_ID
                               WHERE s.SENDER_ID = ? AND m.MESSAGE_TIMESTAMP BETWEEN ? AND ?""", (sender_id, start_date.timestamp(), end_date.timestamp()))

        self.database_log.debug("Fetching all messages in the specified time range...")
        messages_attached_in_specified_range = self.cursor.fetchall() # Assuming this data is small enough.

        self.database_log.debug("Parsing fetched datas from databases and converting to AttachedMessageData type...")
        specified_message_datas = [wa_r.parsing.package_message_data_raw(*message) for message in messages_attached_in_specified_range]

        return specified_message_datas if len(specified_message_datas) != 1 else specified_message_datas[0]


    def check_media_file_exists_by_file_name(self, file_name: str) -> bool: # WIP
        self.cursor.execute("SELECT 1 FROM MEDIA_FILES WHERE FILE_NAME = ? LIMIT 1", (file_name,))
        return bool(self.cursor.fetchone())

    def check_media_files_exists_by_file_name(self, file_names_list: typing.Iterable[str]) -> typing.Dict[str, bool]: #WIP
        self.cursor.executescript("""DROP TABLE IF EXISTS EXISTING_CHECK_FILES;
                                     CREATE TEMPORARY TABLE EXISTING_CHECK_FILES (FILE_NAME TEXT UNIQUE);""")
        self.cursor.executemany("INSERT INTO EXISTING_CHECK_FILES VALUES (?)", [(i,) for i in file_names_list])
        self.cursor.execute("SELECT FILE_NAME, EXISTS(SELECT 1 FROM MEDIA_FILES mf WHERE ecf.FILE_NAME = mf.FILE_NAME) FROM EXISTING_CHECK_FILES ecf")
        
        return {file_name: bool(file_exists) for file_name, file_exists in self.cursor.fetchall()}



    def close(self) -> None:
        self.database_log.info("Resetting senders cache...")
        self.senders.reset_cache()

        self.database_log.info("Auto-reverting applied and not committed changes...")
        self.revert_changes()

        self.database_log.info("Closing database connection...")
        self.conn.close()


class AttachedMessagesDatabaseImporter:

    def __init__(self, file_name: str):
        self.__file_name = os.path.basename(file_name)
        self.__file_path = os.path.dirname(file_name)

        self.__full_file_path = os.path.abspath(file_name)

        self.senders = SendersCache()

        self.database_log = logging.getLogger("AttachedMessagesDatabaseImporter") # We will add handlers in main flow.

        self.database_log.info(f"Creating database file...", extra = {"path": self.__full_file_path})
        
        if self.file_path:
            os.makedirs(self.file_path, exist_ok = True)

        self.__conn = sql.connect(self.__full_file_path)
        self.__cursor = self.__conn.cursor()

        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.database_log.info(f"SQLite database initialization successful!")
    
        self.create_tables()
        self.database_log.info("Table creation successful.")
    
    @property
    def file_name(self):
        return self.__file_name
    
    @property
    def file_path(self):
        return self.__file_path
    
    @property
    def conn(self):
        return self.__conn
    
    @property
    def cursor(self):
        return self.__cursor

    def create_tables(self) -> None:
        self.database_log.debug("Sending table creationg queries...")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS SENDERS (SENDER_NAME TEXT UNIQUE, SENDER_ID INTEGER PRIMARY KEY AUTOINCREMENT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS MESSAGES (MESSAGE_ID INTEGER PRIMARY KEY AUTOINCREMENT, MESSAGE_TIMESTAMP INTEGER, SENDER_ID INTEGER, LINE_INDEX INTEGER, FOREIGN KEY (SENDER_ID) REFERENCES SENDERS(SENDER_ID))")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS MEDIA_FILES (FILE_NAME TEXT, FILE_HASH BLOB, FILE_TYPE TEXT, FILE_NAME_TIMESTAMP INTEGER, MESSAGE_ID INTEGER, FOREIGN KEY (MESSAGE_ID) REFERENCES MESSAGES(MESSAGE_ID))")

        self.cursor.execute("CREATE INDEX IF NOT EXISTS IDX_SENDER_ID ON MESSAGES (SENDER_ID)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS IDX_FILE_HASH ON MEDIA_FILES (FILE_HASH)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS IDX_FILE_TYPE ON MEDIA_FILES (FILE_TYPE)")

        self.conn.commit()
        self.database_log.debug("New tables commited on database!")

    def load_cache(self) -> None:
        self.database_log.info("Loading senders cache from database on memory...")
        self.database_log.debug("Sending SELECT query to database...")

        self.cursor.execute("SELECT * FROM SENDERS")
        senders_information = self.cursor.fetchall()

        self.database_log.debug("Fetched senders from DB!")

        for sender_name, sender_id in senders_information:
            self.database_log.debug(f"Trying to add Sender(name=\"{sender_name}\", id={sender_id}) to the cache...")
            # We're putting try except stage here to be able to handle the situation more way better
            try:
                self.senders.add_message_sender(sender_name, sender_id) #!

            except KeyError: # This sender is already placed in cache, so we can pass it. TODO: give detailed logs here
                self.database_log.debug(f"Sender(name=\"{sender_name}\", id={sender_id}) already exists in cache, skipping")

            except ValueError: #This means there's a conflict between cache and database, so cache must be cleaned to prevent wrong write operations on DB.
                self.database_log.critical(f"Conflict between database and cache has been detected on Sender(name=\"{sender_name}\", id={sender_id}) ")
                raise wa_r.exceptions.DatabaseCacheConflictException()               # Code must be aborted
                # This won't be wrapped.

            else:
                self.database_log.debug(f"Sender(name=\"{sender_name}\", id={sender_id}) has been succesfully added to cache!")
        
        self.database_log.info("Cache load from database successfully!")


    def commit_changes(self) -> None:
        self.database_log.info("Committing changes not committed yet...")
        self.conn.commit()
        self.database_log.info("Committing successful.")

    def revert_changes(self) -> None:
        self.database_log.info("Reverting changes not committed yet...")
        self.conn.rollback()
        self.database_log.info("Reverting successful.")

    def add_attached_message(self, message: wa_r.types.AttachedMessageData, commit_now = False) -> None:
        self.database_log.debug(f"Adding Message(line_index={message.line_index}) to database...")

        try:
            self.add_message_sender(message.sender, commit_now) 
        
        except wa_r.exceptions.SenderAdditionException:
            self.database_log.error(f"Failed to insert Sender(sender_name=\"{message.sender}\") of Message(line_index={message.line_index}) into the database.")
            self.database_log.warning(f"Message(line_index={message.line_index}) and its attachments won't be added to database.")
            raise

        self.database_log.debug(f"Sending insertion query for Message(line_index={message.line_index})...")
        self.cursor.execute("INSERT INTO MESSAGES VALUES (NULL, ?, ?, ?) RETURNING MESSAGE_ID", (message.message_date.timestamp(),
                                                                                                 self.senders_cache.get_message_sender_id(message.sender),
                                                                                                 message.line_index))
        message_id = self.cursor.fetchone()

        if not message_id:
            self.database_log.error(f"Failed to insert Message(line_index={message.line_index}) into the database and couldn't retrieve message ID from database.")
            self.database_log.warning(f"Attachment of Message(line_index={message.line_index}) won't be added to database.")
            raise wa_r.exceptions.MessageInsertionError(f"Failed to insert Message(line_index={message.line_index})")

        message_id = message_id[0]
        self.database_log.debug(f"Insertion query sent for Message(line_index={message.line_index}, message_id={message_id}).")
        
        if commit_now:
            self.conn.commit()
            self.database_log.debug(f"Forced to commit now on add_attached_message for Message(line_index={message.line_index}) successfully.")
        
        self.add_attached_file(message.file, message_id) 
        
    def add_message_sender(self, sender_name: str, commit_now = False) -> None:
        # Must load cache before this stage
        if sender_name not in self.senders.message_senders_names:
            self.database_log.debug(f"Sending insertion query for Sender(sender_name=\"{sender_name}\")...")
            self.cursor.execute("INSERT INTO SENDERS VALUES (?, NULL) RETURNING SENDER_ID", (sender_name,)) 

            sender_id = self.cursor.fetchone() #Checkout

            if not sender_id: #If list is empty, something wrong happened. Abort the process
                raise wa_r.exceptions.SenderAdditionError(f"Failed to add Sender(sender_name=\"{sender_name}\"})")
            
            self.database_log.debug(f"Insertion query for Sender(sender_name=\"{sender_name}\") sent!")

            if commit_now:
                self.conn.commit()
                self.database_log.debug(f"Forced to commit now on add_message_sender for Sender(sender_name=\"{sender_name}\") successfully.")
            
            self.database_log.debug(f"Adding Sender(sender_name=\"{sender_name}\") to the cache...")
            sender_id = sender_id[0]
            self.senders.add_message_sender(sender_name, sender_id)
            self.database_log.debug(f"Sender(sender_name=\"{sender_name}\") added to the cache.")

        else:
            self.database_log.debug(f"Sender(sender_name=\"{sender_name}\") already exists in cache.")


    def add_attached_file(self, file_data: wa_r.types.WPFileData, message_id: int) -> None: # ! MESSAGE ID MUST NOT TO BE BROKEN
        self.database_log.debug(f"Inserting new file attached to Message(id={message_id})...")
        self.cursor.execute("INSERT INTO MEDIA_FILES VALUES (?, ?, ?, ?, ?)", (file_data.file_meta_data.file_name,
                                                                               file_data.file_hash,
                                                                               file_data.file_meta_data.file_type.value, # It is enum parameter
                                                                               None if file_data.file_meta_data.file_name_timestamp is None else int(file_data.file_meta_data.file_name_timestamp.timestamp()),
                                                                               message_id
                                                                               ))
        self.database_log.debug(f"Insertion query of new file attached to Message(id={message_id}) sent!")

    def close(self) -> None:
        self.database_log.info("Closing database connection...")
        self.conn.close()
