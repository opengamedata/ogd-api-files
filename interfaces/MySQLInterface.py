# import libraries
from mysql.connector import connection, cursor
import logging
import sshtunnel
import sys
import traceback
from datetime import datetime, date, time, timedelta
from typing import Any, Dict, List, Tuple, Optional

# import locals
from interfaces.DataInterface import DataInterface

## Dumb struct to collect data used to establish a connection to a SQL database.
class SQLLogin:
    def __init__(self, host: str, port: int, db_name: str, user: str, pword: str):
        self.host    = host
        self.port    = port
        self.db_name = db_name
        self.user    = user
        self.pword   = pword
 
## Dumb struct to collect data used to establish a connection over ssh.
class SSHLogin:
    def __init__(self, host: str, port: int, user: str, pword: str):
        self.host    = host
        self.port    = port
        self.user    = user
        self.pword   = pword

## @class SQL
#  A utility class containing some functions to assist in retrieving from a database.
#  Specifically, helps to connect to a database, make selections, and provides
#  a nicely formatted 500 error message.
class SQL:

    # Function to set up a connection to a database, via an ssh tunnel if available.
    @staticmethod
    def ConnectDB(db_settings:Dict[str,Any], ssh_settings:Optional[Dict[str,Any]]=None) -> Tuple[Optional[sshtunnel.SSHTunnelForwarder], Optional[connection.MySQLConnection]]:
        """
        Function to set up a connection to a database, via an ssh tunnel if available.

        :param db_settings: A dictionary mapping names of database parameters to values.
        :type db_settings: Dict[str,Any]
        :param ssh_settings: A dictionary mapping names of ssh parameters to values, or None if no ssh connection is desired., defaults to None
        :type ssh_settings: Optional[Dict[str,Any]], optional
        :return: A tuple consisting of the tunnel and database connection, respectively.
        :rtype: Tuple[Optional[sshtunnel.SSHTunnelForwarder], Optional[connection.MySQLConnection]]
        """
        tunnel  : Optional[sshtunnel.SSHTunnelForwarder] = None
        db_conn : Optional[connection.MySQLConnection]   = None
        # Load settings, set up consts.
        DB_HOST = db_settings['DB_HOST']
        DB_NAME = db_settings["DB_NAME"]
        DB_PORT = int(db_settings['DB_PORT'])
        DB_USER = db_settings['DB_USER']
        DB_PW = db_settings['DB_PW']
        sql_login = SQLLogin(host=DB_HOST, port=DB_PORT, db_name=DB_NAME, user=DB_USER, pword=DB_PW)
        
        logging.info("Preparing database connection...")
        if ssh_settings is not None:
            SSH_USER = ssh_settings['SSH_USER']
            SSH_PW   = ssh_settings['SSH_PW']
            SSH_HOST = ssh_settings['SSH_HOST']
            SSH_PORT = ssh_settings['SSH_PORT']
            if (SSH_HOST != "" and SSH_USER != "" and SSH_PW != ""):
                ssh_login = SSHLogin(host=SSH_HOST, port=SSH_PORT, user=SSH_USER, pword=SSH_PW)
                tunnel,db_conn = SQL._connectToMySQLviaSSH(sql=sql_login, ssh=ssh_login)
            else:
                db_conn = SQL._connectToMySQL(login=sql_login)
                tunnel = None
        else:
            db_conn = SQL._connectToMySQL(login=sql_login)
            tunnel = None
        logging.info("Done preparing database connection.")
        return (tunnel, db_conn)

    # Function to help connect to a mySQL server.
    @staticmethod
    def _connectToMySQL(login:SQLLogin) -> Optional[connection.MySQLConnection]:
        """Function to help connect to a mySQL server.

        Simply tries to make a connection, and prints an error in case of failure.
        :param login: A SQLLogin object with the data needed to log into MySQL.
        :type login: SQLLogin
        :return: If successful, a MySQLConnection object, otherwise None.
        :rtype: Optional[connection.MySQLConnection]
        """
        try:
            db_conn = connection.MySQLConnection(host     = login.host,    port    = login.port,
                                                 user     = login.user,    password= login.pword,
                                                 database = login.db_name, charset = 'utf8')
            logging.debug(f"Connected to SQL (no SSH) at {login.host}:{login.port}/{login.db_name}, {login.user}")
            return db_conn
        #except MySQLdb.connections.Error as err:
        except Exception as err:
            msg = f"""Could not connect to the MySql database.
            Login info: host={login.host}, port={login.port} w/type={type(login.port)}, db={login.db_name}, user={login.user}.
            Full error: {type(err)} {str(err)}"""
            logging.error(msg)
            traceback.print_tb(err.__traceback__)
            return None

    ## Function to help connect to a mySQL server over SSH.
    @staticmethod
    def _connectToMySQLviaSSH(sql:SQLLogin, ssh:SSHLogin) -> Tuple[Optional[sshtunnel.SSHTunnelForwarder], Optional[connection.MySQLConnection]]:
        """Function to help connect to a mySQL server over SSH.

        Simply tries to make a connection, and prints an error in case of failure.
        :param sql: A SQLLogin object with the data needed to log into MySQL.
        :type sql: SQLLogin
        :param ssh: An SSHLogin object with the data needed to log into MySQL.
        :type ssh: SSHLogin
        :return: An open connection to the database if successful, otherwise None.
        :rtype: Tuple[Optional[sshtunnel.SSHTunnelForwarder], Optional[connection.MySQLConnection]]
        """
        tunnel    : Optional[sshtunnel.SSHTunnelForwarder] = None
        db_conn   : Optional[connection.MySQLConnection] = None
        MAX_TRIES : int = 5
        tries : int = 0
        connected_ssh : bool = False

        # First, connect to SSH
        while connected_ssh == False and tries < MAX_TRIES:
            if tries > 0:
                logging.info("Re-attempting to connect to SSH.")
            try:
                tunnel = sshtunnel.SSHTunnelForwarder(
                    (ssh.host, ssh.port), ssh_username=ssh.user, ssh_password=ssh.pword,
                    remote_bind_address=(sql.host, sql.port), logger=Logger.std_logger
                )
                tunnel.start()
                connected_ssh = True
                logging.debug(f"Connected to SSH at {ssh.host}:{ssh.port}, {ssh.user}")
            except Exception as err:
                msg = f"Could not connect to the SSH: {type(err)} {str(err)}"
                logging.error(msg)
                traceback.print_tb(err.__traceback__)
                tries = tries + 1
        if connected_ssh == True and tunnel is not None:
            # Then, connect to MySQL
            try:
                db_conn = connection.MySQLConnection(host     = sql.host,    port    = tunnel.local_bind_port,
                                                     user     = sql.user,    password= sql.pword,
                                                     database = sql.db_name, charset ='utf8')
                logging.debug(f"Connected to SQL (via SSH) at {sql.host}:{tunnel.local_bind_port}/{sql.db_name}, {sql.user}")
                return (tunnel, db_conn)
            except Exception as err:
                msg = f"Could not connect to the MySql database: {type(err)} {str(err)}"
                logging.error(msg)
                traceback.print_tb(err.__traceback__)
                if tunnel is not None:
                    tunnel.stop()
                return (None, None)
        else:
            return (None, None)

    @staticmethod
    def disconnectMySQL(db:Optional[connection.MySQLConnection], tunnel:Optional[sshtunnel.SSHTunnelForwarder]=None) -> None:
        if db is not None:
            db.close()
            logging.debug("Closed MySQL database connection")
        else:
            logging.debug("No MySQL database to close.")
        if tunnel is not None:
            tunnel.stop()
            logging.debug("Stopped MySQL tunnel connection")
        else:
            logging.debug("No MySQL tunnel to stop")

    # Function to build and execute SELECT statements on a database connection.
    @staticmethod
    def SELECT(cursor        :cursor.MySQLCursor,          db_name        : str,                   table    : str,
               columns       :List[str]           = [],    filter         : Optional[str] = None,
               sort_columns  :Optional[List[str]] = None,  sort_direction : str           = "ASC", grouping : Optional[str] = None,
               distinct      :bool                = False, offset         : int           = 0,     limit    : int           = -1,
               fetch_results :bool                = True) -> Optional[List[Tuple]]:
        """Function to build and execute SELECT statements on a database connection.

        :param cursor: A database cursor, retrieved from the active connection.
        :type cursor: cursor.MySQLCursor
        :param db_name: The name of the database to which we are connected.
        :type db_name: str
        :param table: The name of the table from which we want to make a selection.
        :type table: str
        :param columns: A list of columns to be selected. If empty (or None), all columns will be used (SELECT * FROM ...). Defaults to None
        :type columns: List[str], optional
        :param filter: A string giving the constraints for a WHERE clause (The "WHERE" term itself should not be part of the filter string), defaults to None
        :type filter: str, optional
        :param sort_columns: A list of columns to sort results on. The order of columns in the list is the order given to SQL. Defaults to None
        :type sort_columns: List[str], optional
        :param sort_direction: The "direction" of sorting, either ascending or descending., defaults to "ASC"
        :type sort_direction: str, optional
        :param grouping: A column name to group results on. Subject to SQL rules for grouping, defaults to None
        :type grouping: str, optional
        :param distinct: A bool to determine whether to select only rows with distinct values in the column, defaults to False
        :type distinct: bool, optional
        :param limit: The maximum number of rows to be selected. Use -1 for no limit., defaults to -1
        :type limit: int, optional
        :param fetch_results: A bool to determine whether all results should be fetched and returned, defaults to True
        :type fetch_results: bool, optional
        :return: A collection of all rows from the selection, if fetch_results is true, otherwise None.
        :rtype: Optional[List[Tuple]]
        """
        d          = "DISTINCT" if distinct else ""
        cols = ",".join(columns) if columns is not None and len(columns) > 0 else "*"
        sort_cols  = ",".join(sort_columns) if sort_columns is not None and len(sort_columns) > 0 else None
        table_path = db_name + "." + str(table)
        params = []

        sel_clause = f"SELECT {d} {cols} FROM {table_path}"
        where_clause = "" if filter    is None else f"WHERE {filter}"
        group_clause = "" if grouping  is None else f"GROUP BY {grouping}"
        sort_clause  = "" if sort_cols is None else f"ORDER BY {sort_cols} {sort_direction} "
        lim_clause   = "" if limit < 0         else f"LIMIT {str(max(offset, 0))}, {str(limit)}" # don't use a negative for offset
        query = f"{sel_clause} {where_clause} {group_clause} {sort_clause} {lim_clause};"

        return SQL.Query(cursor=cursor, query=query, params=None, fetch_results=fetch_results)

    @staticmethod
    def Query(cursor:cursor.MySQLCursor, query:str, params:Optional[Tuple], fetch_results: bool = True) -> Optional[List[Tuple]]:
        result : Optional[List[Tuple]] = None
        # first, we do the query.
        logging.debug(f"Running query: {query}\nWith params: {params}")
        start = datetime.now()
        cursor.execute(query, params)
        time_delta = datetime.now()-start
        logging.debug(f"Query execution completed, time to execute: {time_delta}")
        # second, we get the results.
        if fetch_results:
            result = cursor.fetchall()
            time_delta = datetime.now()-start
            loggging.debug(f"Query fetch completed, total query time:    {time_delta} to get {len(result) if result is not None else 0:d} rows")
        return result

