from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from agmp_app.models import drug

class DrugTestCase(TestCase):
    def setUp(self):
        drug.objects.create(
            id="000",
            drug_name="Warfarin",
            drug_bank_id="DBID0000",
            state="ACTIVE",
            indication="IND",
            iupac_name="ABCXYZ")

    def test_drug_created(self):
        '''
        Test if drug entry was created with right columns filled
        '''
        new_drug = drug.objects.get(id = "000")
        self.assertEqual(new_drug.drug_name, "Warfarin")

class TestPages(TestCase):

   def setUp(self):
       self.client = Client()

   def test_home_page(self):
       url = reverse('home')
       response = self.client.get(url)
       self.assertEqual(response.status_code, 200)
       self.assertTemplateUsed(response, 'home.html')
       self.assertContains(response, 'African Genomic Medicine')
