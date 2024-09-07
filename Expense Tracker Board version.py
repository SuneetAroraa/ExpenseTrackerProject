import tkinter as tk
import os
from tkinter import ttk
import mysql.connector as msc
import datetime
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
plt.style.use("fivethirtyeight")

#Eviblishing connection with sql
con = msc.connect(user = 'root', password = 'PASSWORD', host = 'localhost', database = 'csprojtest')
print('SQL Connection status: ' ,con.is_connected())
cur = con.cursor()

#--add expenses screen ---
def add_expense_screen():
    #Initialize add screen
    nroot = tk.Toplevel(root)
    nroot.title("Expense Tracker (by Suneet)|Add Expenses")
    nroot.geometry("500x500")
    nroot.configure(bg='#E0FFE0')

    #print label
    label = tk.Label(nroot, text = 'Add Expenses',font=("Arial", 40), bg="#E0FFE0")
    label.pack(pady=20)

    #expenses entry from user
    entry_label = tk.Label(nroot, text='Enter Expenses:', font=("Arial", 14), bg="#E0FFE0")
    entry_label.pack(pady=10)

    entry = tk.Entry(nroot, font=("Arial", 14))
    entry.pack(pady=10)

    catlist = []
    q = "select cat_id, category from Categories"
    cur.execute(q)
    categories = cur.fetchall()
    for category in categories:
        print(category)
        catlist.append(f"{category[1]}")
        
    
    #dropdown menu for category
    category_label = tk.Label(nroot, text='Category:', font=("Arial", 14), bg="#E0FFE0")
    category_label.pack(pady=10)

    category_var = tk.StringVar()
    category_dropdown = ttk.Combobox(nroot, textvariable=category_var, values=catlist, font=("Arial", 14))
    category_dropdown.pack(pady=10)
    category_dropdown.set('Select Category')

    def add_expense():#to store values of entry and drpdown into list        
        expense = entry.get()
        expense_list = []
        q = "select max(expense_id) from expenses"
        cur.execute(q)
        a = cur.fetchone()
        if a[0] is not None:
            exp_id = a[0] + 1
        else:
            exp_id = 1
        

        
        em = None
        #check if expense is valid integer and >0
        
        if not expense:
            em = "Expenses cannot be empty"
            
        try:
            expense_value = int(expense)
            if expense_value <= 0:
                em = 'Expenses cannot be 0 or negative'
                
        except ValueError:
            em = 'Invalid input. Expenses should be a number'
            
        
        if em: #handaling error
            error = tk.Toplevel(root)
            error.title('Error')
            error.bell()
            label = tk.Label(error, text = em)
            label.pack()
            entry.delete(0,tk.END)
            root.after(3000,error.destroy)
        else:   #getting data with no error
            category = category_var.get()
            q = 'select cat_id from categories where category = %s'
            cur.execute(q,(category,))
            cat_id_tup = cur.fetchone()
            cat_id = int(cat_id_tup[0])
            cdate = datetime.date.today()
            expense_list.append(expense)
            expense_list.append(category)
            print(expense_list)
            expense_list = []
            entry.delete(0, tk.END)

            #execute sql query to insert data into table
            query = "insert into expenses (expense_id, amount, cat_id, tdate) VALUES (%s, %s, %s, %s)"
            cur.execute(query, (exp_id, expense, cat_id, cdate))
            con.commit()

            #display confirmation message
            confirm_screen = tk.Toplevel(root)
            label = tk.Label(confirm_screen, text = 'Expense added')
            label.pack()
            root.after(1000,confirm_screen.destroy)

            

    #add button on screen
    add_button = tk.Button(nroot, text="ADD", font=("Arial", 20), bg="#E0FFE0", command=add_expense)
    add_button.pack(pady=20)

    #back button
    def switch_main_screen():
        nroot.destroy()
        root.deiconify()
    
    back_button = tk.Button(nroot, text = '<-- Back', font=('Arial', 12), command = switch_main_screen)
    back_button.place(x=10, y=10)

    
