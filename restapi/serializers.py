from rest_framework import serializers
from backend.models import Submission, AuthCode, Professor, Year, Subject, Tag, Type


class SubmissionSerializer(serializers.ModelSerializer):
    authcode = serializers.SlugRelatedField(
        slug_field="code", queryset=AuthCode.objects.all(), source="auth_code"
    )
    professor = serializers.SlugRelatedField(
        slug_field="id", queryset=Professor.objects.all()
    )
    subject = serializers.SlugRelatedField(
        slug_field="slug", queryset=Subject.objects.all()
    )
    tags = serializers.CharField(source="tags_arr")

    class Meta:
        model = Submission
        fields = [
            "title",
            "author",
            "year",
            "professor",
            "subject",
            "tags",
            "type",
            "file",
            "authcode",
        ]

    def create(self, data):
        """Set default values for unset fields and create object."""
        if "tags" not in data:
            data["tags"] = []
        AuthCode.use(sub, data["auth_code"])
        sub = Submission.from_form_data(data)
        return sub

    def validate_file(self, value):
        print("Validating file:", value)
        try:
            Submission.generate_filename(1, value.name)
        except ValueError:
            raise serializers.ValidationError("Invalid filename extension")
        # I cannot set the new filename here, because we can't know the subject id
        return value

    # For backwards compatibilty with old javascript code, Submission.from_form_data
    # will only accept the ids of foreign relations
    def validate_subject(self, value):
        return value.id

    def validate_professor(self, value):
        return value.id

    def validate_tags(self, value):
        """Transform a comma-separated list of tags into an array of tag ids."""
        tags = value.split(",")
        tag_ids = []
        for tag in tags:
            new_tag = tag.strip()
            if new_tag != "":
                id = Tag.objects.get_or_create(name=new_tag)[0].id
                tag_ids.append(id)
        print("Validated tags into:", tag_ids)
        return tag_ids

    def validate_authcode(self, value):
        if not AuthCode.is_valid(value.code):
            raise serializers.ValidationError("Invalid authcode: " + str(value.code))
        return value.code


class AuthCodeSerializer(serializers.ModelSerializer):
    authorised_by = serializers.SlugRelatedField(
        slug_field="username", queryset=Professor.objects.all()
    )
    used_file = serializers.StringRelatedField(read_only=True)
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
        data["username"] = data["authorised_by"].username
        try:
            Professor.authenticate(data["username"], data["password"])
        except:
            raise serializers.ValidationError("Invalid credentials")
        return AuthCode.from_form_data(data)
