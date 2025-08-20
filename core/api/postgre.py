import psycopg2 as postgre


class PostgreSQLDatabase:

    async def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the PostgreSQLDatabase instance:

        :param connect: Connection parameters for the PostgreSQL database.
        :type connect: dict

        - *dbname*: Name of the database to connect to.
        - *user*: Username to authenticate with.
        - *password*: Password for the user.
        - *host*: Hostname of the database server.
        - *port*: Port number of the database server.

        """
        self.connect: dict = {
            "dbname": kwargs.get("dbname"),
            "user": kwargs.get("user"),
            "password": kwargs.get("password"),
            "host": kwargs.get("host"),
            "port": kwargs.get("port"),
        }

    async def connect(self) -> None:
        """
        Connect to PostgreSQL server
        """
        self.connection = await postgre.connect(dbname=self.connect.get('dbname'),
                                           user=self.connect.get('user'),
                                           password=self.connect.get('password'),
                                           host=self.connect.get('host'),
                                           port=self.connect.get('port'), async_=True)
        self.cursor = await self.connection.cursor()

    async def execute(self, **data: dict) -> list[tuple] | None:
        """
        Execute a query on the PostgreSQL database.

        :param data: The SQL query to execute.
        :type data: dict

        - *query*: The SQL query to execute.
        - *params*: The parameters to include in the query.
        - *method*: The HTTP method to use for the request.

        """

        await self.cursor.execute(data.get("query"), data.get("params", ""))
        if data.get("method") == "GET":
            return await self.cursor.fetchall()
        if data.get("method") in ("PATCH", "POST", "PUT"):
            await self.connection.commit()

    async def disconnect(self) -> None:
        """
        Disconnect from PostgreSQL server
        """
        await self.cursor.close()
        await self.connection.close()
