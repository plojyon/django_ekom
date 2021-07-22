from rest_framework import serializers

#from django.contrib.auth.models import User, Group

#class UserSerializer(serializers.HyperlinkedModelSerializer):
#    class Meta:
#        model = User
#        fields = ['url', 'username', 'email', 'groups']


#class GroupSerializer(serializers.HyperlinkedModelSerializer):
#    class Meta:
#        model = Group
#		fields = ['url', 'name']

from backend.models import Submission

class SubmissionSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Submission
		fields = ['title', 'author', 'year', 'prof_name', 'subject_name', 'tags_arr', 'type', 'url']
