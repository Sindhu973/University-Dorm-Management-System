import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser
import decimal

@st.cache
def get_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}


def query_db(sql: str):
    # print(f"Running query_db(): {sql}")
    db_info = get_config()
    # Connect to an existing database
    conn = psycopg2.connect(**db_info)
    # Open a cursor to perform database operations
    cur = conn.cursor()
    # Execute a command: this creates a new table
    cur.execute(sql)
    # Obtain data
    data = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    # Make the changes to the database persistent
    conn.commit()
    # Close communication with the database
    cur.close()
    conn.close()
    df = pd.DataFrame(data=data, columns=column_names)

    return df

def insert_db(sql: str):
    # print(f"Running query_db(): {sql}")
    db_info = get_config()
    # Connect to an existing database
    conn = psycopg2.connect(**db_info)
    # Open a cursor to perform database operations
    cur = conn.cursor()
    # Execute a command: this creates a new table
    cur.execute(sql)
    # Make the changes to the database persistent
    conn.commit()
    # Close communication with the database
    cur.close()
    conn.close()

st.title("University Dorm Management")

sidemenu = [ "Admin", "Employee", "Student"]
user = st.sidebar.selectbox('User Menu', sidemenu)

if user == "Student":

    menu = [ "Profile", "Application", "Payments", "Cafeteria", "Requests/Complaints", "Requests Status Update" ]
    choice = st.selectbox('Menu', menu)

    if choice == "Application":
        st.subheader("Application")

        col1, col2, = st.columns(2)

        with col1:
            sid_sql = f"Select sid from Students;"
            try:
                sid_list = query_db( sid_sql )["sid"].tolist()
                sid = st.selectbox('Select your University ID', sid_list)
            except Exception as E:
                st.write('Sorry, something went wrong with your application!')
                st.write( E )

        with col2:
            try:
                aid_sid_sql = f"select aid from Applications where sid = {sid}"
                aid_sid_info = query_db(aid_sid_sql)["aid"].tolist()
            except Exception as E:
                st.write('Sorry, something went wrong with your application!')
                st.write( E )

            if not aid_sid_info:        

                with st.form('application_form'):
                    uId = st.text_input('University ID')
                    pet = st.radio('Do you have a pet?', ('Yes', 'No'))
                    petPref = st.radio('Are you comfortable with a pet friendly flat?', ('Yes', 'No'))
                    numFlat = st.selectbox('Choose preferred number of flatmates?', ('1', '2', '3','0'))
                    commPref =  st.selectbox('What is your preferred community?', ('A', 'B', 'C'))
                    submit = st.form_submit_button('Submit')   

                    if submit:
                        qry = f"""INSERT into Applications( sid, pet, petPref, numFlat, commPref ) values ( {uId}, '{pet}', '{petPref}', {numFlat}, '{commPref}' )"""            
                        try:
                            insert_db(qry)
                            st.info('Application Submitted')  
                        except Exception as E:
                            st.write("Sorry! Something went wrong with your query, please try again.")
                            st.write(E)
                    
            else:
                st.write('Application Status')
                #Joining Applications and Occupy
                aid_status_sql = f"""Select A.aid, A.sid, A.pet, A.petpref, A.numflat, A.commpref, A.status, O.rid, O.bid
                                    from
                                    ( Select A.aid, A.sid, A.pet, A.petpref, A.numflat, A.commpref, A.status from Applications A where A.sid = {sid} ) as A
                                    LEFT OUTER JOIN
                                    Occupy as O 
                                    ON O.sid = A.sid;"""
                try:
                    aid_status_sql = query_db(aid_status_sql)
                    st.dataframe(aid_status_sql)
                except Exception as E:
                    st.write("Sorry! Something went wrong with your query, please try again.")
                    st.write(E)

    if choice == "Profile":        
        st.subheader("Student Profile")

        with st.form('profile_form'):
            uId = st.text_input('University ID')
            firstName = st.text_input('First Name')
            lastName = st.text_input('Last Name')
            dob = st.date_input('Date of Birth')
            address = st.text_input('Address')
            ph = st.text_input('10-digit Mobile Number')
            email = st.text_input('Email')            
            dept = st.selectbox('What department are you enrolled in?', ('CS', 'CE', 'MOT', 'Cybersecurity') )
            pType = st.selectbox('What is your program type?',('MS','BS')) 

            proSubmit = st.form_submit_button('Submit') 

            if proSubmit:
                qry = f"""INSERT into Students( sid, sfirst, slast, ph, email, address, dob, dept, program ) values ( {uId}, '{firstName}', '{lastName}', '{ph}', '{email}', '{address}', '{dob}', '{dept}', '{pType}' )"""            
                try:
                    insert_db(qry)
                    st.info('Profile Updated') 
                except Exception as E:
                    st.write("Sorry! Something went wrong with your query, please try again.")
                    st.write(E)

    if choice == "Payments":
        st.subheader("Student Rent Payments")

        with st.form('payments_form'):
            uId = st.text_input('University ID')
            term = st.selectbox('Choose term', ('JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEPT','OCT','NOV','DEC'))
            amount = st.number_input('Amount')

            paySubmit = st.form_submit_button('Submit')

            if paySubmit:
                qry = f"""INSERT into Payments( sid, amount, term ) values ( {uId}, {amount}, '{term}' )"""
                try:
                    insert_db( qry )
                    st.info('Payment Done')
                except Exception as E:
                    st.write("Sorry! Something went wrong with your query, please try again.")
                    st.write(E)

    if choice == "Cafeteria":
        st.subheader("Cafeteria")

        col1, col2 = st.columns(2)

        with col1:
            sql_cafe_names = "SELECT name FROM Cafes;"
            cafe_names = query_db(sql_cafe_names)["name"].tolist()
            cafe_name = st.selectbox("Choose a cafe", cafe_names)
            
            sql_cafe = f"SELECT * FROM Cafes WHERE name = '{cafe_name}';"
            try:
                cafe_info = query_db(sql_cafe)
                cid = cafe_info["cid"][0]
                st.dataframe(cafe_info)
            except Exception as E:
                    st.write("Sorry! Something went wrong with your query, please try again.")
                    st.write(E)

        with col2:
            with st.form('orders_form'):
                item_sql = f"SELECT iname, price from Menus M, Items I where M.cid = {cid} and M.iid = I.iid"
                items_info = query_db(item_sql)
                items_list = items_info["iname"].tolist()
                item = st.selectbox("Choose an item", items_list)
                qty = st.number_input("Enter quanity")            
                sid = st.text_input("University ID")
                cid = cafe_info["cid"][0]

                orderSubmit = st.form_submit_button('Submit')

                if orderSubmit:
                    item_price_sql = f"SELECT iid, price from Items I where I.iname = '{item}'"
                    price_info = query_db(item_price_sql)["price"][0]            
                    price = price_info * decimal.Decimal( qty )
                    iid = query_db(item_price_sql)["iid"][0]
                    qry = f"""INSERT into Orders( quantity, iid, cost, sid, cid ) values ( {qty}, '{iid}', {price}, {sid}, {cid} )"""
                    try:
                        insert_db( qry )
                        st.info('Order Placed!')
                    except Exception as E:
                        st.write("Sorry! Something went wrong with your query, please try again.")
                        st.write(E)

    if choice == "Requests/Complaints":
        st.subheader("Student Requests/Complaints Form")
        
        with st.form('requests_form'):
            uId = st.text_input('University ID')
            category = st.selectbox('Choose category', ('Electricity','Plumbing','Cleaning','Pest Control','Janitor' ))
            desc = st.text_input('Description')

            reqSubmit = st.form_submit_button('Submit')

            if reqSubmit:
                qry = f"""INSERT into Requests( category, description, sid, status ) values ( '{category}', '{desc}', {uId}, 'pending' )"""
                try:
                    insert_db( qry )
                    st.info('Request Registered')
                except Exception as E:
                    st.write("Sorry! Something went wrong with your query, please try again.")
                    st.write(E)

    if choice == "Requests Status Update":
        st.subheader("Student Requests Status Update")

        col1, col2 = st.columns(2)

        with col1:   
            sql_sid = f"SELECT sid from Students;"
            try:
                sid_info = query_db( sql_sid )["sid"].tolist()
                sid = st.selectbox("University ID", sid_info)
                sql_req_sid = f"SELECT * FROM Requests WHERE sid = {sid} and status = 'in progress';"
                req_sid_info = query_db(sql_req_sid)
                rid_list = req_sid_info["rid"].tolist()
                st.dataframe(req_sid_info)
            except Exception as E:
                st.write("Sorry! Something went wrong with your query, please try again.")
                st.write(E)       
        
        with col2:
            with st.form('upd_form'):
                rid = st.selectbox('Request ID', rid_list)
                updFormSubmit = st.form_submit_button('Submit')

                if updFormSubmit:
                    upd_sql = f"UPDATE Requests set status = 'completed' where rid = {rid}"
                    try:
                        insert_db(upd_sql)
                        st.info('Status Updated')
                    except Exception as E:
                        st.write("Sorry! Something went wrong with your query, please try again.")
                        st.write(E)