class MySQLInterface(DataInterface):

    # *** BUILT-INS ***
    def __init__(self, config:Dict[str,Any]):
        self._tunnel    : Optional[sshtunnel.SSHTunnelForwarder] = None
        self._db        : Optional[connection.MySQLConnection] = None
        self._db_cursor : Optional[cursor.MySQLCursor] = None
        super().__init__(config=config)
        self.Open()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _open(self, force_reopen:bool = False) -> bool:
        if force_reopen:
            self.Close()
            self.Open(force_reopen=False)
        if not self._is_open:
            start = datetime.now()
            
            _sql_cfg = self._config["MYSQL_CONFIG"]
            _ssh_cfg = self._config["MYSQL_CONFIG"]["SSH_CONFIG"]
            self._tunnel, self._db = SQL.ConnectDB(db_settings=_sql_cfg, ssh_settings=_ssh_cfg)
            if self._db is not None:
                self._db_cursor = self._db.cursor()
                self._is_open = True
                time_delta = datetime.now() - start
                logging.info(f"Database Connection Time: {time_delta}")
                return True
            else:
                logging.error(f"Unable to open MySQL interface.")
                SQL.disconnectMySQL(tunnel=self._tunnel, db=self._db)
                return False
        else:
            return True

    def _close(self) -> bool:
        if SQL is not None:
            SQL.disconnectMySQL(tunnel=self._tunnel, db=self._db)
            logging.debug("Closed connection to MySQL.")
            self._is_open = False
        return True

    # *** PUBLIC STATICS ***

    # Check if we can connect to MySQL with the given config settings and raise SystemExit
    @staticmethod
    def TestConnection(settings:Dict[str,Any]) -> None:
        
        logging.info("Testing connection to MySQL")
        mysqlInterface = MySQLInterface(settings)

        # If connection was successful
        if not mysqlInterface._is_open:
            logging.error("MySQL connection unsuccessful")
            sys.exit(1)

        logging.info("MySQL connection successful")
        sys.exit(0)

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***