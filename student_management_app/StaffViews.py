from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json


from student_management_app.models import CustomUser, Staffs, Department, Subjects, Students, Batch, Attendance, AttendanceReport, FeedBackStaffs , StudentResult


def staff_home(request):
    # Fetching All Students under Staff

    subjects = Subjects.objects.filter(staff_id=request.user.id)
    course_id_list = []
    for subject in subjects:
        course = Department.objects.get(id=subject.dept_id.id)
        course_id_list.append(course.id)
    
    final_course = []
    # Removing Duplicate Course Id
    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)
    
    students_count = Students.objects.filter(dept_id__in=final_course).count()
    subject_count = subjects.count()

    # Fetch All Attendance Count
    attendance_count = Attendance.objects.filter(subject_id__in=subjects).count()
    # Fetch All Approve Leave
    

    #Fetch Attendance Data by Subjects
    subject_list = []
    attendance_list = []
    for subject in subjects:
        attendance_count1 = Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance_count1)

    students_attendance = Students.objects.filter(dept_id__in=final_course)
    student_list = []
    student_list_attendance_present = []
    student_list_attendance_absent = []
    for student in students_attendance:
        attendance_present_count = AttendanceReport.objects.filter(status=True, student_id=student.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(status=False, student_id=student.id).count()
        student_list.append(student.admin.first_name+" "+ student.admin.last_name)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)

    context={
        "students_count": students_count,
        "attendance_count": attendance_count,
        "subject_count": subject_count,
        "subject_list": subject_list,
        "attendance_list": attendance_list,
        "student_list": student_list,
        "attendance_present_list": student_list_attendance_present,
        "attendance_absent_list": student_list_attendance_absent
    }
    return render(request, "staff_template/staff_home_template.html", context)



def staff_take_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = Batch.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "staff_template/take_attendance_template.html", context)



def staff_feedback(request):
    staff_obj = Staffs.objects.get(admin=request.user.id)
    feedback_data = FeedBackStaffs.objects.filter(staff_id=staff_obj)
    context = {
        "feedback_data":feedback_data
    }
    return render(request, "staff_template/staff_feedback_template.html", context)


def staff_feedback_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method.")
        return redirect('staff_feedback')
    else:
        feedback = request.POST.get('feedback_message')
        staff_obj = Staffs.objects.get(admin=request.user.id)

        try:
            add_feedback = FeedBackStaffs(staff_id=staff_obj, feedback=feedback, feedback_reply="")
            add_feedback.save()
            messages.success(request, "Feedback Sent.")
            return redirect('staff_feedback')
        except:
            messages.error(request, "Failed to Send Feedback.")
            return redirect('staff_feedback')


# WE don't need csrf_token when using Ajax
@csrf_exempt
def get_students(request):
    # Getting Values from Ajax POST 'Fetch Student'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    session_model =Batch.objects.get(id=session_year)

    students = Students.objects.filter(dept_id=subject_model.dept_id, batch_id=session_model)

    # Only Passing Student Id and Student Name Only
    list_data = []
    list_data.append(subject_model.lab)
    for student in students:
        data_small={"id":student.admin.id, "name":student.admin.first_name+" "+student.admin.last_name}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)
@csrf_exempt
def get_students_marks(request):
    # Getting Values from Ajax POST 'Fetch Student'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    session_model =Batch.objects.get(id=session_year)

    students = StudentResult.objects.filter(subject_id=subject_model)

    # Only Passing Student Id and Student Name Only
    list_data=[]
    for student in students:
        #x=Students.objects.all.filter(id=student.student_id)
        data_small={"usn":student.student_id.admin.username,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"cie_1":student.cie_1,"cie_2":student.cie_2,"cie_3":student.cie_3,"quiz_1":student.quiz_1,"quiz_2":student.quiz_2,"quiz_3":student.quiz_3,"selfstudy":student.selfstudy,"lab":student.lab,"status":student.status}
        list_data.append(data_small)
    print(list_data)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)




@csrf_exempt
def save_attendance_data(request):
    # Get Values from Staf Take Attendance form via AJAX (JavaScript)
    # Use getlist to access HTML Array/List Input Data
    student_ids = request.POST.get("student_ids")
    subject_id = request.POST.get("subject_id")
    attendance_date = request.POST.get("attendance_date")
    session_year_id = request.POST.get("session_year_id")

    subject_model = Subjects.objects.get(id=subject_id)
    session_year_model =Batch.objects.get(id=session_year_id)

    json_student = json.loads(student_ids)
    # print(dict_student[0]['id'])

    # print(student_ids)
    try:
        # First Attendance Data is Saved on Attendance Model
        attendance = Attendance(subject_id=subject_model, attendance_date=attendance_date, batch_id=session_year_model)
        attendance.save()

        for stud in json_student:
            # Attendance of Individual Student saved on AttendanceReport Model
            student = Students.objects.get(admin=stud['id'])
            attendance_report = AttendanceReport(student_id=student, attendance_id=attendance, status=stud['status'])
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")
        print(e)




def staff_update_attendance(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = Batch.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "staff_template/update_attendance_template.html", context)

@csrf_exempt
def get_attendance_dates(request):
    

    # Getting Values from Ajax POST 'Fetch Student'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year_id")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    session_model = Batch.objects.get(id=session_year)

    # students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(subject_id=subject_model, batch_id=session_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.batch_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def get_attendance_student(request):
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


