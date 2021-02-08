from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json,sys
import string

from student_management_app.models import CustomUser, Staffs, Department, Subjects, Students, Batch, FeedBackStudent, FeedBackStaffs,Attendance, AttendanceReport
from .forms import AddStudentForm, EditStudentForm,AddStaffForm, EditStaffForm


def admin_home(request):
    try :
        all_student_count = Students.objects.all().count()
        subject_count = Subjects.objects.all().count()
        course_count = Department.objects.all().count()
        staff_count = Staffs.objects.all().count()

        # Total Subjects and students in Each Course
        course_all = Department.objects.all()
        course_name_list = []
        subject_count_list = []
        student_count_list_in_course = []

        for course in course_all:
            subjects = Subjects.objects.filter(dept_id=course.id).count()
            students = Students.objects.filter(dept_id=course.id).count()
            course_name_list.append(course.dept_name)
            subject_count_list.append(subjects)
            student_count_list_in_course.append(students)
        
        subject_all = Subjects.objects.all()
        subject_list = []
        student_count_list_in_subject = []
        for subject in subject_all:
            course = Department.objects.get(id=subject.dept_id.id)
            student_count = Students.objects.filter(dept_id=course.id).filter(batch_id=subject.batch_id).count()
            subject_list.append(subject.subject_name)
            student_count_list_in_subject.append(student_count)
        
        # For Saffs
        staff_attendance_present_list=[]
        #staff_attendance_leave_list=[]
        staff_name_list=[]

        staffs = Staffs.objects.all()
        for staff in staffs:
            subject_ids = Subjects.objects.filter(staff_id=staff.admin.id)
            attendance = Attendance.objects.filter(subject_id__in=subject_ids).count()
            #leaves = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
            staff_attendance_present_list.append(attendance)
             #staff_attendance_leave_list.append(leaves)
            staff_name_list.append(staff.admin.first_name)

        # For Students
        student_attendance_present_list=[]
        student_attendance_leave_list=[]
        student_name_list=[]

        students = Students.objects.all()
        for student in students:
            attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
            absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        
            student_attendance_present_list.append(attendance)
            student_attendance_leave_list.append(absent)
            student_name_list.append(student.admin.first_name)


        context={
            "all_student_count": all_student_count,
            "subject_count": subject_count,
            "course_count": course_count,
            "staff_count": staff_count,
            "course_name_list": course_name_list,
            "subject_count_list": subject_count_list,
            "student_count_list_in_course": student_count_list_in_course,
            "subject_list": subject_list,
            "student_count_list_in_subject": student_count_list_in_subject,
            "staff_attendance_present_list": staff_attendance_present_list,
            "student_attendance_leave_list":student_attendance_leave_list,
            "staff_name_list": staff_name_list,
            "student_attendance_present_list": student_attendance_present_list,
        
            "student_name_list": student_name_list,
        }
        print(context)
        return render(request, "hod_template/home_content.html", context)
    except:
        print('error')


def add_staff(request):
    form = AddStaffForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_staff_template.html', context)


def add_staff_save(request):
    num=0
    al=0
    sym=0
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_staff')
    else:
        form = AddStaffForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
        
                
            address = form.cleaned_data['address']
            #session_year_id = form.cleaned_data['session_year_id']
            course_id = form.cleaned_data['dept_id']
            gender = form.cleaned_data['gender']

            # Getting Profile     
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None
            try:
                print(request.POST)
                for i in password:
                   if(ord(i)>=48 and ord(i)<=57):
                        num+=1
                   elif((ord(i)>=65 and ord(i)<=90) or ((ord(i)>=97 and ord(i)<=122))):
                        al+=1
                   else:
                        sym+=1
                print(len(password),num,sym,al)
                if(len(password)<8 or num<2 or sym<1):
                    raise NameError('HiThere')
                
                user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
                print(2)
                user.staffs.address = address
                print(3)
                course_obj = Department.objects.get(id=course_id)
                print(4)
                user.staffs.dept_id = course_obj
                print(7)
                print(course_obj)

                #session_year_obj = Batch.objects.get(id=session_year_id)
                #user.students.batch_id= session_year_obj

                user.staffs.gender = gender
                user.staffs.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Staff Added Successfully!")
                return redirect('add_staff')
            except Exception as e:
                exception_type, exception_object, exception_traceback = sys.exc_info()

                filename = exception_traceback.tb_frame.f_code.co_filename

                line_number = exception_traceback.tb_lineno


                print("Exception type: ", exception_type)

                print("File name: ", filename)

                print("Line number: ", line_number)
                print(e)
                messages.error(request, "Failed to Add Staff !")
                return redirect('add_staff')    
        else:
            return redirect('add_staff')



