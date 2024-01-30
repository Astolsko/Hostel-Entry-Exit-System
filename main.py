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
import tkinter as tk
import customtkinter as ctk
from PIL import ImageTk, Image
from CTkTable import CTkTable
from customtkinter import *
from CTkMessagebox import CTkMessagebox
from college_project import*
from win32api import GetSystemMetrics

ctk.set_appearance_mode("Dark")

global password

#app class
class Main_Page(ctk.CTk):

    global main_frame
    
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
    
    



    
    def __init__(self,*args, **kwargs):
        width = GetSystemMetrics(0)
        length = GetSystemMetrics(1)
        right_pos = length/2
        down_pos = width/2
        super().__init__(*args, **kwargs)
        self.title('Attendance Management')
        self.geometry(f"{width}x{length}".format(right_pos, down_pos))

        self.state('zoomed')

        #main frame

        main_frame = CTkFrame(master=self)
        main_frame.pack_propagate(True)
        main_frame.pack(fill= 'both', anchor = "center", side = 'right', expand= 'True', padx= 2, pady =2)

        def get_root_password():
            config = configparser.ConfigParser()
            config.read('security_config.ini')
            return config.get('Security', 'RootPassword')
        
        def set_root_password(new_password):
            config = configparser.ConfigParser()
            config.read('security_config.ini')
            config.set('Security', 'RootPassword', new_password)
            with open('security_config.ini', 'w') as configfile:
                config.write(configfile)


        def add():
            for widget in main_frame.winfo_children():
                widget.destroy()
            login_frame = CTkFrame(master = main_frame)
            login_frame.pack(expand = True, fill = 'both', padx = 27, pady = 21)
            pwd = StringVar(self,)

            display_frame = CTkFrame(master = login_frame, width = 600, height = 300)
            display_frame.place(anchor = 'center', relx = 0.5, rely = 0.5)
            
            CTkLabel(master = display_frame, text = "Enter Password",font=("Arial Bold", 20), anchor = 'center').place(relx = 0.5 , y = 100, anchor = 'center')
            CTkEntry(master = display_frame,placeholder_text = 'password please.....', textvariable=pwd, show = "*").place(relx = 0.5, y = 150, anchor = 'center')

            def verification():
                password = pwd.get()
                if password != get_root_password():
                    msg = CTkMessagebox(title="Warning Message!", message="wrong password",icon="warning", option_1="Retry")
                else:
                    button_5()
            b1 = ctk.CTkButton(master = display_frame, text = 'Submit', command = verification).place(relx = 0.5, y = 200, anchor = 'center')
            def button_5():
                for widget in main_frame.winfo_children():
                    widget.destroy()
                CTkLabel(master = main_frame, text = "Student Name : ",font=("Arial Bold", 20), anchor = 'center').place(x = 300, y = 200)
                CTkLabel(master = main_frame, text = "Roll No. : ",font=("Arial Bold", 20), anchor = 'center').place(x= 300, y = 300)
                CTkLabel(master = main_frame, text = "Room No. : ",font=("Arial Bold", 20), anchor = 'center').place(x= 300, y = 400)
                CTkLabel(master = main_frame, text = "Contact numer: ",font=("Arial Bold", 20), anchor = 'center').place(x= 300, y = 500)

                name = StringVar(self,)
                roll_no = StringVar(self, )
                room_no = StringVar(self, )
                contact = StringVar(self, )


                NameEntry = CTkEntry(master = main_frame, textvariable = name)
                NameEntry.place(y = 200, x= 500)
                RollNo = CTkEntry(master = main_frame, textvariable = roll_no)
                RollNo.place(y = 300, x= 500)
                RoomNo = CTkEntry(master = main_frame, textvariable = room_no)
                RoomNo.place(y = 400, x= 500)
                ContactNo = CTkEntry(master = main_frame, textvariable = contact)
                ContactNo.place(y = 500, x= 500)

                def button_func():
                    L=[]
                    L.append(name.get()) 
                    L.append(int(roll_no.get()))
                    L.append(int(room_no.get()))
                    L.append(int(contact.get()))
        
                    config = read_config()
                    con = mysql.connector.connect(**config)

                    add_student(con, L)

                    
                CTkButton(master = main_frame, text = "Submit", command =lambda:[button_func(),NameEntry.delete(0,END), RollNo.delete(0,END), RoomNo.delete(0,END), ContactNo.delete(0,END)]).place(x = 300, y = 600)

        def student_list():
            for widget in main_frame.winfo_children():
                widget.destroy()
            login_frame = CTkFrame(master = main_frame)
            login_frame.pack(expand = True, fill = 'both', padx = 27, pady = 21)
            pwd = StringVar(self,)

            display_frame = CTkFrame(master = login_frame, width = 600, height = 300)
            display_frame.place(anchor = 'center', relx = 0.5, rely = 0.5)
            
            CTkLabel(master = display_frame, text = "Enter Password",font=("Arial Bold", 20), anchor = 'center').place(relx = 0.5 , y = 100, anchor = 'center')
            CTkEntry(master = display_frame,placeholder_text = 'Password Please.....', textvariable=pwd, show = "*").place(relx = 0.5, y = 150, anchor = 'center')

            def verification():
                password = pwd.get()
                if password != get_root_password():
                    msg = CTkMessagebox(title="Warning Message!", message="Wrong password",icon="warning", option_1="Retry")
                else:
                    button_1()
            b1 = ctk.CTkButton(master = display_frame, text = 'Submit', command = verification).place(relx = 0.5, y = 200, anchor = 'center')

            def button_1():
                config = read_config()
                con = mysql.connector.connect(**config)
            
                select_query = "SELECT * FROM students"
                cursor = con.cursor()
                try:
                    cursor.execute(select_query)
                    rows = cursor.fetchall()
                except Error as e:
                    finish_with_error(e)
                finally:
                    cursor.close()
                tup = ('Roll No.', 'Name', 'Room No.', 'Contact', "Day's Present")
                rows.insert(0, tup)
                for widget in main_frame.winfo_children():
                    widget.destroy()
                table_frame = CTkScrollableFrame(master=main_frame)
                table_frame.pack(expand=True, fill="both", padx=27, pady=21)
                table = CTkTable(master=table_frame, values=rows, hover_color="RoyalBlue", header_color = "RoyalBlue3")
                table.edit_row(0, text_color="white", hover_color="RoyalBlue")
                table.pack(expand=True, fill = "x", pady = 50)

        def today_attendance():
            for widget in main_frame.winfo_children():
                widget.destroy()
            login_frame = CTkFrame(master = main_frame)
            login_frame.pack(expand = True, fill = 'both', padx = 27, pady = 21)
            pwd = StringVar(self,)

            display_frame = CTkFrame(master = login_frame, width = 600, height = 300)
            display_frame.place(anchor = 'center', relx = 0.5, rely = 0.5)
            
            CTkLabel(master = display_frame, text = "Enter Password",font=("Arial Bold", 20), anchor = 'center').place(relx = 0.5 , y = 100, anchor = 'center')
            CTkEntry(master = display_frame,placeholder_text = 'password please.....', textvariable=pwd, show = "*").place(relx = 0.5, y = 150, anchor = 'center')

            def verification():
                password = pwd.get()
                if password != get_root_password():
                    msg = CTkMessagebox(title="Warning Message!", message="wrong password",icon="warning", option_1="Retry")
                else:
                    button_2()
            b1 = ctk.CTkButton(master = display_frame, text = 'Submit', command = verification).place(relx = 0.5, y = 200, anchor = 'center')

            def button_2():
                config = read_config()
                con = mysql.connector.connect(**config)
                heading = ('S. No.', 'Roll No.','name', 'room number','contact','Time out', 'Time in' )
                now = datetime.datetime.now()
                table_name = f"ab{now.year}_{now.month}_{now.day}"
                select_query = f"SELECT * FROM {table_name}"

                cursor = con.cursor()
                try:
                    cursor.execute(select_query)
                    rows = cursor.fetchall()
                    data = []
                    for row in rows:
                    # Replace None values with an empty string during display
                        formatted_row = [str(item) if item is not None else "" for item in row]
                        data.append(formatted_row)
                    data.insert(0, heading )

                except mysql.connector.Error as e:
                    if e.errno == 1146:  # Error number for "Table doesn't exist"
                        msg = CTkMessagebox(title="Warning Message!", message=f"Table doesn't exist. Returning to menu.",icon="warning", option_1="Exit")
                    else:
                        finish_with_error(e)
                finally:
                    cursor.close()
                    
                for widget in main_frame.winfo_children():
                    widget.destroy()
                table_frame = CTkScrollableFrame(master=main_frame)
                table_frame.pack(expand=True, fill="both", padx=27, pady=21)
                table = CTkTable(master=table_frame, values=data, hover_color="RoyalBlue", header_color = "RoyalBlue3")
                table.edit_row(0, text_color="white", hover_color="RoyalBlue")
                table.pack(expand=True, fill = "x", pady = 50)

        def del_student():
            for widget in main_frame.winfo_children():
                widget.destroy()
            login_frame = CTkFrame(master = main_frame)
            login_frame.pack(expand = True, fill = 'both', padx = 27, pady = 21)
            pwd = StringVar(self,)

            display_frame = CTkFrame(master = login_frame, width = 600, height = 300)
            display_frame.place(anchor = 'center', relx = 0.5, rely = 0.5)
            
            CTkLabel(master = display_frame, text = "Enter Password",font=("Arial Bold", 20), anchor = 'center').place(relx = 0.5 , y = 100, anchor = 'center')
            CTkEntry(master = display_frame,placeholder_text = 'password please.....', textvariable=pwd, show = "*").place(relx = 0.5, y = 150, anchor = 'center')

            def verification():
                password = pwd.get()
                if password != get_root_password():
                    msg = CTkMessagebox(title="Warning Message!", message="wrong password",icon="warning", option_1="Retry")
                else:
                    button_3()
            b1 = ctk.CTkButton(master = display_frame, text = 'Submit', command = verification).place(relx = 0.5, y = 200, anchor = 'center')


            def button_3():
                for widget in main_frame.winfo_children():
                    widget.destroy()
                CTkLabel(master = main_frame, text = "Roll No. of Student to Delete : ",font=("Arial Bold", 20), anchor = 'center').place(x= 50, y = 50)

                roll = StringVar(self,)

                entry = CTkEntry(master = main_frame, textvariable = roll)
                entry.place(y = 50, x= 350)


                def button_func2():
                    config = read_config()
                    con = mysql.connector.connect(**config)
                    roll_no = roll.get()
                    delete_student(con,roll_no)

                def clear():
                        entry.delete(0,END)
                CTkButton(master = main_frame, text = "Submit", command = lambda: [button_func2(),clear()]).place(x = 100, y = 100)
            
        def attendance():
            config = read_config()
            con = mysql.connector.connect(**config)
            take_attendance(con)

        def export():
            for widget in main_frame.winfo_children():
                widget.destroy()
            login_frame = CTkFrame(master = main_frame)
            login_frame.pack(expand = True, fill = 'both', padx = 27, pady = 21)
            pwd = StringVar(self,)

            display_frame = CTkFrame(master = login_frame, width = 600, height = 300)
            display_frame.place(anchor = 'center', relx = 0.5, rely = 0.5)
            
            CTkLabel(master = display_frame, text = "Enter Password",font=("Arial Bold", 20), anchor = 'center').place(relx = 0.5 , y = 100, anchor = 'center')
            CTkEntry(master = display_frame,placeholder_text = 'password please.....', textvariable=pwd, show = "*").place(relx = 0.5, y = 150, anchor = 'center')

            def verification():
                password = pwd.get()
                if password != get_root_password():
                    msg = CTkMessagebox(title="Warning Message!", message="wrong password",icon="warning", option_1="Retry")
                else:
                    button_3()
            b1 = ctk.CTkButton(master = display_frame, text = 'Submit', command = verification).place(relx = 0.5, y = 200, anchor = 'center')
            
            def button_3():
                config = read_config()
                con = mysql.connector.connect(**config)
                export_students_to_excel(con)

        def late():
            for widget in main_frame.winfo_children():
                widget.destroy()
            login_frame = CTkFrame(master = main_frame)
            login_frame.pack(expand = True, fill = 'both', padx = 27, pady = 21)
            pwd = StringVar(self,)

            display_frame = CTkFrame(master = login_frame, width = 600, height = 300)
            display_frame.place(anchor = 'center', relx = 0.5, rely = 0.5)
            
            CTkLabel(master = display_frame, text = "Enter Password",font=("Arial Bold", 20), anchor = 'center').place(relx = 0.5 , y = 100, anchor = 'center')
            CTkEntry(master = display_frame, placeholder_text = 'password please.....', textvariable=pwd, show = "*").place(relx = 0.5, y = 150, anchor = 'center')

            def verification():
                password = pwd.get()
                if password != get_root_password():
                    msg = CTkMessagebox(title="Warning Message!", message="wrong password",icon="warning", option_1="Retry")
                else:
                    button_4()
            b1 = ctk.CTkButton(master = display_frame, text = 'Submit', command = verification).place(relx = 0.5, y = 200, anchor = 'center')

            def button_4():
                config = read_config()
                con = mysql.connector.connect(**config)
                data = list_students_not_returned(con)
                for widget in main_frame.winfo_children():
                    widget.destroy()
                table_frame = CTkScrollableFrame(master=main_frame)
                table_frame.pack(expand=True, fill="both", padx=27, pady=21)
                table = CTkTable(master=table_frame, values=data, hover_color="RoyalBlue", header_color = "RoyalBlue3")
                table.edit_row(0, text_color="white", hover_color="RoyalBlue")
                table.pack(expand=True, fill = "x", pady = 50)

        def change_password():
            for widget in main_frame.winfo_children():
                widget.destroy()
            login_frame = CTkFrame(master = main_frame)
            login_frame.pack(expand = True, fill = 'both', padx = 27, pady = 21)
            pwd = StringVar(self,)

            display_frame = CTkFrame(master = login_frame, width = 600, height = 300)
            display_frame.place(anchor = 'center', relx = 0.5, rely = 0.5)
            
            CTkLabel(master = display_frame, text = "Enter Current Password",font=("Arial Bold", 20), anchor = 'center').place(relx = 0.5 , y = 100, anchor = 'center')
            CTkEntry(master = display_frame,placeholder_text = 'password please.....', textvariable=pwd, show = "*").place(relx = 0.5, y = 150, anchor = 'center')

            def verification():
                password = pwd.get()
                if password != get_root_password():
                    msg = CTkMessagebox(title="Warning Message!", message="wrong password",icon="warning", option_1="Retry")
                else:
                    button_6()
                    
            b1 = ctk.CTkButton(master = display_frame, text = 'Submit', command = verification).place(relx = 0.5, y = 200, anchor = 'center')
            def button_6():
                
                for widget in main_frame.winfo_children():
                    widget.destroy()
                display_frame = CTkFrame(master = main_frame, width = 600, height = 300)
                display_frame.place(anchor = 'center', relx = 0.5, rely = 0.5)

                temp_1 = StringVar(self,)
                temp_2 = StringVar(self,)

                CTkLabel(master = display_frame, text = "Enter New Password",font=("Arial Bold", 20), anchor = 'center').place(relx = 0.5 , y = 100, anchor = 'e')
                CTkEntry(master = display_frame,placeholder_text = 'password please.....', textvariable=temp_1, show = "*").place(relx = 0.66, y = 100, anchor = 'center')

                CTkLabel(master = display_frame, text = "Confirm New Password",font=("Arial Bold", 20), anchor = 'center').place(relx = 0.5 , y = 150, anchor = 'e')
                CTkEntry(master = display_frame,placeholder_text = 'password please.....', textvariable=temp_2, show = "*").place(relx = 0.66, y = 150, anchor = 'center')

                def new_pass():
                    if temp_1.get() != temp_2.get():
                        msg = CTkMessagebox(title="Warning Message!", message="Password did not match",icon="warning", option_1="Retry")
                    else:
                        set_root_password(temp_1.get())
                        msg = CTkMessagebox(title="Warning Message!", message="Password has been changed",icon="check", option_1="Okay")

                b1 = ctk.CTkButton(master = display_frame, text = 'Submit', command = new_pass).place(relx = 0.5, y = 200, anchor = 'center')
                
        #side frame
        sidebar_frame = CTkFrame(master=self, width=300, height=650, corner_radius=0)
        sidebar_frame.pack_propagate(0)
        sidebar_frame.pack(fill="both", anchor="w", side="left", padx= 2, pady = 2)

        #side frame content
        pfp_img_data = Image.open("pfp.png")
        pfp_img = CTkImage(dark_image=pfp_img_data, light_image=pfp_img_data, size=(100, 110))

        CTkLabel(master=sidebar_frame, text="", image=pfp_img).pack(pady=(38, 0), anchor="center")
        CTkLabel(master=sidebar_frame, text="Admin NITD Hostel", font = ('Arial', 15),text_color="grey", anchor = 'center').pack(anchor = "center", ipady = 5, pady=(30,0))

        CTkButton(master = sidebar_frame, text = "Take attendance", font=("Arial Bold", 14), anchor="w", fg_color = 'grey20', hover_color='grey40', command = attendance).pack(anchor="center", pady=(30,0),expand = True, fill='x')

        CTkButton(master = sidebar_frame, text = "Add Student", font=("Arial Bold", 14), anchor="w", command = add, fg_color = 'grey20', hover_color='grey40').pack(anchor="center", pady=(30,0),expand = True, fill='x')

        CTkButton(master = sidebar_frame, text = "Remove Student", font=("Arial Bold", 14), anchor="w", fg_color = 'grey20', hover_color='grey40', command = del_student).pack(anchor="center", pady=(30,0),expand = True, fill='x')

        CTkButton(master = sidebar_frame, text = "Student List", font=("Arial Bold", 14), anchor="w", command = student_list, fg_color = 'grey20', hover_color='grey40').pack(anchor="center", pady=(30,0),expand = True, fill='x')

        CTkButton(master = sidebar_frame, text = "Today Attendance", font=("Arial Bold", 14), anchor="w", fg_color = 'grey20', hover_color='grey40', command = today_attendance).pack(anchor="center", pady=(30,0),expand = True, fill='x')

        CTkButton(master = sidebar_frame, text = "Export to Exel", font=("Arial Bold", 14), anchor="w", fg_color = 'grey20', hover_color='grey40', command = export).pack(anchor="center", pady=(30,0),expand = True, fill='x')

        CTkButton(master = sidebar_frame, text = "Late Students", font=("Arial Bold", 14), anchor="w", fg_color = 'grey20', hover_color='grey40', command = late).pack(anchor="center", pady=(30,0),expand = True, fill='x')

        CTkButton(master = sidebar_frame, text = "Change Password", font=("Arial Bold", 14), anchor="w", fg_color = 'grey20', hover_color='grey40', command = change_password).pack(anchor="center", pady=(30,0),expand = True, fill='x')
        
        #main frame content
        CTkLabel(master = main_frame, text= "DashBoard", font=('Times New Roman', 40), anchor = 'center').pack(anchor = 'center',ipady = 5, pady = (50,0))
        CTkLabel(master = main_frame, text= "National Institute of Technology", font=('Times New Roman', 40), anchor = 'center').pack(anchor = 'center',ipady = 5, pady = (100,0))
        CTkLabel(master = main_frame, text= "Delhi", font=('Times New Roman', 40), anchor = 'center').pack(anchor = 'center', pady = (20,0))

        logo_img_data = Image.open("logo.png")
        logo_img = CTkImage(dark_image=logo_img_data, light_image=logo_img_data, size=(200, 200))
        CTkLabel(master=main_frame, text="", image=logo_img).pack(pady=(50, 0), anchor="center")


if __name__ == "__main__":
    app=Main_Page()
    app.mainloop()
    
