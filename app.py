#import streamlit as st
#import pandas as pd

#data = pd.read_csv("data/data.csv")

#st.title("Student Performance Dashboard")

#st.write(data)

#data["Average"] = data[["DM&GT","UHV","IDS","ADS&AA","JAVA"]].mean(axis=1)

#st.subheader("Average Marks")
#st.bar_chart(data["Average"])

#st.subheader("Subject Wise Average")
#st.bar_chart(data[["DM&GT","UHV","IDS","ADS&AA","JAVA"]].mean())

#streamlit run app.py


import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
import os

# ---------------- Constants ----------------
PASS_MARK = 24
TOTAL_MARK = 75

# ---------------- CSV Files ----------------
STUDENT_FILE = "students.csv"
SUBJECT_FILE = "subjects.csv"
ADMIN_FILE = "admin.csv"

# ---------------- Create CSV if not exists ----------------
for file, cols in [(STUDENT_FILE, ["RegisterNo","Name","Branch","Year","Semester","S1","S2","S3","S4","S5"]),
                   (SUBJECT_FILE, ["Semester","Sub1","Sub2","Sub3","Sub4","Sub5"]),
                   (ADMIN_FILE, ["userid","password"])]:
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file,index=False)

students = pd.read_csv(STUDENT_FILE)
subjects = pd.read_csv(SUBJECT_FILE)
admins = pd.read_csv(ADMIN_FILE)

st.title("🎓 College Result Management System")

menu = st.sidebar.selectbox("Portal", ["Student Portal","Admin Portal","Analytics"])

# ---------------- STUDENT PORTAL ----------------
if menu == "Student Portal":
    st.header("Student Result Portal")
    reg = st.text_input("Enter Register Number")
    
    if reg:
        student = students[students["RegisterNo"].astype(str) == reg]
        if not student.empty:
            st.subheader(f"Student Name: {student.iloc[0]['Name']}")
            cgpa_list = []
            sems = sorted(student["Semester"].unique())
            for sem in sems:
                row = student[student["Semester"]==sem].iloc[0]
                sub_row = subjects[subjects["Semester"]==sem]
                if sub_row.empty:
                    st.error(f"Subjects not found for Semester {sem}")
                    continue
                sub_names = sub_row.iloc[0][1:].tolist()
                marks = row[["S1","S2","S3","S4","S5"]].astype(int).tolist()
                df = pd.DataFrame({"Subject":sub_names, "Marks":marks})
                st.subheader(f"Semester {sem}")

                def color(val):
                    try:
                        val=int(val)
                        return "background-color:lightgreen" if val>=PASS_MARK else "background-color:red;color:white"
                    except:
                        return ""

                st.dataframe(df.style.applymap(color))

                avg = sum(marks)/len(marks)
                sgpa = (avg/TOTAL_MARK)*10
                cgpa_list.append(sgpa)
                st.write("SGPA:", round(sgpa,2))

            if cgpa_list:
                cgpa = sum(cgpa_list)/len(cgpa_list)
                st.subheader(f"CGPA: {round(cgpa,2)}")

            # ---------------- PDF DOWNLOAD ----------------
            if st.button("Download Result PDF"):
                filename="result.pdf"
                c = canvas.Canvas(filename)
                y=800
                c.drawString(200,y,"College Result Memo")
                y-=40
                c.drawString(100,y,f"Name: {student.iloc[0]['Name']}")
                y-=30
                for sem in sems:
                    row = student[student["Semester"]==sem].iloc[0]
                    marks = row[["S1","S2","S3","S4","S5"]].tolist()
                    sub_row = subjects[subjects["Semester"]==sem]
                    if sub_row.empty: continue
                    sub_names = sub_row.iloc[0][1:].tolist()
                    c.drawString(100,y,f"Semester {sem}")
                    y-=20
                    for sub, m in zip(sub_names, marks):
                        c.drawString(120,y,f"{sub}: {m}")
                        y-=20
                    y-=10
                c.save()
                with open(filename,"rb") as f:
                    st.download_button("Download PDF", f, file_name="result.pdf")

        else:
            st.error("Register Number Not Found")