def manage_staff(request):
    staffs = Staffs.objects.all()
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):
   # Adding Student ID into Session Variable
    request.session['staff_id'] = staff_id

    student = Staffs.objects.get(admin=staff_id)
    form = EditStaffForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = student.admin.email
    form.fields['username'].initial = student.admin.username
    form.fields['first_name'].initial = student.admin.first_name
    form.fields['last_name'].initial = student.admin.last_name
    form.fields['address'].initial = student.address
    form.fields['dept_id'].initial = student.dept_id.id
    form.fields['gender'].initial = student.gender
    #form.fields['session_year_id'].initial = student.batch_id

    context = {
        "id": staff_id,
        "username": student.admin.username,
        "form": form
    }
    return render(request, "hod_template/edit_staff_template.html", context)
def edit_staff_save(request):
   if request.method != "POST":
        return HttpResponse("Invalid Method!")
   else:
        staff_id = request.session.get('staff_id')
        if staff_id == None:
            return redirect('/manage_staff')

        form = EditStaffForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            course_id = form.cleaned_data['dept_id']
            gender = form.cleaned_data['gender']
            #session_year_id = form.cleaned_data['session_year_id']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=staff_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                user.save()

                # Then Update Students Table
                student_model = Staffs.objects.get(admin=staff_id)
                student_model.address = address

                course = Department.objects.get(id=course_id)
                student_model.course_id = course

                #session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                #student_model.session_year_id = session_year_obj

                student_model.gender = gender
                if profile_pic_url != None:
                    student_model.profile_pic = profile_pic_url
                student_model.save()
                # Delete student_id SESSION after the data is updated
                del request.session['staff_id']

                messages.success(request, "Student Updated Successfully!")
                return redirect('/edit_staff/'+staff_id)
            except Exception as e:
                exception_type, exception_object, exception_traceback = sys.exc_info()

                filename = exception_traceback.tb_frame.f_code.co_filename

                line_number = exception_traceback.tb_lineno


                print("Exception type: ", exception_type)

                print("File name: ", filename)

                print("Line number: ", line_number)
                messages.error(request, "Failed to Update Staff.")

                return redirect('/edit_staff/'+staff_id)
        else:
            return redirect('/edit_staff/'+staff_id)


def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    try:
        ad=staff.delete()

        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')




def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        course = request.POST.get('course')
        try:
            if(course==""):
                raise error
            course_model = Department(dept_name=course)
            
            #cource_model.full_clean()
            course_model.save()
            messages.success(request, "Department Added Successfully!")
            return redirect('add_course')
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            messages.error(request, "Failed to Add Department!")
            return redirect('add_course')


def manage_course(request):
    courses = Department.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'hod_template/manage_course_template.html', context)


