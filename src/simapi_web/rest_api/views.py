import json

import polling2
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from django.db import transaction
from django_celery_results.models import TaskResult
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_api import serializers
from rest_api import models
from rest_api import tasks


def check_result_backend(model_name):
    try:
        task_result = TaskResult.objects.first()
        task_name = task_result.task_name
        task_args = task_result.task_args
        task_status = task_result.status

        if (task_name.endswith('post_model')) and (model_name in task_args) and (task_status == 'SUCCESS'):
            print("FMU Ready")
            return True
    except AttributeError:
        return False

    return False


def print_str(string):
    print(str)


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
    queryset = models.FmuModel.objects.all()

    def perform_create(self, serializer):

        if self.request.POST.get('container_id') is None:
            self.request.data['container_id'] = 'src_simulator_1'

        serializer.save(user=self.request.user, container_id=self.request.data['container_id'])

        data = {
            'model_name': self.request.data['model_name'],
            'step_size': self.request.data['step_size'],
            'final_time': self.request.data['final_time'],
            'container_id': self.request.data['container_id'],
            'Authorization': 'Token ' + str(self.request.auth)
        }

        if 'model_count' in self.request.data:
            data['model_count'] = self.request.data['model_count']

        if self.request.data['container_id'] not in self.request.data['model_name']:
            transaction.on_commit(lambda: tasks.post_model.apply_async((data,), queue='web', routing_key='web'))
            polling2.poll(
                lambda: check_result_backend(self.request.data['model_name']) is True,
                step=10,
                poll_forever=True)  # TODO need to change poll_forever and perform check to see if FMU is created
            return Response("FMU Ready", status=200)


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
        model = models.FmuModel.objects.get(model_name=self.request.data['fmu_model'])

        input_json_field = self.request.data['input_json']
        time_step = self.request.data['time_step']

        data = {
            'time_step': time_step,
            'container_id': model.container_id
        }

        serializer.save(user=self.request.user, fmu_model=model, time_step=time_step, input_json=input_json_field)

        transaction.on_commit(lambda: tasks.post_router_input.apply_async((data,),
                                                                          queue='web',
                                                                          routing_key='web'))


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
        output = self.request.data
        model = models.FmuModel.objects.get(model_name=output['fmu_model'])
        output_json_field = output['output_json']
        time_step = output['time_step']
        serializer.save(user=self.request.user, fmu_model=model, time_step=time_step,
                        output_json=json.dumps(output_json_field))


class SendFMUView(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication)

    def post(self, request, *args, **kwargs):
        data = request.data
        data['Authorization'] = str(self.request.auth)

        result = tasks.send_fmu.apply_async((data,), queue='web', routing_key='web')

        return Response(result.get())


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


class HostNameViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.HostNameSerializer
    queryset = models.ContainerHostNames.objects.all()

    def perform_create(self, serializer):
        serializer.save(hostname=self.request.data['hostname'])
