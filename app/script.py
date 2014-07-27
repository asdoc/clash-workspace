from app.models import User
from os import system as sys
def user_folders():
	users = User.objects.all()
	for user in users:
		a = sys("mkdir -p app/static/files/"+user.files_path)
def clean_up():
	sys("rm -rf files/*")
	sys("rm -rf app/static/files/*")
