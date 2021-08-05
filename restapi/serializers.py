from rest_framework import serializers
from backend.models import Submission, AuthCode, Professor, Year, Subject, Tag, Type
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag

    def to_representation(self, value):
        return value.name  # instead of {"name": value.name}


class SubmissionSerializer(serializers.ModelSerializer):
    authcode = serializers.CharField(source="auth_code.code")
    professor = serializers.CharField(
        source="professor.user.username", label="Professor username"
    )
    subject = serializers.SlugRelatedField(
        slug_field="slug", queryset=Subject.objects.all()
    )
    tags_writeonly = serializers.CharField(
        write_only=True, label="Tags", default=""  # input field (charfield)
    )
    tags = TagSerializer(many=True, read_only=True)  # display (list field)

    class Meta:
        model = Submission
        fields = [
            "title",
            "author",
            "year",
            "professor",
            "subject",
            "tags_writeonly",
            "tags",
            "type",
            "file",
            "authcode",
        ]

    @transaction.atomic
    def create(self, data):
        """Create the submission and use the authcode."""
        data["tags"] = data["tags_writeonly"]  # alias
        data["professor"] = data["professor"]["user"]["username"]
        data["auth_code"] = data["auth_code"]["code"]
        sub = Submission.from_form_data(data)
        AuthCode.use(sub, data["auth_code"])
        return sub

    def validate_file(self, value):
        try:
            Submission.generate_filename(1, value.name)
        except ValueError:
            raise serializers.ValidationError("Invalid filename extension")
        except AttributeError:
            raise serializers.ValidationError("File has no name")

        # I cannot set the new filename here, because we can't know the subject id
        return value

    # For backwards compatibilty with old javascript code, Submission.from_form_data
    # will only accept the ids of foreign relations
    def validate_subject(self, value):
        return value.id

    def validate_professor(self, value):
        profs = Professor.objects.filter(user__username=value)
        if profs.count() != 1:
            raise serializers.ValidationError(
                "Professor {pk} does not exist".format(pk=value)
            )
        return profs[0].id

    def validate_tags_writeonly(self, value):
        """Transform a comma-separated list of tags into an array of tag ids."""
        tags = value.split(",")
        tag_ids = []
        for tag in tags:
            new_tag = tag.strip()
            if new_tag != "":
                id = Tag.objects.get_or_create(name=new_tag)[0].id
                tag_ids.append(id)
        return tag_ids

    def validate_authcode(self, value):
        if not AuthCode.is_valid(value):
            raise serializers.ValidationError(
                'Invalid authcode "{code}"'.format(code=value)
            )
        return value


class AuthCodeSerializer(serializers.ModelSerializer):
    authorised_by = serializers.CharField(
        source="authorised_by.user.username", label="Username"
    )
    used_file = serializers.HyperlinkedRelatedField(
        view_name="submission-detail", read_only=True
    )
    password = serializers.CharField(max_length=50, write_only=True)

    class Meta:
        model = AuthCode
        fields = [
            "code",
            "purpose",
            "authorised_by",
            "authorised_datetime",
            "used_file",
            "used_datetime",
            "password",
        ]
        read_only_fields = [
            "code",
            "used_datetime",
        ]  # + ["used_file"] (already declared read-only)

    def create(self, data):
        data["username"] = data["authorised_by"]["user"]["username"]
        if authenticate(username=data["username"], password=data["password"]) is None:
            raise serializers.ValidationError("Invalid credentials")
        return AuthCode.from_form_data(data)
