from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from app.models import Team, User,Task, MOM, Comments, File, Permissions
from os import system as syst
from django.utils import timezone

@csrf_exempt
def logged_in(request):
	return User.objects.filter(
		uname=request.COOKIES.get("username"),
		ses_id=request.COOKIES.get("sesid")
	).exists()

@csrf_exempt
def logged_in_post(request):
	return User.objects.filter(
		uname=request.POST["username"],
		ses_id=request.POST["sesid"]
	).exists()

@csrf_exempt
def is_admin(request,team_name_t):
    return Permissions.objects.filter(
        user=User.objects.get(
            uname=request.COOKIES.get("username"),
            ses_id=request.COOKIES.get("sesid")
        ),
        team=Team.objects.get(team_name=team_name_t),
        admin_status=True
    ).exists()

@csrf_exempt
def is_admin_post(request,team_name_t):
    return Permissions.objects.filter(
        user=User.objects.get(
            uname=request.POST.get("username"),
            ses_id=request.POST.get("sesid")
        ),
        team=Team.objects.get(team_name=team_name_t),
        admin_status=True
    ).exists()

@csrf_exempt
def download_access(request,team_name_t):
    return Permissions.objects.filter(
        user=User.objects.get(
            uname=request.COOKIES.get("username"),
            ses_id=request.COOKIES.get("sesid")
        ),
        team=Team.objects.get(team_name=team_name_t),
        file_access = True
    ).exists()

@csrf_exempt
def download_access_post(request,team_name_t):
    return Permissions.objects.filter(
        user=User.objects.get(
            uname=request.POST.get("username"),
            ses_id=request.POST.get("sesid")
        ),
        team=Team.objects.get(team_name=team_name_t),
        file_access=True
    ).exists()

@csrf_exempt
def read_access(request,team_name_t):
    user_object = User.objects.get(
        uname=request.COOKIES.get("username"),
        ses_id=request.COOKIES.get("sesid")
    )
    return Permissions.objects.filter(
        user=user_object,
        team=Team.objects.get(team_name=team_name_t),
    ).exists()


@csrf_exempt
def read_access_post(request,team_name_t):
	user_object = User.objects.get(
		uname=request.POST.get("username"),
		ses_id=request.POST.get("sesid")
	)
	return Permissions.objects.filter(
        user=user_object,
        team=Team.objects.get(team_name=team_name_t),
    ).exists()

def get_formatted_team_name(team_name):
	if team_name == "round1":
		return "Round1"
	elif team_name == "round2":
		return "Round2"
	elif team_name == "swifttyper":
		return "SwiftTyper"
	else:
		return team_name

@csrf_exempt
def home(request):
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(uname=username, passwd=password).exists():
            permissions = Permissions.objects.filter(user=User.objects.get(uname=username, passwd=password))
            team_set = set()
            for permission in permissions:
                team_set.add(permission.team)
            context = {"teams": list(team_set)}
            response = HttpResponse()
            response = render(request, 'home/choice.html', context)
            response.set_cookie(
                key='sesid',
                value=User.objects.filter(uname=username, passwd=password).get().ses_id
            )
            response.set_cookie(
                key='username',
                value=User.objects.filter(uname=username, passwd=password).get().uname
            )
            return response
        else:
            return HttpResponse("<html><h1>Invalid Details</h1></html>")
    elif logged_in(request):
        permissions = Permissions.objects.filter(user=User.objects.get(uname=request.COOKIES['username']))
        team_set = set()
        for permission in permissions:
            team_set.add(permission.team)
        context = {"teams": list(team_set)}
        return render(request, 'home/choice.html', context)
    else:
        return render(request, 'home/login.html')

@csrf_exempt
def feeds(request, team_name_t):
    if logged_in(request):
        if read_access(request,team_name_t):
            if request.method=="POST":
                comment_obj = Comments(
                    task=Task.objects.get(task_id=request.POST['task_id']),
                    user=User.objects.get(uname=request.COOKIES.get("username")),
                    text=request.POST['text']
                )
                comment_obj.save()
            all_tasks = Task.objects.prefetch_related('comments_set').filter(team=Team.objects.get(team_name=team_name_t)).order_by('-last_modified_time')
            context = {
                "tasks": all_tasks,
                "team": team_name_t,
                "isadmin": is_admin(request,team_name_t),
                "round": get_formatted_team_name(team_name_t),
            }
            return render(request, 'home/feed.html', context)
        else:
            raise Http404
    else:
        return redirect("/")

