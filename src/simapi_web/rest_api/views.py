import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from django.db import transaction
from rest_framework.decorators import action

from rest_api import serializers
from rest_api import models
from rest_api import tasks


# Create your views here.
# TODO  Add exception handling.
# Possibly have master script in while(time < final_time) and have the pauses inside the loop.


class UserViewSet(viewsets.ModelViewSet):
    """retrieve list of or create new user"""

    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()
    authentication_classes = (TokenAuthentication,)


class LoginViewSet(viewsets.ViewSet):
    """checks email and password and returns an auth token"""

    serializer_class = AuthTokenSerializer

    @staticmethod
    def create(request):
        return ObtainAuthToken().post(request)


class FmuModelViewSet(viewsets.ModelViewSet):
    """handles creating and reading model initialization parameters"""

    authentication_classes = (TokenAuthentication, SessionAuthentication)
    serializer_class = serializers.FmuModelParametersSerializer
    queryset = models.FmuModelParameters.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        data = {'model_name': self.request.data['model_name'],
                'step_size': self.request.data['step_size'],
                'final_time': self.request.data['final_time'],
                'Authorization': 'Token ' + str(self.request.auth)
                }
        transaction.on_commit(lambda: tasks.post_model.apply_async((data,), queue='web', routing_key='web'))


class InputViewSet(viewsets.ModelViewSet):
    """handles creating and reading model input parameters"""

    authentication_classes = (TokenAuthentication, SessionAuthentication)
    serializer_class = serializers.InputSerializer
    queryset = models.Input.objects.all()

    """
    create new input instance. set user as current authenticated user,
    fmu_model as current fmu_model related to user
    """

    def perform_create(self, serializer, **kwargs):
        # TODO add second get param of time/date to ensure the current model is returned
        model = models.FmuModelParameters.objects.get(model_name=self.request.data['fmu_model'])

        input_json_field = self.request.data['input']
        time_step = self.request.data['time_step']

        serializer.save(user=self.request.user, fmu_model=model, time_step=time_step, input=input_json_field)

        transaction.on_commit(lambda: tasks.post_input.apply_async((input_json_field,),
                                                                   queue='web',
                                                                   routing_key='web'))


class GetInputView(viewsets.ViewSet):

    @action(methods=['get'], detail=True)
    def retrieve_input(self, request, model=None):
        user = self.request.user
        fmu_model = models.FmuModelParameters.objects.get(model)
        time_step = self.request.data['time_step']
        queryset = models.Input.objects.all()
        user = get_object_or_404(queryset, user=user, fmu_model=fmu_model, time_step=time_step)
        serializer = serializers.InputSerializer(user)
        return HttpResponse(serializer.data)


class OutputViewSet(viewsets.ModelViewSet):
    """handles creating and reading model output parameters"""

    authentication_classes = (TokenAuthentication, SessionAuthentication)
    serializer_class = serializers.OutputSerializer
    queryset = models.Output.objects.all()

    """
    create new output instance. set user as current authenticated user,
    fmu_model as current init_model related to user
    """

    def perform_create(self, serializer, **kwargs):
        # TODO add second get param of time/date to ensure the current model is returned
        output = self.request.data
        model = models.FmuModelParameters.objects.get(model_name=output['fmu_model'])
        output_json_field = output['output']
        time_step = output['time_step']
        serializer.save(user=self.request.user, fmu_model=model, time_step=time_step,
                        output=json.dumps(output_json_field))


class FileUploadView(viewsets.ModelViewSet):
    serializer_class = serializers.UploadSerializer
    queryset = models.FileModel.objects.all()

    def post(self, request):
        file_model = models.FileModel()
        _, file = request.FILES.popitem()  # get first element of the uploaded files

        file = file[0]  # get the file from MultiValueDict

        file_model.file = file
        file_model.save()

        return HttpResponse(content_type='text/plain', content='File uploaded')
