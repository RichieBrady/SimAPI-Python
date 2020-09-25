import graphene
from graphene_django import DjangoObjectType

from django.db.models import Q

from . import models


class UserType(DjangoObjectType):
    class Meta:
        model = models.User


class FmuModelType(DjangoObjectType):
    class Meta:
        model = models.FmuModel


class InputType(DjangoObjectType):
    class Meta:
        model = models.Input
        filter_fields = {'fmu_model': ['exact'],
                         'time_step': ['exact']}


class OutputType(DjangoObjectType):
    class Meta:
        model = models.Output
        filter_fields = {'fmu_model': ['exact'],
                         'time_step': ['exact']}


class Query(object):
    all_users = graphene.List(UserType)
    
    fmu_models = graphene.List(FmuModelType, model_n=graphene.String())
    fmu_model = graphene.List(FmuModelType, model_n=graphene.String())
    
    inputs = graphene.List(InputType, model_n=graphene.String(), t_step=graphene.Int())

    outputs = graphene.List(OutputType, model_n=graphene.String(), t_step=graphene.Int())

    def resolve_all_users(self, info, **kwargs):
        return models.User.objects.all()

    def resolve_fmu_models(self, info, model_n=None, **kwargs):
        if model_n:
            filter = (
                    Q(model_name__icontains=model_n)
            )
            return models.FmuModel.objects.filter(filter)

        return models.FmuModel.objects.all()
    
    def resolve_fmu_model(self, info, model_n=None, **kwargs):
        if model_n:
            filter = (
                    Q(model_name=model_n)
            )
            return models.FmuModel.objects.filter(filter)

        return models.FmuModel.objects.all()

    def resolve_inputs(self, info, model_n=None, t_step=None, **kwargs):
        if model_n and t_step:
            filter = (
                    Q(fmu_model=model_n) &
                    Q(time_step=t_step)
            )
            return models.Input.objects.filter(filter)

        if model_n:
            filter = (
                    Q(fmu_model=model_n)
            )
            return models.Input.objects.filter(filter)

        if t_step:
            filter = (
                Q(time_step=t_step)
            )
            return models.Input.objects.filter(filter)

        return models.Input.objects.all()

    def resolve_outputs(self, info, model_n=None, t_step=None, **kwargs):
        if model_n and t_step:
            filter = (
                    Q(fmu_model=model_n) &
                    Q(time_step=t_step)
            )
            return models.Output.objects.filter(filter)

        if model_n:
            filter = (
                Q(fmu_model=model_n)
            )
            return models.Output.objects.filter(filter)

        if t_step:
            filter = (
                Q(time_step=t_step)
            )
            return models.Output.objects.filter(filter)

        return models.Output.objects.all()