@csrf_exempt
def mom(request, team_name_t):
    if logged_in(request):
        if read_access(request, team_name_t):
            all_moms = MOM.objects.filter(
                team=Team.objects.get(team_name=team_name_t)
            ).order_by('-mom_id')
            context = {
                "moms": all_moms,
                "team": team_name_t,
                "round": get_formatted_team_name(team_name_t),
            }
            return render(request,'home/mom.html', context)
        else:
            raise Http404
    else:
        return redirect("/")

@csrf_exempt
def cmom(request, team_name_t):
    if logged_in(request):
        if read_access(request,team_name_t):
            if request.method=='POST':
                mom_object = MOM(
                    subject=request.POST['subject'],
                    text=request.POST['text'],
                    team=Team.objects.filter(team_name = team_name_t).get(),
                    created_by=User.objects.filter(uname=request.COOKIES.get("username")).get()
                )
                mom_object.save()
                return HttpResponse("<html><h1>Successfully saved</h1></html>")
            else:
                context = {"team": team_name_t}
                return render(request, 'home/cmom.html', context)
        else:
            raise Http404
    else:
        return redirect("/")

@csrf_exempt
def ctasks(request, team_name_t):
    if logged_in(request):
        if is_admin(request,team_name_t):
            if request.method=='POST':
                task_object = Task(
                    task_name=request.POST['task_name'],
                    tags=request.POST['tags'],
                    team=Team.objects.filter(team_name=team_name_t).get(),
                    created_by=User.objects.filter(uname=request.COOKIES['username']).get(),
                    assigned_to=User.objects.filter(uname=request.POST['assigned_to']).get(),
                    deadline_time=request.POST['deadline']
                )
                task_object.save()
                return HttpResponse("<html><h1>Successfully saved</h1></html>")
            else:
                permissions = Permissions.objects.filter(team=Team.objects.filter(team_name=team_name_t))
                users = set()
                for permission in permissions:
                    users.add(str(permission.user))
                context = {
                    "team": team_name_t,
                    "users": users,
                    "round": get_formatted_team_name(team_name_t),
                }
                return render(request, 'home/ctasks.html', context)
        else:
            raise Http404
    else:
        return redirect("/")

@csrf_exempt
def accept_task(request, team_name_t):
	if request.method=="POST":
		if logged_in(request):
		    if is_admin(request,team_name_t):
			    task_object=Task.objects.get(task_id=request.POST['task_id'])
			    task_object.accepted_time=timezone.localtime(timezone.now())
			    task_object.last_modified_time=timezone.localtime(timezone.now())
			    task_object.accepted=True
			    task_object.save()
			    return HttpResponse("<html><h1>Successfully accepted</h1></html>")

@csrf_exempt
def submit_task(request, team_name_t):
    if logged_in(request):
        if read_access(request,team_name_t):
            if request.method=="POST":
                task_object=Task.objects.get(task_id=request.POST['task_id'])
                task_object.submittion_time=timezone.localtime(timezone.now())
                task_object.last_modified_time=timezone.localtime(timezone.now())
                task_object.submitted=True
                task_object.save()
                uploaded_file = request.FILES['file_submit']
                file_text = uploaded_file.read()
                file_object=File(file_name=uploaded_file.name,task=task_object)
                with open('files/'+str(file_object.file_id),'w') as f:
                    f.write(file_text)
                file_object.save()
                return HttpResponse("<html><h1>Successfully submitted</h1></html>")
            else:
                all_tasks = Task.objects.filter(assigned_to=User.objects.get(uname=request.COOKIES.get("username")))
                context = {
                    "tasks": all_tasks,
                    "team": str(team_name_t),
                    "round": get_formatted_team_name(team_name_t),
                }
                return render(request, 'home/tasks.html', context)
        else:
            raise Http404
    else:
        return redirect("/")
