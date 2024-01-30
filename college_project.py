import getpass
import cv2
from pyzbar.pyzbar import decode
import mysql.connector
from mysql.connector import Error
from tabulate import tabulate
import datetime
import configparser
import pandas as pd
from tkinter import Tk, filedialog
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

def finish_with_error(con):
    print(con.msg)
    exit(1)

def read_config():
    # Read the configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Access values using section and key
    return {
        'host': config['Database']['host'],
        'user': config['Database']['user'],
        'password': config['Database']['password'],
        'database': config['Database']['database']
    }

def create_database(con):
    cursor = con.cursor()
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS student_attendance")
    except Error as e:
        finish_with_error(e)
    finally:
        cursor.close()

def create_table(con):
    cursor = con.cursor()
    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS students (roll_no INT PRIMARY KEY, name VARCHAR(255), room_no INT, contact_no VARCHAR(15), days_present INT)")
    except Error as e:
        finish_with_error(e)
    finally:
        cursor.close()

def add_student(con, student_details):
    name = student_details[0]
    roll_no = student_details[1]
    room_no = student_details[2]
    contact_no = student_details[3]

    insert_query = f"INSERT INTO students VALUES ({roll_no}, '{name}', {room_no}, '{contact_no}', 0)"
    cursor = con.cursor()
    try:
        cursor.execute(insert_query)
        con.commit()
        msg = CTkMessagebox(title="NIT DELHI", message="Student Added ",icon="check", option_1="okay")
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:  # Error number for "Duplicate entry"
             msg = CTkMessagebox(title="Warning Message!", message=f"Student with Roll number {roll_no} already exists.",icon="warning", option_1="Retry", option_2="close")
        else:
            con.rollback()
            finish_with_error(e)
    finally:
        cursor.close()

def show_all_data(con):
    now = datetime.datetime.now()
    table_name = f"ab{now.year}_{now.month}_{now.day}"
    select_query = f"SELECT * FROM {table_name}"

    cursor = con.cursor()
    try:
        cursor.execute(select_query)
        rows = cursor.fetchall()

        return rows
    except mysql.connector.Error as e:
        if e.errno == 1146:  # Error number for "Table doesn't exist"
            print(f"Table doesn't exist. Returning to menu.")
        else:
            finish_with_error(e)
    finally:
        cursor.close()

def read_qr_code():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        qr_codes = decode(gray)
        cv2.imshow('Press Any Key To Exit', frame)

        if qr_codes:
            qr_data = qr_codes[0].data.decode('utf-8')
            cap.release()
            cv2.destroyAllWindows()
            return qr_data

        key = cv2.waitKey(1)

        # Check if any key is pressed to break the loop
        if key != -1:
            break

    cap.release()
    cv2.destroyAllWindows()

def take_attendance(con):
    now = datetime.datetime.now()

    # Read QR code to get the student's roll number
    qr_data = read_qr_code()
    if qr_data is None:
        print("QR code scanning canceled.")
        return
    roll_no = int(qr_data)
        

    # Check if the student with the given roll number exists
    check_student_query = f"SELECT * FROM students WHERE roll_no = {roll_no}"

    cursor = con.cursor()
    try:
        cursor.execute(check_student_query)
        student_exists = cursor.fetchone()

        if not student_exists:
            print(f"Student with Roll number {roll_no} does not exist.")
            return

        table_name = f"ab{now.year}_{now.month}_{now.day}"
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (s_no INT PRIMARY KEY, roll_no INT, name VARCHAR(255), room_no INT, contact_no VARCHAR(15), time_out TIME, time_in TIME)"
        select_count_query = f"SELECT COUNT(*) FROM {table_name}"
        select_student_query = f"SELECT * FROM students WHERE roll_no = {roll_no}"
        select_attendance_query = f"SELECT * FROM {table_name} WHERE roll_no = {roll_no}"

        cursor.execute(create_table_query)
        cursor.execute(select_count_query)
        days = cursor.fetchone()[0] + 1

        cursor.execute(select_student_query)
        student_row = cursor.fetchone()

        cursor.execute(select_attendance_query)
        attendance_rows = cursor.fetchall()

        if not attendance_rows:
            time_out = now.strftime("%H:%M:%S")
            insert_query = f"INSERT INTO {table_name} VALUES ({days}, {roll_no}, '{student_row[1]}', {student_row[2]}, '{student_row[3]}', '{time_out}', NULL)"
            cursor.execute(insert_query)
            con.commit()
            return

        for attendance_row in attendance_rows:
            if attendance_row[6] is None:
                time_in = now.strftime("%H:%M:%S")
                update_query = f"UPDATE {table_name} SET time_in = '{time_in}' WHERE roll_no = {roll_no}"
                cursor.execute(update_query)
                con.commit()
                return

        time_out = now.strftime("%H:%M:%S")
        insert_query = f"INSERT INTO {table_name} VALUES ({days}, {roll_no}, '{student_row[1]}', {student_row[2]}, '{student_row[3]}', '{time_out}', NULL)"
        cursor.execute(insert_query)
        con.commit()
    except Error as e:
        finish_with_error(e)
    finally:
        cursor.close()
        take_attendance(con)
        