@csrf_exempt
def update_attendance_data(request):
    student_ids = request.POST.get("student_ids")

    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    json_student = json.loads(student_ids)

    try:
        
        for stud in json_student:
            # Attendance of Individual Student saved on AttendanceReport Model
            student = Students.objects.get(admin=stud['id'])

            attendance_report = AttendanceReport.objects.get(student_id=student, attendance_id=attendance)
            attendance_report.status=stud['status']

            attendance_report.save()
        return HttpResponse("OK")
    except:
        print(e)
        return HttpResponse("Error")


def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin=user)

    context={
        "user": user,
        "staff": staff
    }
    return render(request, 'staff_template/staff_profile.html', context)


def staff_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('staff_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            staff = Staffs.objects.get(admin=customuser.id)
            staff.address = address
            staff.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('staff_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('staff_profile')



def staff_add_result(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = Batch.objects.all()
    x=[]
    for i in subjects:
        if i.lab:
            x.append(i.id)
    context = {
        "subjects": subjects,
        "session_years": session_years,
        "a":x,
    }
    return render(request, "staff_template/add_result_template.html", context)
def staff_view_marks(request):
    subjects = Subjects.objects.filter(staff_id=request.user.id)
    session_years = Batch.objects.all()
    x=[]
    for i in subjects:
        if i.lab:
            x.append(i.id)
    context = {
        "subjects": subjects,
        "session_years": session_years,
        "a":x,
    }
    return render(request, "staff_template/staff_view_marks.html", context)

def staff_add_result_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_result')
    else:
        student_admin_id = request.POST.get('student_list')
        cie1 = int(request.POST.get('cie1'))
        cie2 = int(request.POST.get('cie2'))
        cie3 = int(request.POST.get('cie3'))
        quiz1 = int(request.POST.get('quiz1'))
        quiz2 = int(request.POST.get('quiz2'))
        subject=request.POST.get('subject')
        sub=Subjects.objects.all().filter(id=subject)
        islab=Subjects.objects.all().filter(id=subject).values_list('lab')
        quiz3 = int(request.POST.get('quiz3'))
        if(islab==True):
            lab=int(request.POST.get('lab'))
        else:
            lab=0
        print(islab)
        selfstudy=int(request.POST.get('selfstudy'))
        #subject=request.POST.get('subject')
        
        s=0
        print(sub)
        if(True):
            s=s+(cie1+cie2+cie3)/3+quiz1+quiz2+quiz3+selfstudy
            if(s>=40):
                status=True
            else:
                status=False
        else:
             s=s+(cie1+cie2+cie3)/3+quiz1+quiz2+quiz3+selfstudy+lab
             if(s>=60):
                 status=True
             else:
                 status=False
        print(status)
        if(cie1<0 or cie1>50):
            messages.error(request, "CIE I marks not in range")
            messages.error(request, "0 to 50 allowed")

            return redirect('staff_add_result')
        if(cie2<0 or cie2>50):
            messages.error(request, "CIE II marks not in range")
            messages.error(request, "0 to 50 allowed")
            return redirect('staff_add_result')
        if(cie3<0 or cie3>50):
            messages.error(request, "CIE III marks not in range")
            messages.error(request, "0 to 50 allowed")
            return redirect('staff_add_result')
        if(quiz1<0 or quiz1>10):
            messages.error(request, "QUIZ I marks not in range")
            messages.error(request, "0 to 10 allowed")
            return redirect('staff_add_result')
        if(quiz2<0 or quiz2>10):
            messages.error(request, "QUIZ II marks not in range")
            messages.error(request, "0 to 10 allowed")
            return redirect('staff_add_result')
        if(quiz3<0 or quiz3>10):
            messages.error(request, "QUIZ III marks not in range")
            messages.error(request, "0 to 10 allowed")
            return redirect('staff_add_result')
        if(lab<0 or lab>50):
            messages.error(request, "Lab not in range")
            messages.error(request, "0 to 50 allowed")
            return redirect('staff_add_result')
        if(selfstudy<0 or selfstudy>20):
            messages.error(request, "SelfStudy marks not in range")
            messages.error(request, "0 to 20 allowed")
            return redirect('staff_add_result')

        
        ct_id = request.POST.get('subject')
        subject_id = request.POST.get('subject')
        student_obj = Students.objects.get(admin=student_admin_id)
        subject_obj = Subjects.objects.get(id=subject_id)

        try:
            # Check if Students Result Already Exists or not
            check_exist = StudentResult.objects.filter(subject_id=subject_obj, student_id=student_obj).exists()
            if check_exist:
                result = StudentResult.objects.get(subject_id=subject_obj, student_id=student_obj)
                result.cie_1 = cie1
                result.cie_2 = cie2
                result.cie_3 = cie3
                result.quiz_1=quiz1
                result.quiz_2=quiz2
                result.quiz_3=quiz3
                result.lab=lab
                result.status=status
                result.selfstudy=selfstudy
                print(result)
                result.save()
                messages.success(request, "Result Updated Successfully!")
                return redirect('staff_add_result')
            else:
                result = StudentResult(student_id=student_obj, subject_id=subject_obj,cie_1 = cie1,cie_2 = cie2,cie_3 = cie3,quiz_1=quiz1,quiz_2=quiz2,quiz_3=quiz3,selfstudy=selfstudy,status=status)
                result.save()
                messages.success(request, "Result Added Successfully!")
                return redirect('staff_add_result')
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            messages.error(request, "Failed to Add Result!")
            return redirect('staff_add_result')