@csrf_exempt
def mytask(request, team_name_t):
    if logged_in(request):
        if read_access(request,team_name_t):
            if request.method=='POST':
                task_object=Task.objects.get(
                    assigned_to=User.objects.get(uname=request.COOKIES['username']),
                    task_id=request.POST['task_id']
                )
                task_object.submittion_time=timezone.localtime(timezone.now())
                task_object.last_modified_time=timezone.localtime(timezone.now())
                task_object.submitted=True
                task_object.save()
                if not 'file_submit' in request.FILES:
                    return HttpResponse("<html><h1>No file selected</h1></html>")
                uploaded_file = request.FILES['file_submit']
                file_text = uploaded_file.read()
                if File.objects.filter(task=task_object,file_name=uploaded_file.name).exists():
                    file_object=File.objects.get(task=task_object,file_name=uploaded_file.name)
                    file_object.accepted=False
                    file_object.submitted_time=timezone.localtime(timezone.now())
                    file_object.save()
                else:
                    file_object=File(file_name=uploaded_file.name,task=task_object,tags=request.POST['tags'])
                    file_object.save()
                f = open('files/'+str(file_object.file_id),'w+')
                f.write(file_text)
                f.close()
                return HttpResponse("<html><h1>File Submitted</h1></html>")
            my_tasks = Task.objects.prefetch_related('file_set').filter(
                assigned_to=User.objects.get(uname=request.COOKIES.get("username")),
                team=Team.objects.get(team_name=team_name_t)
            ).order_by('-task_id')
            context = {
                "team": team_name_t,
                "tasks": my_tasks,
                "user": User.objects.get(uname=request.COOKIES['username']),
                "round": get_formatted_team_name(team_name_t),
                "is_admin": is_admin(request,team_name_t),
            }
            return render(request, 'home/mytask.html', context)
        else:
            raise Http404
    else:
        return redirect("/")
@csrf_exempt
def alltask(request, team_name_t):
    if logged_in(request):
        if read_access(request,team_name_t):
            if request.method=='POST':
                if 'task_id' in request.POST and 'accept' in request.POST:
                    task_object = Task.objects.get(task_id=request.POST['task_id'])
                    task_object.accepted=True
                    task_object.accepted_time=timezone.localtime(timezone.now())
                    task_object.save()
                    return HttpResponse("<html><h1>Successfully Accepted</h1></html>")
                elif 'task_id' in request.POST:
                    comment_obj = Comments(
                        task=Task.objects.get(task_id=request.POST['task_id']),
                        user=User.objects.get(uname=request.COOKIES.get("username")),
                        text=request.POST['text']
                    )
                    comment_obj.save()
                elif 'file_id' in request.POST:
                    file_object = File.objects.get(file_id=request.POST['file_id'])
                    file_object.accepted = True
                    file_object.accepted_time=timezone.localtime(timezone.now())
                    file_object.save()
                    return HttpResponse("<html><h1>Successfully Accepted</h1></html>")
            all_tasks = Task.objects.prefetch_related('file_set').prefetch_related('comments_set').filter(
                team=Team.objects.get(team_name=team_name_t)
            ).order_by('-task_id')
            context = {
                "team": team_name_t,
                "tasks": all_tasks,
                "user": User.objects.get(uname=request.COOKIES['username']),
                "round": get_formatted_team_name(team_name_t),
                "is_admin": is_admin(request,team_name_t),
                "download": download_access(request,team_name_t),
            }
            return render(request, 'home/alltask.html', context)
        else:
            raise Http404
    else:
        return redirect("/")

@csrf_exempt
def generate_file(request, team_name_t):
    if logged_in_post(request):
        if (download_access_post(request,team_name_t)) or (File.objects.get(file_id=request.POST['file_id']).task.assigned_to==User.objects.get(uname=request.POST['username'])):
            file_object = File.objects.get(file_id=request.POST['file_id'])
            user = User.objects.get(uname=request.POST['username'])
            if file_object.task.team.team_name == team_name_t:
                syst("rm -rf app/static/files/"+user.files_path+"/*")
                syst("cp -f files/"+str(file_object.file_id)+" app/static/files/"+user.files_path)
                syst("mv -f app/static/files/"+user.files_path+"/"+str(file_object.file_id)+" "+" app/static/files/"+user.files_path+"/"+file_object.file_name)
                return HttpResponse("<html><h1>Success</h1></html>")
            else:
                return HttpResponse("<html><h1>Access denied</h1></html>")
    return HttpResponse("<html><h1>Not logged in</h1></html>")

def logout(request):
    response = HttpResponse()
    response = render(request, 'home/login.html')
    response.delete_cookie('sesid')
    response.delete_cookie('username')
    return response

@csrf_exempt
def comment(request,team_name_t):
    if logged_in_post(request):
        if read_access_post(request,team_name_t):
            comment_obj = Comments(
                task=Task.objects.get(task_id=request.POST['task_id']),
                user=User.objects.get(uname=request.POST['username']),
                text=request.POST['text']
            )
            comment_obj.save()
            return HttpResponse("<html><h1>Success</h1></html>")
        else:
            return HttpResponse("<html><h1>Access denied</h1></html>")
    else:
        return HttpResponse("<html><h1>Not logged in</h1></html>")