#--view expenses screen--
def view_expense_screen():
    #initialize window
    n2root = tk.Toplevel(root)
    n2root.title("Expense Tracker (by Suneet)|View Expenses")
    n2root.geometry("500x500")
    n2root.configure(bg='#E0FFE0')

    label = tk.Label(n2root, text = 'View Expenses',font=("Arial", 40), bg="#E0FFE0")
    label.pack(pady=35)

    def view_all():#view all text file func
        #execute sql query and store data in 'rows' variable
        q = 'select e.amount, c.category, e.tdate from expenses as e join categories as c on e.cat_id = c.cat_id;'
        data = cur.execute(q)
        rows = cur.fetchall()
        with open('combined expenses.txt' , 'w') as t:
            for row in rows: #write row into the text file
                rowsp = list(row)
                string = f"{rowsp[0]} spent on {rowsp[1]} on date {rowsp[2]}\n"
                t.write(string)
                #t.write(' spent on '.join(map(str, row)) + '\n')
        #get file path
        filepath = Path('/Users/suneetarora/Desktop/Expense Tracker/combined expenses.txt')
        #print file path in window
        filepath_screen = tk.Toplevel(root)
        filepath_screen.title('File Path')
        
        label = tk.Label(filepath_screen, text = filepath )
        label.pack()
        root.after(5000,filepath_screen.destroy)

        #automatically open text file
        os.system(f'open "{filepath}"')

    def view_tot():#view combined expenses
        #execute sql query and store data in 'rows'
        q = 'select c.category, sum(e.amount) from expenses as e join categories as c on e.cat_id = c.cat_id group by c.category;'
        data = cur.execute(q)
        rows = cur.fetchall()

        #create new tkinter window for output
        opscreen = tk.Toplevel(root)
        opscreen.title("Expense Tracker (by Suneet)|Total Expenses By Category")
        opscreen.geometry("500x500")
        opscreen.configure(bg='#E0FFE0')
        
        label = tk.Label(opscreen, text = 'Total Expenses ',font=("Arial", 40), bg="#E0FFE0")
        label.pack(pady=35)
        

        for row in rows: #format data for tkinter window
            category,tamt = row
            result = f"{category}:{tamt}"
            label = tk.Label(opscreen, text=result, font=("Arial", 14), bg="#E0FFE0")
            label.pack()

        #back button
        def switch_main_screen():
            opscreen.destroy()
            n2root.deiconify()
    
        back_button = tk.Button(opscreen, text = '<-- Back', font=('Arial', 12), command = switch_main_screen)
        back_button.place(x=10, y=10)

    def piegen(): #piechart
        q = 'select c.category, sum(e.amount) from expenses as e join categories as c on e.cat_id = c.cat_id group by c.category;'
        data = cur.execute(q)
        rows = cur.fetchall()
        categories = []
        amounts = []

        for row in rows: #format data for tkinter window
            category,tamt = row
            categories.append(category)
            amounts.append(tamt)    

        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(amounts, labels=categories, autopct='%1.1f%%', wedgeprops={'edgecolor': 'black'})
        ax.set_title("Pie chart")
        plt.show()

        
    all_button = tk.Button(n2root, text="Combine All Expenses Into Text File", font=("Arial", 20), bg="#E0FFE0", command = view_all)
    all_button.pack(pady=30)
    
    tot_button = tk.Button(n2root, text="View Total Expenses By Category", font=("Arial", 20), bg="#E0FFE0", command = view_tot)
    tot_button.pack(pady=20)

    pie_button = tk.Button(n2root, text="Generate Pie Chart", font=("Arial", 20), bg="#E0FFE0", command = piegen )
    pie_button.pack(pady=20)
                    
    def switch_main_screen():
        n2root.destroy()
        root.deiconify()
    
    back_button = tk.Button(n2root, text = '<-- Back', font=('Arial', 12), command = switch_main_screen)
    back_button.place(x=10, y=10)


