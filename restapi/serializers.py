from rest_framework import serializers

# from django.contrib.auth.models import User, Group

# class UserSerializer(serializers.HyperlinkedModelSerializer):
#    class Meta:
#        model = User
#        fields = ['url', 'username', 'email', 'groups']


# class GroupSerializer(serializers.HyperlinkedModelSerializer):
#    class Meta:
#        model = Group
# 		fields = ['url', 'name']

from backend.models import Submission, AuthCode, Professor, Year, Subject, Tag, Type


class SubmissionSerializer(serializers.Serializer):
    file = serializers.FileField()
    title = serializers.CharField(max_length=150)
    author = serializers.CharField(max_length=50)
    year = serializers.ChoiceField(choices=Year.choices, default=Year.OTHER)
    professor = serializers.IntegerField(label="Professor id")
    subject = serializers.CharField(max_length=10, label="Subject slug")
    tags = serializers.CharField(max_length=50, required=False)
    type = serializers.ChoiceField(choices=Type.choices, default=Type.OTHER)
    authcode = serializers.CharField(max_length=50)

    def to_representation(self, instance):
        return {
            "title": instance.title,
            "author": instance.author,
            "year": instance.year,
            "professor": instance.professor.full_name,
            "subject": instance.subject.slug,
            "tags": instance.tags_arr,
            "type": instance.type_name,
            "url": instance.url,
        }

    def create(self, data):
        if "tags" not in data:
            data["tags"] = []
        sub = Submission.from_form_data(data)
        AuthCode.use(sub, data["authcode"])
        return sub

    def validate_file(self, value):
        try:
            Submission.generate_filename(1, value.name)
        except ValueError:
            raise serializers.ValidationError("Invalid filename extension")
        # I cannot set the new filename here, because we can't know the subject id
        return value

    def validate_subject(self, value):
        if Subject.objects.filter(slug=value).count() != 1:
            raise serializers.ValidationError("Invalid subject slug: " + str(value))
        # slug -> id
        return Subject.objects.get(slug=value).id

    def validate_professor(self, value):
        if Professor.objects.filter(pk=value).count() != 1:
            raise serializers.ValidationError("Invalid professor id: " + str(value))
        return value

    def validate_tags(self, value):
        tags = value.split(",")
        tag_ids = []
        for tag in tags:
            new_tag = tag.strip()
            if new_tag != "":
                id = Tag.object.get_or_create(name=new_tag).id
                tag_ids.append(id)
        return tag_ids

    def validate_authcode(self, value):
        if not AuthCode.is_valid(value):
            raise serializers.ValidationError("Invalid authcode: " + str(value))
        return value


class AuthCodeSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField(max_length=50)
    purpose = serializers.CharField(max_length=200)

    def to_representation(self, instance):
        return {
            "code": instance.code,
            "purpose": instance.purpose,
            "authorised_by": instance.authorised_by.full_name,
            "authorised_datetime": instance.authorised_datetime,
            "used_file": instance.used_file.title if instance.used_file else None,
            "used_datetime": instance.used_datetime,
        }

    def create(self, data):
        try:
            Professor.authenticate(data["username"], data["password"])
        except:
            raise serializers.ValidationError("Invalid credentials")
        return AuthCode.from_form_data(data)

    def update(self):
        raise NotImplementedError("ne gre sori")
