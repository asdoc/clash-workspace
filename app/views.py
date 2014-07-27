from django.shortcuts import render_to_response, render, redirect
from django.views.decorators.csrf import csrf_exempt
from app.models import User
from django.http import HttpResponse, Http404
from app.models import Team,User,Task,MOM, Comments, File
from datetime import datetime
from os import system as syst

@csrf_exempt
def logged_in(request):
	if not "sesid" in request.COOKIES.keys():
		return False
	return User.objects.filter(
		uname=request.COOKIES.get("username"),
		ses_id=request.COOKIES.get("sesid")
	).exists()

@csrf_exempt
def is_admin(request):
	return User.objects.filter(
		uname=request.COOKIES.get("username"),
		ses_id=request.COOKIES.get("sesid"),
		is_admin=True
	).exists()

@csrf_exempt
def validate_round(request,team_number):
	user = User.objects.filter(
		uname=request.COOKIES.get("username"),
		ses_id=request.COOKIES.get("sesid")
	).get()
	if user.is_admin == True:
		return True
	else:
		if team_number == 0 and str(user.team)=="round1":
			return True
		elif team_number == 1 and str(user.team)=="round2":
			return True
		elif team_number == 2 and str(user.team)=="swifttyper":
			return True
		else:
			return False
		
@csrf_exempt
def logged_in_post(request):
	return User.objects.filter(
		uname=request.POST["username"],
		ses_id=request.POST["sesid"]
	).exists()

@csrf_exempt
def is_admin_post(request):
	return User.objects.filter(
		uname=request.POST["username"],
		ses_id=request.POST["sesid"],
		is_admin=True
	).exists()

@csrf_exempt
def validate_round_post(request,team_number):
	user = User.objects.filter(
		uname=request.POST["username"],
		ses_id=request.POST["sesid"]
	).get()
	if user.is_admin == True:
		return True
	else:
		if team_number == 0 and str(user.team)=="round1":
			return True
		elif team_number == 1 and str(user.team)=="round2":
			return True
		elif team_number == 2 and str(user.team)=="swifttyper":
			return True
		else:
			return False


def get_team_name(team_number):
	if team_number == 0:
		return "round1"
	elif team_number == 1:
		return "round2"
	elif team_number == 2:
		return "swifttyper"
	else:
		return None
		
def get_formatted_team_name(team_number):
	if team_number == 0:
		return "Round1"
	elif team_number == 1:
		return "Round2"
	elif team_number == 2:
		return "SwiftTyper"
	else:
		return None

def get_team_number(team_name):
	if team_name=="round1":
		return 0
	elif team_name=="round2":
		return 1
	elif team_name=="swifttyper":
		return 2
	else:
		return None
		
@csrf_exempt
def home(request):
	if request.method=='POST':
		username = request.POST['username']
		password = request.POST['password']

		if User.objects.filter(uname=username, passwd=password).exists():
			context = {}
			response = HttpResponse()
			if User.objects.filter(uname=username, passwd=password, is_admin=True).exists():
				response = render(request, 'home/choice.html', context)
			else:
				team = User.objects.filter(uname=username, passwd=password).get().team
				team = str(team)
				context = {
					"team": str(get_team_number(team)),
					"round": get_formatted_team_name(team_number),
				}
				response = render(request, 'home/home.html', context)
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
			return HttpResponse("<html>Invalid Details</html>")
	elif logged_in(request):
		if is_admin(request):
			context = {}
			return render(request, 'home/choice.html',context)
		else:
			team = User.objects.filter(
				uname=request.COOKIES.get("username"),
				ses_id=request.COOKIES.get("sesid")
			).get().team
			team = str(team)
			context = {
				"team": str(get_team_number(team)),
				"round": get_formatted_team_name(team_number),
			}
			return render(request, 'home/home.html',context)
	else:
		return render(request, 'home/login.html')
		
