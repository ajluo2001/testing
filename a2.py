"""
# This code is provided solely for the personal and private use of students 
# taking the CSC343H course at the University of Toronto. Copying for purposes 
# other than this use is expressly prohibited. All forms of distribution of 
# this code, including but not limited to public repositories on GitHub, 
# GitLab, Bitbucket, or any other online platform, whether as given or with 
# any changes, are expressly prohibited. 
"""

from typing import Optional
import psycopg2 as pg
import datetime
import math

class Assignment2:

    ##### DO NOT MODIFY THE CODE BELOW. #####

    def __init__(self) -> None:
        """Initialize this class, with no database connection yet.
        """
        self.db_conn = None

    
    def connect_db(self, url: str, username: str, pword: str) -> bool:
        """Connect to the database at url and for username, and set the
        search_path to "air_travel". Return True iff the connection was made
        successfully.

        >>> a2 = Assignment2()
        >>> # This example will make sense if you change the arguments as
        >>> # appropriate for you.
        >>> a2.connect_db("csc343h-<your_username>", "<your_username>", "")
        True
        >>> a2.connect_db("test", "postgres", "password") # test doesn't exist
        False
        """
        try:
            self.db_conn = pg.connect(dbname=url, user=username, password=pword,
                                      options="-c search_path=air_travel")
        except pg.Error:
            return False

        return True

    def disconnect_db(self) -> bool:
        """Return True iff the connection to the database was closed
        successfully.

        >>> a2 = Assignment2()
        >>> # This example will make sense if you change the arguments as
        >>> # appropriate for you.
        >>> a2.connect_db("csc343h-<your_username>", "<your_username>", "")
        True
        >>> a2.disconnect_db()
        True
        """
        try:
            self.db_conn.close()
        except pg.Error:
            return False

        return True

    ##### DO NOT MODIFY THE CODE ABOVE. #####

    # ----------------------- Airline-related methods ------------------------- */

    def book_seat(self, pass_id: int, flight_id: int, seat_class: str) -> Optional[bool]:
        """Attempts to book a flight for a passenger in a particular seat class. 
        Does so by inserting a row into the Booking table.
        
        Read the handout for information on how seats are booked.

        Parameters:
        * pass_id - id of the passenger
        * flight_id - id of the flight
        * seat_class - the class of the seat

        Precondition:
        * seat_class is one of "economy", "business", or "first".
        
        Return: 
        * True iff the booking was successful.
        * False iff the seat can't be booked, or if the passenger or flight cannot be found.
        """
        try:
            cur = self.db_conn.cursor()

            #we want to first see if the flight_id or pass_id exists, it not, return False
            
            cur.execute(("SELECT count(*) FROM flight WHERE id = %s"), (flight_id,))
            for row in cur:
                if row[0] == 0:
                    return False
            
            cur.execute(("SELECT count(*) FROM passenger WHERE id = %s"), (pass_id,))
            for row in cur:
                if row[0] == 0:
                    return False
        
            #we want to start off by getting the capacities of economy, business, and first class for the
            #specific flight that the passenger wants to book

            cur.execute(("SELECT capacity_economy, capacity_business, capacity_first FROM flight JOIN plane ON plane = tail_number WHERE flight.id = %s"), (flight_id,))
            capacity_economy = 0
            capacity_business = 0
            capacity_first = 0
            for row in cur:
                capacity_economy = row[0]
                capacity_business = row[1]
                capacity_first = row[2]



            #get prices of economy, business, and first class from the flight
            cur.execute(("SELECT economy, business, first FROM price WHERE flight_id = %s"), (flight_id,))
            price_economy = 0
            price_business = 0
            price_first = 0
            for row in cur:
                price_economy = row[0]
                price_business = row[1]
                price_first = row[2]

            
            #these are used to keep track of the "largest" seat row and letter so far that we encounter in the first class, business, and economy
            largest_seat_row_first = 1
            largest_seat_letter_first = "A"
            
            starting_business_row = math.ceil(capacity_first/6) + 1

            largest_seat_row_business = starting_business_row
            largest_seat_letter_business = "A"

            starting_economy_row = math.ceil(capacity_business/6) + starting_business_row

            largest_seat_row_economy = starting_economy_row
            largest_starting_letter_economy = "A"
            

            #get max booking id and add 1 to it so its unique
            bookings_id = 1
            cur.execute("SELECT max(id) FROM booking;")
            for row in cur:
                bookings_id = row[0] + 1
            
            
            cur.execute(("SELECT * FROM booking WHERE flight_id = %s"), (flight_id,))

            total = 0 #this is the total number of the seats that are so far in the class
            for row in cur:
                if row[5] == seat_class:
                    total += 1
            
            if seat_class == "first":
                if total >= capacity_first:
                    return False
                
                else:
                    booking_date = self._get_current_timestamp()
                    cur.execute(("SELECT * FROM booking WHERE seat_class = 'first' and flight_id = %s"), (flight_id,))
                    for row in cur:
                        if row[6] > largest_seat_row_first or (row[6] == largest_seat_row_first and row[7] > largest_seat_letter_first):
                            largest_seat_row_first = row[6]
                            largest_seat_letter_first = row[7]
                    if largest_seat_letter_first == 'F':
                        cur.execute("INSERT INTO booking VALUES (%s, %s, %s, %s, %s, %s, %s, 'A')", (bookings_id, pass_id, flight_id, booking_date, price_first, seat_class, 
                        largest_seat_row_first + 1))
                        self.db_conn.commit()
                        return True

                    elif total == 0:
                        cur.execute("INSERT INTO booking VALUES (%s, %s, %s, %s, %s, %s, %s, 'A')", (bookings_id, pass_id, flight_id, booking_date, price_first, seat_class, 
                        largest_seat_row_first))
                        self.db_conn.commit()
                        return True

                    else:
                        #insert into same row, one letter above
                        next_letter = chr(ord(largest_seat_letter_first) + 1)
                        cur.execute("INSERT INTO booking VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (bookings_id, pass_id, flight_id, booking_date, price_first,
                        seat_class, largest_seat_row_first, next_letter))
                        self.db_conn.commit()
                        return True
            
            if seat_class == "business":
                if total >= capacity_business:
                    return False
                
                else:
                    booking_date = self._get_current_timestamp()
                    cur.execute(("SELECT * FROM booking WHERE seat_class = 'business' and flight_id = %s"), (flight_id,))
                    for row in cur:
                        if row[6] > largest_seat_row_business or (row[6] == largest_seat_row_business and row[7] > largest_seat_letter_business):
                            largest_seat_row_business = row[6]
                            largest_seat_letter_business = row[7]
                    if largest_seat_letter_business == 'F':
                        cur.execute("INSERT INTO booking VALUES (%s, %s, %s, %s, %s, %s, %s, 'A')", (bookings_id, pass_id, flight_id, booking_date, price_business, seat_class, 
                        largest_seat_row_business + 1))
                        self.db_conn.commit()
                        return True
                    
                    elif total == 0:
                        cur.execute("INSERT INTO booking VALUES (%s, %s, %s, %s, %s, %s, %s, 'A')", (bookings_id, pass_id, flight_id, booking_date, price_first, seat_class, 
                        largest_seat_row_business))
                        self.db_conn.commit()
                        return True

                    else:
                        #insert into same row, one letter above
                        next_letter = chr(ord(largest_seat_letter_business) + 1)
                        cur.execute("INSERT INTO booking VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (bookings_id, pass_id, flight_id, booking_date, price_business,
                        seat_class, largest_seat_row_business, next_letter))
                        self.db_conn.commit()
                        return True


            if seat_class == "economy":
                if total >= (capacity_economy + 10):
                    return False

                elif (capacity_economy + 10) > total >= capacity_economy:
                    booking_date = self._get_current_timestamp()
                    cur.execute("INSERT INTO booking VALUES (%s, %s, %s, %s, %s, %s, NULL, NULL)", (bookings_id, pass_id, flight_id, booking_date, price_economy, seat_class))
                    self.db_conn.commit()
                    return True

                elif capacity_economy > total:
                    booking_date = self._get_current_timestamp()
                    cur.execute(("SELECT * FROM booking WHERE seat_class = 'economy' and flight_id = %s"), (flight_id,))
                    for row in cur:
                        if row[6] > largest_seat_row_economy or (row[6] == largest_seat_row_economy and row[7] > largest_starting_letter_economy):
                            largest_seat_row_economy = row[6]
                            largest_starting_letter_economy = row[7]
                    if largest_starting_letter_economy == 'F':
                        cur.execute("INSERT INTO booking VALUES (%s, %s, %s, %s, %s, %s, %s, 'A')", (bookings_id, pass_id, flight_id, booking_date, price_economy, seat_class, 
                        largest_seat_row_economy + 1))
                        self.db_conn.commit()
                        return True
                    
                    elif total == 0:
                        cur.execute("INSERT INTO booking VALUES (%s, %s, %s, %s, %s, %s, %s, 'A')", (bookings_id, pass_id, flight_id, booking_date, price_first, seat_class, 
                        largest_seat_row_economy))
                        self.db_conn.commit()
                        return True

                    else:
                        #insert into same row, one letter above
                        next_letter = chr(ord(largest_starting_letter_economy) + 1)
                        cur.execute("INSERT INTO booking VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (bookings_id, pass_id, flight_id, booking_date, price_economy,
                        seat_class, largest_seat_row_economy, next_letter))
                        self.db_conn.commit()
                        return True
            return False

        except pg.Error:
            return None


    def upgrade(self, flight_id: int) -> Optional[int]:
        """Attempts to upgrade overbooked economy passengers to business class
        or first class (in that order until each seat class is filled).
        Does so by altering the database records for the bookings such that the
        seat and seat_class are updated if an upgrade can be processed.
        
        Upgrades should happen in order of earliest booking timestamp first.
        If economy passengers are left over without a seat (i.e. not enough higher class seats), 
        remove their bookings from the database.
        
        Parameters:
        * flight_id - the flight to upgrade passengers in
        
        Precondition: 
        * flight_id exists in the database (a valid flight id).
        
        Return: 
        * The number of passengers upgraded.
        """
        try:
            cur = self.db_conn.cursor()
            
            #Find if seats are available in business or first class
            
            #First find the capacity of first class and economy for the flight
            cur.execute(("SELECT capacity_business, capacity_first FROM flight JOIN plane ON plane = tail_number WHERE flight.id = %s"), (flight_id,))
            capacity_business = 0
            capacity_first = 0
            for row in cur:
                capacity_business = row[0]
                capacity_first = row[1]
            
            cur.execute(("SELECT seat_class, count(*) FROM booking WHERE flight_id = %s GROUP BY seat_class"), (flight_id,))
            
            taken_business = 0
            taken_first = 0

            for row in cur:
                if row[0] == "business":
                    taken_business = row[1]
                elif row[0] == "first":
                    taken_first = row[1]
                
            #Find the "largest" available spot
            largest_seat_row_first = 1
            largest_seat_letter_first = "A"
            
            starting_business_row = math.ceil(capacity_first/6) + 1

            largest_seat_row_business = starting_business_row
            largest_seat_letter_business = "A"
            
            cur.execute(("SELECT * FROM booking WHERE flight_id = %s"), (flight_id,))
            for row in cur:
                if row[5] == "business":
                    if row[6] > largest_seat_row_business or (row[6] == largest_seat_row_business and row[7] > largest_seat_letter_business):
                        largest_seat_row_business = row[6]
                        largest_seat_letter_business = row[7]

                if row[5] == "first":
                    if row[6] > largest_seat_row_first or (row[6] == largest_seat_row_first and row[7] > largest_seat_letter_first):
                        largest_seat_row_first = row[6]
                        largest_seat_letter_first = row[7]


            taken_business = 0
            taken_first = 0

            for row in cur:
                if row[0] == "business":
                    taken_business = row[1]
                elif row[0] == "first":
                    taken_first = row[1]

            total_booked = 0
            to_delete = []
            to_change = []
            cur.execute(("SELECT * FROM booking WHERE flight_id = %s"), (flight_id,))
            for row in cur:
                if row[6] is None and row[7] is None:
                    if taken_first >= capacity_first and taken_business < capacity_business:
                        if largest_seat_letter_business == "F":
                            largest_seat_row_business += 1
                            change = [row[0], "business", "A", largest_seat_row_business]
                            to_change.append(change)
                            total_booked += 1
                            largest_seat_letter_business = "A"
                            taken_business += 1
                        elif taken_business == 0:
                            change = [row[0], "business", "A", largest_seat_row_business]
                            to_change.append(change)
                            total_booked += 1
                            taken_business += 1
                        else:
                            largest_seat_letter_business = chr(ord(largest_seat_letter_business) + 1)
                            change = [row[0], "business", largest_seat_letter_business, largest_seat_row_business]
                            to_change.append(change)
                            total_booked += 1
                            taken_business += 1


                    elif taken_first < capacity_first and taken_business >= capacity_business:
                        if largest_seat_letter_first == "F":
                            largest_seat_row_first += 1
                            change = [row[0], "first", "A", largest_seat_row_first]
                            to_change.append(change)
                            total_booked += 1
                            largest_seat_letter_first = "A"
                            taken_first += 1
                        elif taken_first == 0:
                            change = [row[0], "first", "A", largest_seat_row_first]
                            to_change.append(change)
                            total_booked += 1
                            taken_first += 1

                        else:
                            largest_seat_letter_first = chr(ord(largest_seat_letter_first) + 1)
                            change = [row[0], "first", largest_seat_letter_first, largest_seat_row_first]
                            to_change.append(change)
                            total_booked += 1
                            taken_first += 1
                    
                    elif taken_first < capacity_first and taken_business < capacity_business:
                        next_row = largest_seat_row_business
                        next_letter = "A"
                        if largest_seat_letter_business == "F":
                            largest_seat_row_business += 1
                            change = [row[0], "business", "A", largest_seat_row_business]
                            to_change.append(change)
                            total_booked += 1
                            largest_seat_letter_business = "A"
                            taken_business += 1
                        elif taken_business == 0:
                            change = [row[0], "business", "A", largest_seat_row_business]
                            to_change.append(change)
                            total_booked += 1
                            taken_business += 1
                        else:
                            largest_seat_letter_business = chr(ord(largest_seat_letter_business) + 1)
                            change = [row[0], "business", largest_seat_letter_business, largest_seat_row_business]
                            to_change.append(change)
                            total_booked += 1
                            taken_business += 1
                    
                    else:
                        to_delete.append(row[0])
            
            for changes in to_change:
                cur.execute("UPDATE booking SET seat_class = %s, row = %s, letter = %s WHERE id = %s", (changes[1], changes[3], changes[2], changes[0]))
                self.db_conn.commit()
            
            for flight in to_delete:
                cur.execute("DELETE FROM booking WHERE id = %s", (flight,))
                self.db_conn.commit()
            

            return total_booked

        except pg.Error:
            return None


# ----------------------- Helper methods below  ------------------------- */
    

    # A helpful method for adding a timestamp to new bookings.
    def _get_current_timestamp(self):
        """Return a datetime object of the current time, formatted as required
        in our database.
        """
        return datetime.datetime.now().replace(microsecond=0)

   
    ## Add more helper methods below if desired.



# ----------------------- Testing code below  ------------------------- */

def sample_testing_function() -> None:
    a2 = Assignment2()
    # TODO: Change this to connect to your own database:
    print(a2.connect_db("csc343h-luoalbe1", "luoalbe1", ""))
    print(a2.book_seat(1, 1, 'economy'))
   
    a2.disconnect_db()


## You can put testing code in here. It will not affect our autotester.
if __name__ == '__main__':
    # TODO: Put your testing code here, or call testing functions such as
    # this one:
    sample_testing_function()