def delete_student(con, roll_no):
    check_student_query = f"SELECT * FROM students WHERE roll_no = {roll_no}"
    cursor = con.cursor()
    try:
        cursor.execute(check_student_query)
        student_exists = cursor.fetchone()
        if not student_exists:
            msg = CTkMessagebox(title="NIT DELHI", message=f"No student with Roll number {roll_no} exists.",icon="warning")
            return

        delete_query = f"DELETE FROM students WHERE roll_no = {roll_no}"
        cursor.execute(delete_query)
        con.commit()
        print(f"Student with Roll number {roll_no} deleted.")

    except Error as e:
        con.rollback()
        finish_with_error(e)
    finally:
        cursor.close()

        # Only print "Student has been deleted" if the student existed
        if student_exists:
            msg = CTkMessagebox(title="NIT DELHI", message="Student Deleted",icon="check")

def show_all_students(con):
    select_query = "SELECT * FROM students"

    cursor = con.cursor()
    try:
        cursor.execute(select_query)
        rows = cursor.fetchall()
        return rows


    except Error as e:
        finish_with_error(e)
    finally:
        cursor.close()

def export_students_to_excel(con):
    # Retrieve all students from the database
    select_query = "SELECT * FROM students"
    cursor = con.cursor()

    try:
        cursor.execute(select_query)
        rows = cursor.fetchall()

        if not rows:
            print("No student data available.")
            return

        # Create a DataFrame
        columns = ["Roll_no", "Name", "Room_no", "Contact_no", "Days_Present"]
        data = [(row[0], row[1], row[2], row[3], row[4]) for row in rows]
        df = pd.DataFrame(data, columns=columns)

        # Create Tkinter root window
        root = Tk()
        root.focus_force()
        root.withdraw()

        # Ask user for the file name using a file dialog
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

        if not file_path:
            print("Export canceled.")
            return

        # Save DataFrame to Excel
        df.to_excel(file_path, index=False)

        msg = CTkMessagebox(title="NIT DELHI", message=f"Student data exported to {file_path}",icon="check")
        #print(f"Student data exported to {file_path}")
        
    except Exception as e:
        msg = CTkMessagebox(title="NIT DELHI", message=f"Error exporting student data: {e}",icon="warning")

        #print(f"Error exporting student data: {e}")
    finally:
        cursor.close()

def list_students_not_returned(con):
    # Get the current date and time
    now = datetime.datetime.now()

    # Create a timestamp for 9:30 PM on the current date
    deadline_time = datetime.datetime(now.year, now.month, now.day, 21, 30, 0)

    # Check if it's past the deadline
    if now >= deadline_time:
        # Display students who haven't returned
        table_name = f"ab{now.year}_{now.month}_{now.day}"
        select_query = f"SELECT * FROM {table_name} WHERE time_in IS NULL"

        cursor = con.cursor()
        try:
            cursor.execute(select_query)
            rows = cursor.fetchall()

            headers = ("S.no", "Roll_no", "Name", "Room No", "Contact No", "Time out", "Time in")
            rows.insert(0, headers)

            return rows
        except mysql.connector.Error as e:
            if e.errno == 1146:  # Error number for "Table doesn't exist"
                msg = CTkMessagebox(title="Warning Message!", message="Table doesn't exist",icon="warning")
            else:
                finish_with_error(e)
        finally:
            cursor.close()
    else:
        msg = CTkMessagebox(title="Warning Message!", message="It's not yet 9:30 PM. No students to display.",icon="warning")

def main():
    try:
        config = read_config()
        con = mysql.connector.connect(**config)
        if con.is_connected():
            print("Connected to MySQL server")

            create_database(con)
            con.database = config['database']
            create_table(con)

            ans = 'y'
            while ans == 'y':
                print("\n\t[Menu]\n1. Take Attendance\n2. Show Today's Attendance\n3. Add Student\n4. Delete Student\n5. Show Students List\n6. Export All Student List\n7. Exit")
                m = int(input("What Would You Like To Do: "))

                if m == 1:
                    take_attendance(con)
                elif m == 2:
                    password = get_password()
                    table_data= show_all_data(con, password)
                    print(table_data)
                elif m == 3:
                    password = get_password()
                    add_student(con, password)

                elif m == 4:
                    password = get_password()
                    delete_student(con, password)
                elif m == 5:
                    password = get_password()
                    show_all_students(con, password)
                elif m==6:
                    password = get_password()
                    export_students_to_excel(con, password)
                elif m == 7:
                    break

        else:
            print("Connection failed")

    except Error as e:
        finish_with_error(e)
    finally:
        if con.is_connected():
            con.close()

if __name__ == "__main__":
    main()
