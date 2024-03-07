from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    """
    TODO: Part 1
    """
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return
    
    username = tokens[1]
    password = tokens[2]

    #check if username is unique.
    if username_exists_patient(username):
        print("Username taken, try again")
        return

    #check password strength
    if password_strength(password) is False:
        print("Create patient failed")
        return
    
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    #save patient info to database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Create patient failed")
        print(e)
        return
    print("Created user ", username)

def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return
    
    #check password strength
    if password_strength(password) is False:
        print("Create user failed")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    """
    TODO: Part 1
    """
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in, try again")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login patient failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login patient failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login patient failed.")
    else:
        print("Logged in as " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver

#FINISH LATER
def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    """
    global current_caregiver
    global current_patient
    #check if user is logged in
    if current_patient is None and current_caregiver is None:
        print("Please login first:")
        return
    
    #token check
    if len(tokens) != 2:
        print("Please try again")
        return
    
    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    d = datetime.datetime(year, month, day)
    search_schedule = "SELECT C.Username FROM Caregivers as C, Availabilities as A WHERE A.Username = C.Username AND Time = %s ORDER BY C.Username"
    check_doses = "SELECT * FROM Vaccines ORDER BY Vaccines.Name"

    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        cursor.execute(search_schedule, (d))
        results = cursor.fetchall()
        for result in results:
            print(result[0])
        conn.commit()
    except pymssql.Error as e:
        print("Please try again")
        print(e)
        return
    except ValueError as e:
        #error for inputting improperly formated date
        print("Please try again")
        print(e)
        return
    except Exception as e:
        print("Please try again")
        print("Error:", e)
        return
    finally:
        cm.close_connection()
    
    #check vaccines
    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        cursor.execute(check_doses)
        results = cursor.fetchall()
        for result in results:
            print(f"{result[0]} {result[1]}")
        conn.commit()
    except pymssql.Error as e:
        print("Please try again")
        return
    except Exception as e:
        print("Please try again")
        print("Error:", e)
        return
    finally:
        cm.close_connection()
    return








def reserve(tokens):
    """
    TODO: Part 2
    """
    global current_patient
    if current_patient is None and current_caregiver is None:
        print("Please login first")
        return
    if current_patient is None and current_caregiver is not None:
        print("Please login as a patient")
        return
    
    #token check
    if len(tokens) != 3:
        print("Please try again")
        return
    
    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    d = datetime.datetime(year, month, day)

    vaccine_name = tokens[2]

    #check availability
    available_caregiver = "SELECT A.Username FROM Availabilities AS A WHERE Time = %s ORDER BY A.Username"
    caregiver_username = None

    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        cursor.execute(available_caregiver, (d))
        caregiver_username = cursor.fetchone()
    except pymssql.Error as e:
        print("Please try again")
        print(e)
        return
    except Exception as e:
        print("Please try again")
        print(e)
        return
    finally:
        cm.close_connection()
    if caregiver_username is None:
        print("No caregiver is avaiable")
        return
    
    #check vaccine doses
    get_doses = "SELECT V.doses FROM Vaccines AS V WHERE V.Name = %s"
    vaccine_doses = None

    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        cursor.execute(get_doses, (vaccine_name))
        result = cursor.fetchone()
        if result is not None:
            vaccine_doses = result[0]
        else:
            vaccine_doses = 0
    except pymssql.Error as e:
        print("Please try again")
        print(e)
        return
    except Exception as e:
        print("Please try again")
        print(e)
        return
    finally:
        cm.close_connection()
    if vaccine_doses == 0:
        print("Not enough available doses")
        return
    
    #generate appointment ID
    get_last_appt_id = "SELECT MAX(appointment_id) FROM Appointments"
    last_appt_id = None
    appt_id = None

    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        cursor.execute(get_last_appt_id)
        result = cursor.fetchone()
        last_appt_id = result[0] if result else None
        if last_appt_id == None:
            appt_id = 1
        else:
            appt_id = last_appt_id + 1
    except pymssql.Error as e:
        print("Please try again")
        print(e)
        return
    except Exception as e:
        print("Please try again")
        print(e)
        return
    finally:
        cm.close_connection()
    if appt_id is None:
        print("Please try again")
        return

    #update apptointment database
    update_appts = "INSERT INTO Appointments VALUES (%s, %s, %s, %s, %s)"

    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        cursor.execute(update_appts, (appt_id, vaccine_name, d, current_patient.username, caregiver_username))
        conn.commit()
    except pymssql.Error as e:
        print("Please try again")
        print(e)
        return
    except Exception as e:
        print("Please try again")
        print(e)
        return
    finally:
        cm.close_connection()

    #update availablility
    update_available = "DELETE FROM Availabilities WHERE Username = %s AND Time = %s"

    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        cursor.execute(update_available, (caregiver_username[0], d))
        conn.commit()
    except pymssql.Error as e:
        print("Please try again")
        print(e)
        return
    except Exception as e:
        print("Please try again")
        print(e)
        return
    finally:
        cm.close_connection()

    #update vaccine doses
    vaccine = Vaccine(vaccine_name, vaccine_doses)

    try:
        vaccine.decrease_available_doses(1)
    except pymssql.Error as e:
        print("Please try again")
        print(e)
        return
    except Exception as e:
        print("Please try again")
        print(e)
        return
    finally:
        cm.close_connection()

    print(f"Appointment ID {appt_id}, Caregiver username {caregiver_username[0]}")


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    <appointment_id>
    """
    global current_caregiver
    global current_patient
    if current_patient is None and current_caregiver is None:
        print("Please login first")
        return

    #token check
    if len(tokens) != 2:
        print("Please try again")
        return
    
    appt_id = tokens[1]

    get_appt_info = "SELECT vac_name, Time, caregiver_name FROM Appointments WHERE appointment_id = %s"
    delete_appt = "DELETE FROM Appointments WHERE appointment_id = %s"
    add_availability = "INSERT INTO Availabilities VALUES (%s, %s)"


    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        #get appt info
        cursor.execute(get_appt_info, (appt_id))
        appt_info = cursor.fetchone()
        if not appt_info:
            print("Appointment does not exist.")
            return

        #delete appointment
        cursor.execute(delete_appt, (appt_id))
        conn.commit()

        #update vaccine doses
        vaccine = Vaccine(appt_info['vac_name'], 0)
        vaccine = vaccine.get()
        if vaccine:
            vaccine.increase_available_doses(1)

        #update caregiver availability
        cursor.execute(add_availability, (appt_info['Time'], appt_info['caregiver_name']))
        conn.commit()

        print(f"Appointment {appt_id} successfully canceled")

    except pymssql.Error as e:
        print("Please try again")
        return
    except Exception as e:
        print("Please try again")
        print("Error:", e)
        return
    finally:
        cm.close_connection()

    return

    



def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    global current_caregiver
    global current_patient
    #check if user is logged in
    if current_patient is None and current_caregiver is None:
        print("Please login first:")
        return
    

    #  check 2: the length for tokens need to be exactly 1 to include all information (with the operation name)
    if len(tokens) != 1:
        print("Please try again!")
        return
    
    if current_patient is not None:
        get_appt_info = "SELECT appointment_id, vac_name, Time, caregiver_name FROM Appointments WHERE patient_name = %s ORDER BY appointment_id"

        try:
            cm = ConnectionManager()
            conn = cm.create_connection()
            cursor = conn.cursor()

            cursor.execute(get_appt_info, (current_patient.username))
            results = cursor.fetchall()
            if not results:
                print("You have no appointments scheduled")
                return

            for result in results:
                appt_id, vax_name, time, caregiver_name = result
                print(f"{appt_id} {vax_name} {time.strftime('%m-%d-%Y')} {caregiver_name}")
            

        except pymssql.Error as e:
            print("Please try again")
            print(e)
            return
        except Exception as e:
            print("Please try again")
            print(e)
            return
        finally:
            cm.close_connection()
        
        return
    
    else:
        get_appt_info = "SELECT appointment_id, vac_name, Time, patient_name FROM Appointments WHERE caregiver_name = %s ORDER BY appointment_id"


        try:
            cm = ConnectionManager()
            conn = cm.create_connection()
            cursor = conn.cursor()

            cursor.execute(get_appt_info, (current_caregiver.username))
            results = cursor.fetchall()
            if not results:
                print("You have no appointments scheduled")
                return

            for result in results:
                appt_id, vax_name, time, patient_name = result
                print(f"{appt_id} {vax_name} {time.strftime('%m-%d-%Y')} {patient_name}")

        except pymssql.Error as e:
            print("Please try again")
            print(e)
            return
        except Exception as e:
            print("Please try again")
            print(e)
            return
        finally:
            cm.close_connection()
        
        return


def logout(tokens):
    """
    TODO: Part 2
    """
    # see if someone is logged in
    global current_caregiver
    global current_patient

    #  check 2: the length for tokens need to be exactly 1 to include all information (with the operation name)
    if len(tokens) != 1:
        print("Please try again!")
        return

    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return
    if len(tokens) != 1:
        print("Please try again")
        return
    else:
        current_caregiver = None
        current_patient = None
        print("Successfully logged out")
        return
    

def password_strength(password):
    if len(password) < 8:
        print("Password must be 8 characters or greater.")
        return False
    if not any(char.isupper() for char in password) or not any(char.islower() for char in password):
        print("Password must contain uppercase and lowercase letters.")
        return False
    if not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
        print("Password must contain letters and numbers.")
        return False
    special_chars = "!@#?"
    if not any(char in special_chars for char in password):
        print("Password must contain !, @, #, or ?")
        return False
    
    return True





def display_menu():
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")
    print("> reserve <date> <vaccine>")
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")
    print("> logout")
    print("> Quit")
    print()


def start():
    stop = False

    while not stop:
        display_menu()
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
