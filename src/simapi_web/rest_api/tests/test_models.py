from django.test import TestCase
from rest_api.models import Input, Output, User, FmuModel


class UserTestCase(TestCase):
    """
    Test user and super user creation
    """
    def test_user(self):
        self.test_user = User.objects.create(
            name='test user',
            email='testuser@test.com',
            password='test user 88'
        )

        self.assertEquals(
            User.objects.count(),
            1
        )

        self.assertEquals(
            self.test_user.get_full_name(),
            self.test_user.name
        )

        self.assertEquals(
            self.test_user.get_short_name(),
            self.test_user.name
        )

        self.assertEquals(
            self.test_user.__str__(),
            self.test_user.email
        )

        self.super_user = User.objects.create_superuser(
            name='super_user',
            email='testsuper@test.com',
            password='super user 88'
        )

        self.assertEquals(
            User.objects.count(),
            2
        )

        self.assertTrue(
            self.super_user.is_superuser
        )
        self.assertTrue(
            self.super_user.is_staff
        )


class FmuModelTestCase(TestCase):
    """
    Test case for FmuModelParameters model
    """
    def test_model_initialization(self):
        self.user = User.objects.create(
            name='test_user',
            email='testuser@test.com',
            password='test user 88'
        )

        self.assertEquals(
            FmuModel.objects.count(),
            0
        )

        self.model = FmuModel.objects.create(
            model_name="test_model",
            user=self.user,
            step_size=600,
            final_time=72.0
        )

        self.assertEquals(
            self.model.__str__(),
            self.model.model_name
        )

        self.assertEquals(
            FmuModel.objects.count(),
            1
        )

        FmuModel.objects.create(
            model_name="test_model1",
            user=self.user,
            step_size=800,
            final_time=82.0
        )

        self.assertEquals(
            FmuModel.objects.count(),
            2
        )


class InputTestCase(TestCase):
    """
    Test case for Input model
    """
    def test_input(self):
        # input needs user
        self.user = User.objects.create(
            name='test_user',
            email='testuser@test.com',
            password='test user 88'
        )

        # and model
        self.model = FmuModel.objects.create(
            model_name="test_model",
            user=self.user,
            step_size=600,
            final_time=72.0
        )

        self.assertEquals(
            Input.objects.count(),
            0
        )

        Input.objects.create(
            user=self.user,
            fmu_model=self.model,
            time_step=600,
            yshade=1.0
        )

        self.assertEquals(
            Input.objects.count(),
            1
        )


class OutputTestCase(TestCase):
    """
    Test case for Output model
    """
    def test_output(self):
        # input needs user
        self.user = User.objects.create(
            name='test_user',
            email='testuser@test.com',
            password='test user 88'
        )
        # and model
        self.model = FmuModel.objects.create(
            model_name="test_model",
            user=self.user,
            step_size=600,
            final_time=72.0
        )

        self.assertEquals(
            Output.objects.count(),
            0
        )
        Output.objects.create(
            user=self.user,
            fmu_model=self.model,
            time_step=600,
            yshade=1.0,
            dry_bulb=1.2,
            troo=1.5,
            isolext=1.6,
            sout=1.7,
            zonesens=1.8,
            cool_rate=1.9
        )
        Output.objects.create(
            user=self.user,
            fmu_model=self.model,
            time_step=800,
            yshade=1.2,
            dry_bulb=1.4,
            troo=1.8,
            isolext=1.9,
            sout=1.2,
            zonesens=1.3,
            cool_rate=1.6
        )
        self.assertEquals(
            Output.objects.count(),
            2
        )
