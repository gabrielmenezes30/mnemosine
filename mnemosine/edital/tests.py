from django.test import TestCase
from .models import Edital, CicloDeEstudo

class EditalModelTest(TestCase):
    def setUp(self):
        self.edital = Edital.objects.create(
            title="Sample Edital",
            content="This is a sample edital content."
        )

    def test_edital_creation(self):
        self.assertEqual(self.edital.title, "Sample Edital")
        self.assertEqual(self.edital.content, "This is a sample edital content.")

class CicloDeEstudoModelTest(TestCase):
    def setUp(self):
        self.ciclo = CicloDeEstudo.objects.create(
            name="Study Cycle 1",
            description="Description of study cycle 1."
        )

    def test_ciclo_creation(self):
        self.assertEqual(self.ciclo.name, "Study Cycle 1")
        self.assertEqual(self.ciclo.description, "Description of study cycle 1.")