#Settings_screen
def settings_screen():
    n3root = tk.Toplevel(root)
    n3root.title("Expense Tracker (by Suneet)| Settings")
    n3root.geometry("500x500")
    n3root.configure(bg='#E0FFE0')

    label = tk.Label(n3root, text = 'Settings',font=("Arial", 40), bg="#E0FFE0")
    label.pack(pady=35)

    ###clear sql table funcn###

    
    def confirm_clear(): #func for succesful confirmation
        confirm_screen.destroy()
        query = 'delete from expenses;'
        cur.execute(query)
        query = 'delete from income;'
        cur.execute(query)
        con.commit()

        done_screen = tk.Toplevel(root)
        label = tk.Label(done_screen, text = 'Data Deleted')
        label.pack()
        root.after(3000,done_screen.destroy)
        
    
    def confirmation(): #get confirmation
        global confirm_screen
        confirm_screen = tk.Toplevel(root)
        confirm_screen.title("Expense Tracker (by Suneet)| Confirm Deletion")
        confirm_screen.geometry("500x500")
        confirm_screen.configure(bg='#FF0000')

        label = tk.Label(confirm_screen, text='Are you sure you want to delete data?', font=("Arial", 14), bg="#FF0000")
        label.pack(pady=10)

        label = tk.Label(confirm_screen, text='All EXPENSES and INCOME data will be deleted?', font=("Arial", 16), bg="#FF0000")
        label.pack(pady=10)

        label = tk.Label(confirm_screen, text='Once deleted data will not be recovered', font=("Arial", 16), bg="#FF0000")
        label.pack(pady=10)

        label = tk.Label(confirm_screen, text='Confirm within 10 seconds...', font=("Arial", 16), bg="#FF0000")
        label.pack(pady=10)

        confirm_button = tk.Button(confirm_screen, text="Confirm", font=("Arial", 12), bg="#E0FFE0", command=confirm_clear)
        confirm_button.pack(side="left", padx=20)

        cancel_button = tk.Button(confirm_screen, text="Cancel", font=("Arial", 12), bg="#E0FFE0", command=confirm_screen.destroy)
        cancel_button.pack(side="right", padx=20)

        #cancel after 5 seconds
        root.after(10000, confirm_screen.destroy)
        
    #Clear button
    clear_button = tk.Button(n3root, text="Clear Data From SQL",font=("Arial", 20), bg="#E0FFE0",command = confirmation)
    clear_button.pack(pady = 30)

    def categories():
        cat_root = tk.Toplevel(root)
        cat_root.title("Manage Categories")
        cat_root.geometry("700x500")
        cat_root.configure(bg="#E0FFE0")

        label = tk.Label(cat_root, text="Manage Categories", font=("Arial", 25), bg="#E0FFE0")
        label.pack(pady=20)

        categories_listbox = tk.Listbox(cat_root, font=("Arial", 14),width = 40,activestyle = 'underline',bg = '#ffffff')
        categories_listbox.pack(pady=10)

        def load_cat():
            categories_listbox.delete(0, tk.END)
            q = "select cat_id, category from Categories"
            cur.execute(q)
            categories = cur.fetchall()
            for category in categories:
                categories_listbox.insert(tk.END, f"{category[0]}. {category[1]}")
                global catid
                catid = category[0] + 1
            
                
        
        load_cat()
        def add_category():
            new_category = new_category_entry.get()
            if new_category:
                query = "insert into Categories (cat_id,category) values (%s,%s)"
                cur.execute(query, (catid,new_category))
                con.commit()
                new_category_entry.delete(0, tk.END)
                load_cat()

        new_category_label = tk.Label(cat_root, text="New Category Name:", font=("Arial", 14), bg="#E0FFE0")
        new_category_label.pack(pady=10)
        new_category_entry = tk.Entry(cat_root, font=("Arial", 14))
        new_category_entry.pack(pady=10)
        add_button = tk.Button(cat_root, text="Add Category", font=("Arial", 12), bg="#E0FFE0", command=add_category)
        add_button.pack()

        def delete_category():
            selected_category = categories_listbox.get(categories_listbox.curselection())
            category_id = int(selected_category.split(".")[0])
            query = "delete from Categories where cat_id = %s"
            cur.execute(query, (category_id,))
            con.commit()
            load_cat()

            conf = tk.Toplevel(root)
            conf.title('Deleted')
            label = tk.Label(conf, text = 'Successfully Deleted')
            label.pack()
            root.after(3000,conf.destroy)

        delete_button = tk.Button(cat_root, text="Delete Selected Category", font=("Arial", 12), bg="#E0FFE0", command=delete_category)
        delete_button.pack()


        #back button
        def switch_main_screen():
            cat_root.destroy()
            n3root.deiconify()

        back_button = tk.Button(cat_root, text = '<-- Back', font=('Arial', 12), command = switch_main_screen)
        back_button.place(x=10, y=10)
    
    category_button = tk.Button(n3root, text="Manage Categories",font=("Arial", 20), bg="#E0FFE0",command = categories)
    category_button.pack(pady = 30)

    def add_income_screen():
            aisroot = tk.Toplevel(root)
            aisroot.title("Expense Tracker (by Suneet) | Add Income")
            aisroot.geometry("500x500")
            aisroot.configure(bg='#E0FFE0')

            label = tk.Label(aisroot, text='Add Income', font=("Arial", 40), bg="#E0FFE0")
            label.pack(pady=20)

            income_label = tk.Label(aisroot, text='Income Amount:', font=("Arial", 14), bg="#E0FFE0")
            income_label.pack(pady=10)

            income_entry = tk.Entry(aisroot, font=("Arial", 14))
            income_entry.pack(pady=10)

            source_label = tk.Label(aisroot, text='Income Source:', font=("Arial", 14), bg="#E0FFE0")
            source_label.pack(pady=10)

            source_entry = tk.Entry(aisroot, font=("Arial", 14))
            source_entry.pack(pady=10)
            
            def add_income():
                income = income_entry.get()
                income_source = source_entry.get()

                em = None
                if not income:
                    em = "Income amount cannot be empty"
                else:
                    try:
                        income_value = int(income)
                        if income_value <= 0:
                            em = 'Income amount cannot be 0 or negative'

                        else:
                
                            q = 'insert into income(amount,income_source) values(%s,%s)'
                            cur.execute(q, (income,income_source))
                            con.commit()

                            conf = tk.Toplevel(root)
                            conf.title('Confirmed')
                            label = tk.Label(conf, text = 'Confirmed')
                            label.pack()
                            income_entry.delete(0,tk.END)
                            source_entry.delete(0,tk.END)                
                            root.after(3000,conf.destroy)
                    except ValueError:
                        em = 'Invalid input. Income amount should be a number'

                if em:
                    error = tk.Toplevel(aisroot)
                    error.title('Error')
                    error.bell()
                    label = tk.Label(error, text=em)
                    label.pack()
                    income_entry.delete(0, tk.END)
                    root.after(3000,error.destroy)

            add_button = tk.Button(aisroot, text="Add Income", font=("Arial", 20), bg="#E0FFE0", command=add_income)
            add_button.pack(pady=30)

            def switch_main_screen():
                aisroot.destroy()
                inc_root.deiconify()
    
            back_button = tk.Button(aisroot, text = '<-- Back', font=('Arial', 12), command = switch_main_screen)
            back_button.place(x=10, y=10)
        
            def switch_main_screen():
                aisroot.destroy()
                n3root.deiconify()

            back_button = tk.Button(aisroot, text = '<-- Back', font=('Arial', 12), command = switch_main_screen)
            back_button.place(x=10, y=10)
             
    income_button = tk.Button(n3root, text="Add Income", font=("Arial", 20), bg="#E0FFE0", command=add_income_screen)
    income_button.pack(pady=30)
        

    def switch_main_screen():
        n3root.destroy()
        root.deiconify()
    
    back_button = tk.Button(n3root, text = '<-- Back', font=('Arial', 12), command = switch_main_screen)
    back_button.place(x=10, y=10)

