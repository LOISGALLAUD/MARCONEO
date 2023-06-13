"""
dbcursor.py

Defines the DBCursor class and everything
related to the connexion to the database.
"""

#-------------------------------------------------------------------#

import decimal
import mysql.connector as mysql

from src.utils.decorators import close_service, setup_service
from src.client.member import Member
from src.server.logins import Logins

#-------------------------------------------------------------------#

class DBCursor:
    """
    Defines the objects of type cursors that point on the MySQL database.
    It will be able to return information or modify values in the database.
    """
    def __init__(self, app) -> None:
        """
        DataBase's constructor.
        """
        self.loggers = app.loggers
        self.connection = None
        self.cursor = None
        self._logins = Logins()
        self.connect_to_db()
        self.cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

    @setup_service(max_attempts=5)
    def connect_to_db(self) -> bool:
        """
        Connects to the database.
        """
        self.connection = mysql.connect(host=self._logins.get_host(),
                                        database=self._logins.get_database(),
                                        user=self._logins.get_user(),
                                        password=self._logins.get_password(),
                                        port=self._logins.get_port())
        self.cursor = self.connection.cursor()
        self.loggers.log.info("Connected to the database.")
        return True

    @close_service
    def close(self) -> bool:
        """
        Ferme la session MySQL.
        """
        self.connection.close()
        self.loggers.log.debug("Disconnected from the database.")
        return True

    def get_member(self, card_id:int) -> Member:
        """
        Retrieves a user with the given ID from the database.
        Returns the user if a match is foundin the database, None otherwise
        """
        if card_id < 0:
            return None


        self.cursor.execute("""SELECT id, first_name, last_name, nickname, card_number,\
                            balance, admin, contributor
                                FROM Members
                                WHERE card_number = %s""", (card_id,))

        result = self.cursor.fetchone()

        if result is not None:
            member_data = {'id':result[0],
                            'first_name':result[1],
                            'last_name':result[2],
                            'nickname':result[3],
                            'card_number':result[4],
                            'balance':result[5],
                            'admin':result[6],
                            'contributor':result[7]}
            self.loggers.log.debug(f"Retrieving member {member_data['first_name']} (ID:{card_id})")
            return member_data
        self.loggers.log.warn(f"No member found with card ID {card_id}")

    def update_balance(self, member:Member) -> None:
        """
        Updates the balance of the given member in the database.
        """
        if member is None:
            return

        self.cursor.execute("""UPDATE Members
                            SET balance = %s
                            WHERE id = %s""", (member.balance, member.member_id))
        self.connection.commit()

        self.loggers.log.debug(f"Member {member.first_name} (ID:{member.card_id}) Balance: {member.balance}")

    def send_order(self, product_id:int=None, member_id:int=None,
                     price:decimal.Decimal=None, amount:int=None) -> None:
        """
        Sends a command to the database.
        """
        self.cursor.execute("""INSERT INTO Orders (product_id, member_id, price, amount)
                               VALUES (%s, %s, %s, %s)
                            """, (product_id, member_id, price*amount, amount))
        self.connection.commit()
        self.loggers.log.debug(f"Command sent to the database: {product_id}, {member_id}, {price}, {amount}")

    def get_history(self, member_id:int=None) -> list:
        """
        Retrieves the history of the given member, including member and product names.
        """
        self.cursor.execute("""SELECT Members.first_name AS member_first_name,
                                Products.name AS product_name,
                                Orders.price,
                                Orders.amount,
                                Orders.date
                                FROM Orders
                                INNER JOIN Members ON Orders.member_id = Members.id
                                INNER JOIN Products ON Orders.product_id = Products.id
                                ORDER BY Orders.date DESC
                                LIMIT 10;
                            """)
        result = self.cursor.fetchall()
        self.loggers.log.debug(f"Retrieving history of member ID {member_id}")
        return result