if user == "Employee":
    menu = [ "Employee Registration", "Tasks", "Paycheck"]
    choice = st.selectbox( "Menu", menu )

    if choice == "Employee Registration":        
        st.subheader("New Employee Registration")

        with st.form('profile_form'):
            uId = st.text_input('University Employee ID')
            firstName = st.text_input('First Name')
            lastName = st.text_input('Last Name')
            dob = st.date_input('Date of Birth')
            address = st.text_input('Address')
            ph = st.text_input('10-digit Mobile Number')
            email = st.text_input('Email')            
            
            proSubmit = st.form_submit_button('Submit') 

            if proSubmit:
                qry = f"""INSERT into Employees( eid, efirst, elast, ph, email, address, dob ) values ( {uId}, '{firstName}', '{lastName}', '{ph}', '{email}', '{address}', '{dob}' )"""            
                try:
                    insert_db(qry)
                    st.info('Profile Updated')  
                except Exception as E:
                    st.write("Sorry! Something went wrong with your query, please try again.")
                    st.write(E)
        
    if choice == "Paycheck":
        with st.form('emp_paycheck'):
            eid = st.text_input('Employee ID')
            paySubmit = st.form_submit_button('Submit')

        if paySubmit:
            try:
                #joining the tables pay and admins
                sql_salary = f"SELECT p.amount as Amount, p.date as Date, a.afirst as Payed_by, a.email as Admin_mail FROM Pay p, Admins a WHERE p.adid=a.adid AND p.eid={eid};"
                salary_info = query_db(sql_salary)
                st.subheader("Your Paycheck")
                st.dataframe(salary_info)
            except Exception as E:
                    st.write("Sorry! Something went wrong with your query, please try again.")
                    st.write(E)

    if choice ==  "Tasks":
        with st.form('emp_tasks'):
            eid = st.text_input('Employee ID')
            taskSubmit = st.form_submit_button('Submit')

        if taskSubmit:
            #joining the tables requests and assigned_to 
            try:
                sql_tasks_prev = f"SELECT a.rid as Task_ID, r.description as Description FROM Assigned_To a, Requests r WHERE a.rid = r.rid AND a.eid={eid} AND r.status='completed';"
                prev_tasks_info = query_db(sql_tasks_prev)
                st.subheader("Your Completed Tasks")
                st.dataframe(prev_tasks_info)
            except Exception as E:
                    st.write("Sorry! Something went wrong with your query, please try again.")
                    st.write(E)
                    
            #joining the tables requests and assigned_to 
            try:
                sql_tasks_new = f"SELECT a.rid as Task_ID, r.description as Description FROM Assigned_To a, Requests r WHERE a.rid = r.rid AND a.eid={eid} AND r.status='in progress';"
                new_tasks_info = query_db(sql_tasks_new)
                st.subheader("Your Incomplete Tasks")
                st.dataframe(new_tasks_info)
            except Exception as E:
                    st.write("Sorry! Something went wrong with your query, please try again.")
                    st.write(E)

