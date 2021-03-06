from django.shortcuts import render
import MySQLdb
from datetime import datetime


def start(request):
    if 'username' in request.session:
        if 'type' in request.session and request.session['type'] == 'S':
            return render(request, "university_portal/welcome.html",
                          {"username": request.session['username'],
                           "type": request.session['type']})
    return render(request, 'university_portal/login.html', {})


def login(request):
    conn = MySQLdb.connect(user='root', password='root123', database='ssdi_project', host='localhost')
    cur = conn.cursor()
    statement = "select pwd, email, typ from login where email=\'" + request.POST['username'] + "\'"
    cur.execute(statement)
    rs = cur.fetchone()

    if rs:
        if rs[0] == request.POST['password']:
            request.session['username'] = rs[1]
            request.session['type'] = rs[2]
            if rs[2] == 'S':
                return render(request, "university_portal/welcome.html",
                              {"username": request.session['username'],
                               "type": rs[2]})
            elif rs[2] == 'F':
                request.session['faculty'] = get_faculty(request.session['username'])
                request.session['courses'] = get_courses(request.session['username'])
                return render(request, "faculties/teaches.html",
                              {"session": request.session, "faculty": request.session['faculty'],
                               "courses": request.session['courses']})
    return render(request, "university_portal/login.html", {})


def logout(request):
    request.session.flush()
    return render(request, "university_portal/login.html", {})


def assignments(request):
    if 'username' not in request.session:
        return render(request, "university_portal/login.html", {})
    else:
        assign = get_assignments(request.GET['CourseID'])
        faculty = get_faculty(request.session['username'])
        return render(request, "faculties/assignment.html",
                      {"session": request.session, "assignments": assign, "faculties": faculty,
                       "mindate": datetime.today()})


def grades(request):
    if 'username' not in request.session:
        return render(request, "university_portal/login.html", {})
    else:
        assign = get_assignments(request.GET['CourseID'])
        faculty = get_faculty(request.session['username'])
        assignment, students = get_grades(request.GET['aid'], request.GET['Deadline'])
        print(datetime.today())
        return render(request, "faculties/assignment.html",
                      {"session": request.session, "students": students, "faculties": faculty, "assignments": assign,
                       "deadline": assignment, "mindate": datetime.now().strftime("%Y-%m-%d")})


# Query function for Assignment

def get_faculty(username):
    conn = MySQLdb.connect(user='root', password='root123', database='ssdi_project', host='localhost')
    cur = conn.cursor()
    statement = "select * from faculties where email=\'" + username + "\'"
    cur.execute(statement)
    faculty = cur.fetchone()
    conn.close()
    return faculty


def get_courses(username):
    conn = MySQLdb.connect(user='root', password='root123', database='ssdi_project', host='localhost')
    cur = conn.cursor()
    statement = "select c.cid, c.cname, t.semester_of_teaching from courses c, login l, faculties f, teaches t where l.email=\'" + username + "\' and l.email = f.email and f.fid=t.fid and t.cid=c.cid"
    cur.execute(statement)
    course = cur.fetchall()
    return course


def get_assignments(CourseID):
    conn = MySQLdb.connect(user='root', password='root123', database='ssdi_project', host='localhost')
    cur = conn.cursor()
    statement = "select DISTINCT a.aid,a.cid, c.cname from assignments a, courses c where a.cid=\'" + CourseID + "\' and a.cid=c.cid"
    cur.execute(statement)
    all_assignment = cur.fetchall()
    return all_assignment


def get_grades(aid, Deadline):
    conn = MySQLdb.connect(user='root', password='root123', database='ssdi_project', host='localhost')
    cur = conn.cursor()
    cur1 = conn.cursor()
    statement = "update fac_submit set deadline_date= \'" + Deadline + "\' where aid= \'" + aid + "\'"
    statement2 = "select * from students s, assignments a where a.sid=s.sid and aid=\'" +aid+"\'";
    cur.execute(statement)
    conn.commit()
    statement = "select deadline_date from fac_submit where aid=\'" + aid + "\'"
    cur.execute(statement)
    cur1.execute(statement2)
    rs = cur.fetchall()
    rs1 = cur1.fetchall()
    return rs, rs1