def edit_course(request, course_id):
    course =Department.objects.get(id=course_id)
    context = {
        "course": course,
        "id": course_id
    }
    return render(request, 'hod_template/edit_course_template.html', context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course')

        try:
            course = Department.objects.get(id=course_id)
            course.dept_name = course_name
            course.save()

            messages.success(request, "Department Updated Successfully.")
            return redirect('/edit_course/'+course_id)

        except:
            messages.error(request, "Failed to Update Department.")
            return redirect('/edit_course/'+course_id)


def delete_course(request, course_id):
    course =Department.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Department Deleted Successfully.")
        return redirect('manage_course')
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print (message)
        messages.error(request, "Failed to Delete Department.")
        return redirect('manage_course')


def manage_session(request):
    session_years =Batch.objects.all()
    context = {
        "session_years": session_years
    }
    return render(request, "hod_template/manage_session_template.html", context)


def add_session(request):
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_course')
    else:
        session_start_year = request.POST.get('session_start_year')
        semester = request.POST.get('semester')

        try:
            sessionyear = Batch(batch_start_year=session_start_year, semester=semester)
            sessionyear.save()
            messages.success(request, "Batch added Successfully!")
            return redirect("add_session")
        except:
            messages.error(request, "Failed to Add Batch")
            return redirect("add_session")


def edit_session(request, session_id):
    session_year = Batch.objects.get(id=session_id)
    context = {
        "session_year": session_year
    }
    return render(request, "hod_template/edit_session_template.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_session')
    else:
        session_id = request.POST.get('batch_id')
        session_start_year = request.POST.get('session_start_year')
        semester = request.POST.get('semester')

        try:
            session_year =Batch.objects.get(id=session_id)
            session_year.batch_start_year = session_start_year
            session_year.semester = semester
            session_year.save()

            messages.success(request, "Batch Updated Successfully.")
            return redirect('/edit_session/'+session_id)
        except:
            messages.error(request, "Failed to Update Session Year.")
            return redirect('/edit_session/'+session_id)


def delete_session(request, session_id):
    session =Batch.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "Batch Deleted Successfully.")
        return redirect('manage_session')
    except:
        messages.error(request, "Failed to Delete Session.")
        return redirect('manage_session')


def add_student(request):
    form = AddStudentForm()
    context = {
        "form": form
    }
    return render(request, 'hod_template/add_student_template.html', context)




def add_student_save(request):
    num=0
    sym=0
    al=0
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_student')
    else:
        form = AddStudentForm(request.POST, request.FILES)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            address = form.cleaned_data['address']
            session_year_id = form.cleaned_data['session_year_id']
            course_id = form.cleaned_data['dept_id']
            gender = form.cleaned_data['gender']

            # Getting Profile     
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None
            try:
                for i in password:
                   if(ord(i)>=48 and ord(i)<=57):
                        num+=1
                   elif((ord(i)>=65 and ord(i)<=90) or ((ord(i)>=97 and ord(i)<=122))):
                        al+=1
                   else:
                        sym+=1
                print(len(password),num,sym,al)
                if(len(password)<8 or num<2 or sym<1):
                    raise NameError('HiThere')
                print(request.POST)
                user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=3)
                print(2)
                user.students.address = address
                print(3)
                course_obj = Department.objects.get(id=course_id)
                print(4)
                user.students.dept_id = course_obj
                print(7)
                print(course_obj)

                session_year_obj = Batch.objects.get(id=session_year_id)
                user.students.batch_id= session_year_obj

                user.students.gender = gender
                user.students.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Student Added Successfully!")
                return redirect('add_student')
            except Exception as e:
                exception_type, exception_object, exception_traceback = sys.exc_info()

                filename = exception_traceback.tb_frame.f_code.co_filename

                line_number = exception_traceback.tb_lineno


                print("Exception type: ", exception_type)

                print("File name: ", filename)

                print("Line number: ", line_number)
                messages.error(request, "Failed to Add Student!")
                return redirect('add_student')
        else:
            return redirect('add_student')


def manage_student(request):
    students = Students.objects.all()
    context = {
        "students": students
    }
    return render(request, 'hod_template/manage_student_template.html', context)


def edit_student(request, student_id):
    # Adding Student ID into Session Variable
    request.session['student_id'] = student_id

    student = Students.objects.get(admin=student_id)
    form = EditStudentForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = student.admin.email
    form.fields['username'].initial = student.admin.username
    form.fields['first_name'].initial = student.admin.first_name
    form.fields['last_name'].initial = student.admin.last_name
    form.fields['address'].initial = student.address
    form.fields['dept_id'].initial = student.dept_id.id
    form.fields['gender'].initial = student.gender
    form.fields['session_year_id'].initial = student.batch_id

    context = {
        "id": student_id,
        "username": student.admin.username,
        "form": form
    }
    return render(request, "hod_template/edit_student_template.html", context)


def edit_student_save(request):#Student
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        student_id = request.session.get('student_id')
        if student_id == None:
            return redirect('/manage_student')

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            course_id = form.cleaned_data['dept_id']
            gender = form.cleaned_data['gender']
            session_year_id = form.cleaned_data['session_year_id']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                user.save()

                # Then Update Students Table
                student_model = Students.objects.get(admin=student_id)
                student_model.address = address

                course = Department.objects.get(id=course_id)
                student_model.course_id = course

                session_year_obj = Batch.objects.get(id=session_year_id)
                student_model.session_year_id = session_year_obj

                student_model.gender = gender
                if profile_pic_url != None:
                    student_model.profile_pic = profile_pic_url
                student_model.save()
                # Delete student_id SESSION after the data is updated
                del request.session['student_id']

                messages.success(request, "Student Updated Successfully!")
                return redirect('/edit_student/'+student_id)
            except Exception as e:
                exception_type, exception_object, exception_traceback = sys.exc_info()

                filename = exception_traceback.tb_frame.f_code.co_filename

                line_number = exception_traceback.tb_lineno


                print("Exception type: ", exception_type)

                print("File name: ", filename)

                print("Line number: ", line_number)
                messages.error(request, "Failed to Update Student.")
                return redirect('/edit_student/'+student_id)
        else:
            return redirect('/edit_student/'+student_id)