if user == "Admin":
    menu = [ "Profile", "Employee Payrolls", "Requests/Complaints", "Manage Dorms", "Student Payment Activity"]
    choice = st.selectbox( "Menu", menu )

    if choice == "Profile":        
        st.subheader("Admin profile")

        with st.form('profile_form'):
            uId = st.text_input('University Staff ID')
            firstName = st.text_input('First Name')
            lastName = st.text_input('Last Name')
            dob = st.date_input('Date of Birth')
            address = st.text_input('Address')
            ph = st.text_input('10-digit Mobile Number')
            email = st.text_input('Email')            
            
            proSubmit = st.form_submit_button('Submit') 

            if proSubmit:
                try:
                    qry = f"""INSERT into Admins( adid, afirst, alast, ph, email, address, dob ) values ( {uId}, '{firstName}', '{lastName}', '{ph}', '{email}', '{address}', '{dob}' )"""            
                    insert_db(qry)
                    st.info('Profile Updated')   
                except Exception as E:
                    st.write("Sorry! Something went wrong with your query, please try again.")
                    st.write(E)
            
    if choice == "Employee Payrolls":
        st.subheader('Employee Payrolls')
        try:
            sql_eids = f"select e.eid from Employees e"
            eids = query_db(sql_eids)["eid"].tolist()
            ch = st.selectbox("Select the employee ID",eids)
        except Exception as E:
            st.write("Sorry! Something went wrong with your query, please try again.")
            st.write(E)

        col1, col2 = st.columns(2)
        with col1:
            try:
                #Joining Requests and Assigned_To
                sql_tasks = f"SELECT r.rid,r.description,r.status FROM Requests r, Assigned_To a where a.rid=r.rid AND a.eid = {ch}; "
                tasks = query_db(sql_tasks)
                st.dataframe(tasks)
            except Exception as E:
                st.write("Sorry! Something went wrong with your query, please try again.")
                st.write(E)

        with col2:
            with st.form('emp_payroll_form'):
                
                salary = st.number_input("Enter Payment")
                adid = st.text_input("Enter Admin ID")
                date = st.date_input("Enter Date")

                paySubmit = st.form_submit_button('Pay')

                if paySubmit:
                    try:
                        qry = f"""INSERT into Pay( amount, date, eid, adid ) values ( {salary}, '{date}', {ch},{adid} )"""
                        insert_db( qry )
                        st.info('Pay Updated!')
                    except Exception as E:
                        st.write("Sorry! Something went wrong with your query, please try again.")
                        st.write(E)

    if choice == "Requests/Complaints":
        st.write('All Requests')
        try:        
            sql_req = f"SELECT * FROM Requests;"
            req_info = query_db(sql_req)
            st.dataframe(req_info)
        except Exception as E:
            st.write("Sorry! Something went wrong with your query, please try again.")
            st.write(E)


        col1, col2 = st.columns(2)
        with col1:
            try:
                sql_req = f"SELECT * FROM Requests where status='pending';"
                req = query_db(sql_req)["rid"].tolist()
                ch1 = st.selectbox("Select a pending request to assign",req)
            except Exception as E:
                st.write("Sorry! Something went wrong with your query, please try again.")
                st.write(E)

            try:
                sql_category = f"SELECT category FROM Requests WHERE rid = {ch1};"
                cat = query_db(sql_category)["category"][0]
            except Exception as E:
                st.write("Sorry! Something went wrong with your query, please try again.")
                st.write(E)

        with col2:     
            try:       
                sql_emp = f"SELECT e.eid, e.efirst, e.elast from Employees e WHERE e.category = '{cat}';"
                emp = query_db(sql_emp)["eid"].tolist()
                ch2 = st.selectbox("Select an employee from the pending request category to assign the task",emp)
            except Exception as E:
                st.write("Sorry! Something went wrong with your query, please try again.")
                st.write(E)

        with st.form('Requests'):
            taskSubmit = st.form_submit_button('Assign') 
            if taskSubmit:
                try:
                    qry = f"""INSERT into Assigned_To( eid,rid ) values ( {ch2},{ch1})"""      
                    insert_db(qry)
                    st.info('Task assigned!')      
                except Exception as E:
                    st.write("Sorry! Something went wrong with your query, please try again.")
                    st.write(E) 

                try:
                    qry= f"""UPDATE Requests SET status = 'in progress' WHERE rid = {ch1}"""     
                    insert_db(qry); 
                    st.info("Status changed!")
                except Exception as E:
                    st.write("Sorry! Something went wrong with your query, please try again.")
                    st.write(E)

    if choice == "Manage Dorms":
        
        col1, col2 = st.columns(2)
        with col1:
            try:
                sql_app = f"SELECT * FROM Applications where status='Pending';"
                app = query_db(sql_app)["aid"].tolist()
            except Exception as E:
                st.write("Sorry! Something went wrong with your query, please try again.")
                st.write(E)

            try:
                ch1 = st.selectbox("Select an application to address",app)
                sql_data = f"SELECT * FROM Applications WHERE aid = {ch1}"
                data = query_db(sql_data)
                st.dataframe(data)
                numflat = data["numflat"][0]
                commpref = data["commpref"][0]
                petpref = data["petpref"][0]
                pet = data["pet"][0]
                sid = data["sid"][0]
            except Exception as E:
                st.write("Sorry! Something went wrong with your query, please try again.")
                st.write(E)


        with col2:
            if petpref=="Yes":
                sql_room = f"SELECT r.rid, b.name, b.community, r.pet_friendly, r.pet_exists, r.tot_occupancy, r.cur_occupancy FROM Rooms_in r, Buildings b WHERE r.bid = b.bid AND r.pet_friendly like '%Yes%' AND r.tot_occupancy = {numflat+1} AND r.cur_occupancy!=r.tot_occupancy;"
            elif petpref=="No":
                sql_room = f"SELECT r.rid, b.name, b.community, r.pet_friendly, r.pet_exists, r.tot_occupancy, r.cur_occupancy FROM Rooms_in r, Buildings b WHERE r.bid = b.bid AND r.pet_friendly like '%No%' AND r.tot_occupancy = {numflat+1} AND r.cur_occupancy!=r.tot_occupancy;"
            try:
                room = query_db(sql_room)
            except Exception as E:
                st.write("Sorry! Something went wrong with your query, please try again.")
                st.write(E)


            if room.empty:
                st.info("Sorry, no rooms vacant")

            else:
                comm_room = room[room["community"] == commpref]
                
                if comm_room.empty:
                    st.dataframe(room)
                    chroom = st.selectbox("Select room to allot",room["rid"].tolist())
                    
                else:
                    st.dataframe(comm_room)
                    chroom = st.selectbox("Select room to allot",comm_room["rid"].tolist())



            with st.form("manage_dorms"):    
                taskSubmit = st.form_submit_button('Assign') 

                if taskSubmit:     
                    try:       
                        qry= f"""UPDATE Rooms_in SET pet_exists = '{pet}' WHERE rid = {chroom}"""     
                        insert_db(qry); 
                    except Exception as E:
                        st.write("Sorry! Something went wrong with your query, please try again.")
                        st.write(E)

                    try:
                        sql_build = f"SELECT bid from Rooms_in where rid = {chroom};"
                        build = query_db(sql_build)["bid"][0]
                    except Exception as E:
                        st.write("Sorry! Something went wrong with your query, please try again.")
                        st.write(E)
                    try:
                        qry = f"""INSERT into Occupy( sid,rid,bid ) values ( {sid},{chroom},{build})"""      
                        insert_db(qry)
                        st.info('Room Assigned!')    
                    except Exception as E:
                        st.write("Sorry! Something went wrong with your query, please try again.")
                        st.write(E)


                    try:
                        qry= f"""UPDATE Applications SET status = 'Assigned' WHERE aid = {ch1}"""     
                        insert_db(qry); 
                        st.info("Application status changed!")
                    except Exception as E:
                        st.write("Sorry! Something went wrong with your query, please try again.")
                        st.write(E)

                    try:
                        qry= f"""UPDATE Rooms_in SET cur_occupancy = cur_occupancy+1 WHERE rid = {chroom}"""     
                        insert_db(qry); 
                        st.info("Room occupancy updated!")
                    except Exception as E:
                                st.write("Sorry! Something went wrong with your query, please try again.")
                                st.write(E)

        st.subheader('Room Statistics by Community')
        try:
            comm_st_sql = f"SELECT B.community, B.bid, COUNT(R.rid) as Total_Rooms from Rooms_in R, Buildings B where R.bid = B.bid group by B.community, B.bid;"
            comm_st_info = query_db(comm_st_sql)
            st.dataframe(comm_st_info)
        except Exception as E:
            st.write("Sorry! Something went wrong with your query, please try again.")
            st.write(E)

        st.subheader('Student Reports')
        try:
            stu_st_sql = f"""select S.sid, S.sfirst, S.slast, S.status, R.rid, R.bid, R.community, R.address
                            from
                            ( select S.sid, S.sfirst, S.slast, A.status
                                from Students S, Applications A
                                where S.sid = A.sid ) as S
                            LEFT OUTER JOIN 
                            ( select O.rid, O.sid, B.bid, B.community, B.address
                                from Occupy O, Buildings B
                                where O.bid = B.bid ) as R
                            ON S.sid = R.sid;"""
            stu_st_info = query_db(stu_st_sql)
            st.dataframe(stu_st_info)
        except Exception as E:
            st.write("Sorry! Something went wrong with your query, please try again.")
            st.write(E)    

    if choice== "Student Payment Activity":
        st.write("All Payments")
        try:
            sql_pay = f"SELECT * FROM Payments;"
            pay_info = query_db(sql_pay)
            st.dataframe(pay_info)
        except Exception as E:
            st.write("Sorry! Something went wrong with your query, please try again.")
            st.write(E)

        try:
            st.write("Term wise payments")
            sql_termfee = f"SELECT term, sum(amount) from Payments GROUP BY(term)"
            termfee = query_db(sql_termfee)
            st.dataframe(termfee)
        except Exception as E:
            st.write("Sorry! Something went wrong with your query, please try again.")
            st.write(E)        

        try:
            st.write("Student wise Payments")
            sql_stutermfee = f"SELECT sid,term, sum(amount) from Payments GROUP BY(sid,term)"
            stutermfee = query_db(sql_stutermfee)
            st.dataframe(stutermfee)
        except Exception as E:
            st.write("Sorry! Something went wrong with your query, please try again.")
            st.write(E)