#tkinter main window initialize
root = tk.Tk()
root.title("Monthly Expense Tracker (by Suneet)|Home Page")
width = 450
height = 400
root.geometry('500x450')
root.configure(bg = '#E0FFE0')

#tkinter main screen text and buttons
label = tk.Label(root, text="Monthly Expense Tracker", font=("Arial", 25), bg="#E0FFE0")
label.pack(pady=10)

ctext = 'Loading...'

def cashinhand():
    try:
        query = 'select sum(amount) from expenses'
        cur.execute(query)
        totexpenses = cur.fetchone()[0] or 0
        query = 'select sum(amount) from income'
        cur.execute(query)
        totincome = cur.fetchone()[0] or 0
        cash = totincome - totexpenses
    
    except Exception as e:
        cash = 0
        
    if cash == 0:
        ctext = 'No income or expenses added yet'
        
    else:
        ctext = 'Cash in Hand is: {tcash}'.format(tcash=cash)

    label.config(text=ctext)
    root.after(1000, cashinhand)

label = tk.Label(root, text=ctext, font=("Arial", 20), bg="#E0FFE0")
label.pack(pady=10)
cashinhand()

button1 = tk.Button(root, text="Add Expenses", font=("Arial", 20), command = add_expense_screen)
button1.pack(pady=10)

button2 = tk.Button(root, text="View Expenses", font=("Arial", 20), command = view_expense_screen)
button2.pack(pady=10)

button3 = tk.Button(root, text="Settings",font=("Arial", 20), command = settings_screen)
button3.pack(pady=10)

button1.config(height=2, width=20)
button2.config(height=2, width=20)
button3.config(height=2, width=10)



#tkinter loop 
root.mainloop()
#END
