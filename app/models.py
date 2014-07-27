from django.db import models

class Team(models.Model):
	team_id = models.AutoField(primary_key=True)
	team_name = models.CharField(max_length=30)
	def __unicode__(self):
	    return self.team_name

class User(models.Model):
	user_id = models.AutoField(primary_key = True)
	uname = models.CharField(max_length=20)
	passwd = models.CharField(max_length=20)
	is_admin = models.BooleanField(default=False)
	ses_id = models.CharField(max_length=16)
	files_path = models.CharField(max_length=16)
	team = models.ForeignKey(Team)
	contribution_count = models.IntegerField(default=0)
	last_contribution_date = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
	    return self.uname
	
class Task(models.Model):
	task_id = models.AutoField(primary_key=True)
	task_name = models.CharField(max_length=50)
	tags = models.CharField(max_length=150)
	team = models.ForeignKey(Team)
	created_by = models.ForeignKey(User, related_name="created_by")
	assigned_to = models.ForeignKey(User, related_name="assigned_to")
	
	created_time = models.DateTimeField(auto_now_add=True)
	deadline_time = models.DateTimeField()
	submittion_time = models.DateTimeField(auto_now_add=True)
	accepted_time = models.DateTimeField(auto_now_add=True)
	last_modified_time = models.DateTimeField(auto_now_add=True)
	
	submitted = models.BooleanField(default=False)
	accepted = models.BooleanField(default=False)
	def __unicode__(self):
	    return self.task_name
	
class MOM(models.Model):
	mom_id = models.AutoField(primary_key=True)
	subject = models.CharField(max_length=200)
	text = models.CharField(max_length=2000)
	team = models.ForeignKey(Team)
	created_by = models.ForeignKey(User)
	def __unicode__(self):
		return self.subject
	    
class Comments(models.Model):
	comment_id = models.AutoField(primary_key=True)
	task = models.ForeignKey(Task)
	user = models.ForeignKey(User)
	date = models.DateTimeField(auto_now_add=True)
	text = models.CharField(max_length=1000)
	def __unicode__(self):
		return str(self.comment_id)
		
class File(models.Model):
	file_id = models.AutoField(primary_key=True)
	file_name = models.CharField(max_length=30)
	task = models.ForeignKey(Task)
	accepted = models.BooleanField(default=False)
	submitted_time = models.DateTimeField(auto_now_add=True)
	accepted_time = models.DateTimeField(auto_now_add=True)
	def __unicode__(self):
		return self.file_name