# ---------------- ADMIN PORTAL ----------------
elif menu=="Admin Portal":
    st.header("Admin Login")
    user = st.text_input("UserID")
    pwd = st.text_input("Password", type="password")
    
    login = admins[(admins["userid"]==user) & (admins["password"]==pwd)]
    if not login.empty:
        st.success("Login Successful")
        admin_menu = st.selectbox("Admin Options", ["Add Student","Search/Edit Student","Delete Student","Upload Excel"])
        
        # ---------------- Add Student ----------------
        if admin_menu=="Add Student":
            st.subheader("Add Student Marks")
            reg = st.text_input("Register No", key="add_reg")
            name = st.text_input("Name", key="add_name")
            branch = st.text_input("Branch", key="add_branch")
            year = st.number_input("Year",1,4, key="add_year")
            sem = st.number_input("Semester",1,8, key="add_sem")
            sub_row = subjects[subjects["Semester"]==sem]
            if not sub_row.empty:
                subs = sub_row.iloc[0][1:].tolist()
                m1 = st.number_input(subs[0],0,75, key="add_m1")
                m2 = st.number_input(subs[1],0,75, key="add_m2")
                m3 = st.number_input(subs[2],0,75, key="add_m3")
                m4 = st.number_input(subs[3],0,75, key="add_m4")
                m5 = st.number_input(subs[4],0,75, key="add_m5")
                if st.button("Save Marks"):
                    new = {"RegisterNo":reg,"Name":name,"Branch":branch,"Year":year,
                           "Semester":sem,"S1":m1,"S2":m2,"S3":m3,"S4":m4,"S5":m5}
                    students.loc[len(students)] = new
                    students.to_csv(STUDENT_FILE,index=False)
                    st.success("Data Saved")

        # ---------------- Search / Edit Student ----------------
        elif admin_menu=="Search/Edit Student":
            st.subheader("Search / Edit Student")
            reg_search = st.text_input("Enter Register Number to Edit", key="edit_reg")
            if reg_search:
                student = students[students["RegisterNo"].astype(str)==reg_search]
                if not student.empty:
                    row_idx = student.index[0]
                    st.write("Current Marks:")
                    st.write(student.loc[row_idx,["S1","S2","S3","S4","S5"]])
                    m1 = st.number_input("S1",0,75,value=int(student.loc[row_idx,"S1"]), key="edit_m1")
                    m2 = st.number_input("S2",0,75,value=int(student.loc[row_idx,"S2"]), key="edit_m2")
                    m3 = st.number_input("S3",0,75,value=int(student.loc[row_idx,"S3"]), key="edit_m3")
                    m4 = st.number_input("S4",0,75,value=int(student.loc[row_idx,"S4"]), key="edit_m4")
                    m5 = st.number_input("S5",0,75,value=int(student.loc[row_idx,"S5"]), key="edit_m5")
                    if st.button("Update Marks"):
                        students.loc[row_idx,["S1","S2","S3","S4","S5"]] = [m1,m2,m3,m4,m5]
                        students.to_csv(STUDENT_FILE,index=False)
                        st.success("Marks Updated")
                else:
                    st.error("Student Not Found")

        # ---------------- Delete Student ----------------
        elif admin_menu=="Delete Student":
            st.subheader("Delete Student Record")
            reg_del = st.text_input("Enter Register Number to Delete", key="del_reg")
            if reg_del:
                student = students[students["RegisterNo"].astype(str)==reg_del]
                if not student.empty:
                    row_idx = student.index[0]
                    if st.button("Delete Student"):
                        students.drop(row_idx,inplace=True)
                        students.to_csv(STUDENT_FILE,index=False)
                        st.success("Student Record Deleted")
                else:
                    st.error("Student Not Found")

        # ---------------- Excel Upload ----------------
        elif admin_menu=="Upload Excel":
            st.subheader("Upload Excel File")
            file = st.file_uploader("Upload Excel", type=["xlsx"])
            if file:
                df = pd.read_excel(file)
                students = pd.concat([students,df],ignore_index=True)
                students.to_csv(STUDENT_FILE,index=False)
                st.success("Excel Uploaded Successfully")
    else:
        st.warning("Enter Admin Login")

# ---------------- ANALYTICS ----------------
else:
    st.header("Department Analytics")
    branch = st.selectbox("Select Branch", students["Branch"].unique())
    branch_data = students[students["Branch"]==branch]
    st.subheader("Average Marks")
    avg = branch_data[["S1","S2","S3","S4","S5"]].astype(float).mean()
    st.bar_chart(avg)
    st.subheader("Pass Percentage")
    passed = (branch_data[["S1","S2","S3","S4","S5"]].astype(float) >= PASS_MARK).sum().sum()
    total = branch_data[["S1","S2","S3","S4","S5"]].count().sum()
    percent = (passed/total)*100 if total>0 else 0
    st.metric("Pass Percentage",f"{percent:.2f}%")