@csrf_exempt
def feeds(request, team_number):
	team_number=int(team_number)
	if logged_in(request) and validate_round(request,team_number):
		if request.method=="POST":
			comment_obj = Comments(
				task=Task.objects.get(task_id=request.POST['task_id']),
				user=User.objects.get(uname=request.COOKIES.get("username")),
				text=request.POST['text']
			)
			comment_obj.save()
		all_tasks = Task.objects.prefetch_related('comments_set').filter(team=Team.objects.get(team_name=get_team_name(team_number))).order_by('-last_modified_time')
		context = {
			"tasks": all_tasks,
			"team": str(team_number),
			"isadmin": is_admin(request),
			"round": get_formatted_team_name(team_number),
		}
		return render(request, 'home/feed.html', context)
	else:
		raise Http404

@csrf_exempt
def mom(request, team_number):
	team_number=int(team_number)
	if logged_in(request) and validate_round(request, team_number):
		all_moms = MOM.objects.filter(team=Team.objects.get(team_name=get_team_name(team_number)))
		context = {
			"moms": all_moms,
			"team": str(team_number),
			"round": get_formatted_team_name(team_number),
		}
		return render(request,'home/mom.html', context)

@csrf_exempt
def cmom(request, team_number):	
	team_number = int(team_number)
	if logged_in(request) and validate_round(request,team_number):
		if request.method=='POST':
			mom_object = MOM(
				subject=request.POST['subject'],
				text=request.POST['text'],
				team=Team.objects.filter(team_name = get_team_name(team_number)).get(),
				created_by=User.objects.filter(uname=request.COOKIES.get("username")).get()
			)
			mom_object.save()
			return HttpResponse("<html>Successfully saved</html>")
		else:
			context = {"team": team_number}
			return render(request, 'home/cmom.html', context)
	else:
		raise Http404

@csrf_exempt	
def tasks(request, team_number):
	team_number = int(team_number)
	
@csrf_exempt	
def ctasks(request, team_number):
	team_number = int(team_number)
	if logged_in(request) and is_admin(request):
		if request.method=='POST':
			task_object = Task(
				task_name=request.POST['task_name'],
				tags=request.POST['tags'],
				team=Team.objects.filter(team_name=get_team_name(team_number)).get(),
				created_by=User.objects.filter(uname=request.COOKIES['username']).get(),
				assigned_to=User.objects.filter(uname=request.POST['assigned_to']).get(),
				deadline_time=request.POST['deadline']
			)
			task_object.save()
			return HttpResponse("<html>Successfully saved</html>")
		else:
			team_users = User.objects.filter(
				team=Team.objects.get(team_name=get_team_name(team_number)),
				is_admin=False
			)
			context = {
				"team": team_number,
				"users": team_users,
				"round": get_formatted_team_name(team_number),
			}
			return render(request, 'home/ctasks.html', context)
	else:
		raise Http404
		
@csrf_exempt
def accept_task(request, team_number):
	team_number = int(team_number)
	if request.method=="POST":
		if logged_in(request) and is_admin(request):
			task_object=Task.objects.get(task_id=request.POST['task_id'])
			task_object.accepted_time=datetime.now()
			task_object.last_modified_time=datetime.now()
			task_object.accepted=True
			task_object.save()
			return HttpResponse("<html>Successfully accepted</html>")
			
@csrf_exempt
def submit_task(request, team_number):
	team_number = int(team_number)
	if logged_in(request) and validate_round(request,team_number):
		if request.method=="POST":
			task_object=Task.objects.get(task_id=request.POST['task_id'])
			task_object.submittion_time=datetime.now()
			task_object.last_modified_time=datetime.now()
			task_object.submitted=True
			task_object.save()
			
			uploaded_file = request.FILES['file_submit']
			file_text = uploaded_file.read()
			file_object=File(file_name=uploaded_file.name,task=task_object)
			file_object.save()
			
			with open('files/'+str(file_object.file_id),'w') as f:
				f.write(file_text)
			
			return HttpResponse("<html>Successfully submitted</html>")
		else:
			all_tasks = Task.objects.filter(assigned_to=User.objects.get(uname=request.COOKIES.get("username")))
			context = {
				"tasks": all_tasks,
				"team": str(team_number),
				"round": get_formatted_team_name(team_number),
			}
			return render(request, 'home/tasks.html', context)
	else:
		raise Http404			

