from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from rest_api.models import User, FmuModel


# TODO write tests


class FmuModelViewTest(APITestCase):
    """
    Test FmuModelParameters View
    """
    def setUp(self) -> None:
        self.test_user = User(name='test_user',
                              email='test@test.com',
                              password='test user 88')

        self.test_user.save()

        self.token = Token.objects.create(
            user=self.test_user
        )

    def test_Model_Initialization(self):
        self.client.force_login(user=self.test_user)

        data = {
            "model_name": "test",
            "step_size": "800",
            "final_time": "72.0"
        }

        response = self.client.post(
            '/init_model/',
            data=data,
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token.key
        )

        self.assertEqual(response.status_code, 201)


class InputViewTest(APITestCase):
    """
    Test Input View
    """
    def setUp(self) -> None:
        self.test_user = User(name='test_user',
                              email='test@test.com',
                              password='test user 88')

        self.test_user.save()

        self.token = Token.objects.create(
            user=self.test_user
        )

        self.model = FmuModel(
            model_name="test_model",
            user=self.test_user,
            step_size=600,
            final_time=72.0
        )

        self.model.save()

    def test_input_create(self):
        self.client.force_login(user=self.test_user)

        data = {
            'user': self.test_user.email,
            'fmu_model': self.model.model_name,
            'time_step': 600,
            'yshade': 1.0
        }

        response = self.client.post(
            '/input/',
            data=data,
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token.key
        )

        self.assertEqual(response.status_code, 201)


class OutputViewTest(APITestCase):
    """
    Test Output View
    """
    def setUp(self) -> None:
        self.test_user = User(name='test_user',
                              email='test@test.com',
                              password='test user 88')

        self.test_user.save()

        self.token = Token.objects.create(
            user=self.test_user
        )

        self.model = FmuModel(
            model_name="test_model",
            user=self.test_user,
            step_size=600,
            final_time=72.0
        )

        self.model.save()

    def test_output_create(self):
        self.client.force_login(user=self.test_user)

        data = {
            'user': self.test_user.email,
            'fmu_model': self.model.model_name,
            "time_step": "800",
            "yshade": "2.4",
            "dry_bulb": "5.0",
            "troo": "7.0",
            "isolext": "4.01",
            "sout": "6.89",
            "zonesens": "9.111",
            "cool_rate": "18.9"
        }

        response = self.client.post(
            '/output/',
            data=data,
            format='json',
            HTTP_AUTHORIZATION='Token ' + self.token.key
        )

        self.assertEqual(response.status_code, 201)