def delete_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    try:
        student.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return redirect('manage_student')


def add_subject(request):
    courses =Department.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    a=[i for i in range(1,6)]
    b=[True,False]
    sem1=Batch.objects.all()
    context = {
        "courses": courses,
        "staffs": staffs,
        "range":a,
        "sem":sem1,
        "islab":b
    }
    #print(sem.semester  )
    return render(request, 'hod_template/add_subject_template.html', context    )



def add_subject_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subject')
    else:
        subject_name = request.POST.get('subject')
        sid=request.POST.get('subjectid')
        semid=request.POST.get('sem')
        semes=Batch.objects.get(id=semid)
        print(semid)
        print(semes)
        x=request.POST.get('lab')
        #print(sem.semester)
        course_id = request.POST.get('course')
        course = Department.objects.get(id=course_id)
        credit=request.POST.get('credit')
        print(credit)
        #sem=request.POST.get('sem')
        staff_id = request.POST.get('staff')
        staff = CustomUser.objects.get(id=staff_id)
        lab=request.POST.get('lab')

        try:
            if subject_name=="" or sid=="":
                raise error
            subject = Subjects(subject_name=subject_name, dept_id=course, staff_id=staff,cid=sid,batch_id=semes,credit=credit,lab=lab)
            print(subject.lab)
            #subject.full_clean()
            subject.save()
            messages.success(request, "Subject Added Successfully!")
            return redirect('add_subject')
        except Exception as e:
                exception_type, exception_object, exception_traceback = sys.exc_info()

                filename = exception_traceback.tb_frame.f_code.co_filename

                line_number = exception_traceback.tb_lineno


                print("Exception type: ", exception_type)

                print("File name: ", filename)

                print("Line number: ", line_number)
                print(e)
                messages.error(request, "Failed to Add Subject!")
                return redirect('add_subject')


def manage_subject(request):
    subjects = Subjects.objects.all()
    context = {
        "subjects": subjects
    }
    return render(request, 'hod_template/manage_subject_template.html', context)


def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Department.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    a=[i for i in range(1,6)]
    context = {
        "subject": subject,
        "courses": courses,
        "range":a,
        "staffs": staffs,
        "id": subject_id
    }
    return render(request, 'hod_template/edit_subject_template.html', context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        sid=request.POST.get('subjectid')
        subject_name = request.POST.get('subject')
        course_id = request.POST.get('course')
        credit=request.POST.get('credit')
        staff_id = request.POST.get('staff')


        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name
            
            course = Department.objects.get(id=course_id)
            subject.course_id = course

            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff
            subject.credit=credit
            subject.cid=sid
            
            subject.save()

            messages.success(request, "Subject Updated Successfully.")
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))

        except Exception as e:
                exception_type, exception_object, exception_traceback = sys.exc_info()

                filename = exception_traceback.tb_frame.f_code.co_filename

                line_number = exception_traceback.tb_lineno
                print("Exception type: ", exception_type)

                print("File name: ", filename)

                print("Line number: ", line_number)

                messages.error(request, "Failed to Update Subject.")
                return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))
            # return redirect('/edit_subject/'+subject_id)



def delete_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject Deleted Successfully.")
        return redirect('manage_subject')
    except Exception as e:
                exception_type, exception_object, exception_traceback = sys.exc_info()

                filename = exception_traceback.tb_frame.f_code.co_filename

                line_number = exception_traceback.tb_lineno
                print("Exception type: ", exception_type)

                print("File name: ", filename)

                print("Line number: ", line_number)

                messages.error(request, "Failed to Delete Subject.")
                print(e)
                return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))
            # return redirect('/edit_subject/'+subject_id)


@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)



def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/student_feedback_template.html', context)


@csrf_exempt
def student_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/staff_feedback_template.html', context)


@csrf_exempt
def staff_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def admin_view_attendance(request):
    subjects = Subjects.objects.all()
    session_years = Batch.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
    # Getting Values from Ajax POST 'Fetch Student'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("batch_year_id")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    #session_model = Batch.objects.get(id=session_year)

    # students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(subject_id=subject_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id, "name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name, "status":student.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')
    


def staff_profile(request):
    pass


def student_profile(requtest):
    pass