@csrf_exempt
def mytask(request, team_number):
	team_number = int(team_number)
	if logged_in(request) and validate_round(request,team_number):
		if request.method=='POST':
			task_object=Task.objects.get(
				assigned_to=User.objects.get(uname=request.COOKIES['username']),
				task_id=request.POST['task_id']
			)
			task_object.submittion_time=datetime.now()
			task_object.last_modified_time=datetime.now()
			task_object.submitted=True
			task_object.save()
			
			uploaded_file = request.FILES['file_submit']
			file_text = uploaded_file.read()
			
			if File.objects.filter(task=task_object,file_name=uploaded_file.name).exists():
				file_object=File.objects.get(task=task_object,file_name=uploaded_file.name)
				file_object.accepted=False
				file_object.submitted_time=datetime.now()
				file_object.save()
			else:
				file_object=File(file_name=uploaded_file.name,task=task_object)
				file_object.save()
			
			with open('files/'+str(file_object.file_id),'w') as f:
				f.write(file_text)

		my_tasks = Task.objects.prefetch_related('file_set').filter(
			assigned_to=User.objects.get(uname=request.COOKIES.get("username")),
			team=Team.objects.get(team_name=get_team_name(team_number))
		)
		
		context = {
			"team": str(team_number),
			"tasks": my_tasks,
			"user": User.objects.get(uname=request.COOKIES['username']),
			"round": get_formatted_team_name(team_number),
		}
		return render(request, 'home/mytask.html', context)
	else:
		return Http404

@csrf_exempt
def alltask(request, team_number):
	team_number = int(team_number)
	if logged_in(request) and validate_round(request,team_number):
		if request.method=='POST':
			if 'task_id' in request.POST and 'accept' in request.POST:
				task_object = Task.objects.get(task_id=request.POST['task_id'])
				task_object.accepted=True
				task_object.accepted_time=datetime.now()
				task_object.save()
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
				file_object.accepted_time=datetime.now()
				file_object.save()
			
		all_tasks = Task.objects.prefetch_related('file_set').prefetch_related('comments_set').filter(
			team=Team.objects.get(team_name=get_team_name(team_number))
		)
		context = {
			"team": str(team_number),
			"tasks": all_tasks,
			"user": User.objects.get(uname=request.COOKIES['username']),
			"round": get_formatted_team_name(team_number),
		}
		return render(request, 'home/alltask.html', context)
	else:
		return Http404
	
@csrf_exempt	
def generate_file(request, team_number):
	team_number = int(team_number)
	syst("pwd")
	print "username "+request.POST['username']
	print "file_id "+request.POST['file_id']
	print "sesid "+request.POST['sesid']
	if logged_in_post(request) and validate_round_post(request,team_number):
		file_object = File.objects.get(file_id=request.POST['file_id'])
		user = User.objects.get(uname=request.POST['username'])
		if file_object.task.team.team_name == get_team_name(team_number):
			print ("rm -rf app/static/files/"+user.files_path+"/*")
			print ("cp -f files/"+str(file_object.file_id)+" app/static/files/"+user.files_path)
			print ("mv -f app/static/files/"+user.files_path+"/"+str(file_object.file_id)+" "+" app/static/files/"+user.files_path+"/"+file_object.file_name)

			syst("rm -rf app/static/files/"+user.files_path+"/*")
			syst("cp -f files/"+str(file_object.file_id)+" app/static/files/"+user.files_path)
			syst("mv -f app/static/files/"+user.files_path+"/"+str(file_object.file_id)+" "+" app/static/files/"+user.files_path+"/"+file_object.file_name)
			return HttpResponse("<html>Success</html>")
		else:
			return HttpResponse("<html>Access denied</html>")
	return HttpResponse("<html>Not logged in</html>")
