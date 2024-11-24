from django.test import TestCase
from django.urls import reverse
from merchants.models import *
import datetime as dt
from django.core import mail

class Test_Merchants(TestCase):
    def setUp(self):
        # each of these tables has a relationship with Merchants
        Event.objects.create(
            event_name = "Test Furry Con",
            submissions_end = dt.date.today()+dt.timedelta(days=1),
            event_start = dt.date.today()+dt.timedelta(days=2),
            event_end = dt.date.today()+dt.timedelta(days=3),
            max_merchants = 15,
            max_party_rooms = 10,
            module_panels_enabled = True,
            module_merchants_enabled = True,
            module_performers_enabled = True,
            module_partyfloor_enabled = True,
            module_competitors_enabled = True,
        )
        Table.objects.create(key="FULL", name="Full Table")
        Table.objects.create(key="DOUB", name="Double Table")
        
    # the requests a merchant is expected to made as they sign up
    def test_applicant(self):
        
        # navigates to the merchants home page
        with self.assertNumQueries(1): # the current Event
            r = self.client.get(reverse("core:index"))
            self.assertContains(
                r, F'href="{reverse("merchants:index")}"', status_code=200
            )
            
        with self.assertNumQueries(7*2): # current event and merchant counts
            r = self.client.get(reverse("merchants:index"))
            self.assertContains(
                r, F'href="{reverse("merchants:apply")}"', status_code=200
            )
        
            # visits the blank form
            r = self.client.get(reverse("merchants:apply"))
            self.assertEquals(r.status_code, 200)
            
        # submits an invalid form, given back same form
        with self.assertNumQueries(7):
            r = self.client.post(reverse("merchants:new"), data={})
            self.assertTemplateUsed(r, 'merch-apply.html')
            self.assertEquals(r.status_code, 200)
            self.assertFormError(
                r.context['form'], "email", ['This field is required.']
            )
            self.assert_(len(r.context['form'].errors) > 0)
        # invalid merchants should not have been created
        self.assertEquals(0, Merchant.objects.count())
        
        # fills out and submits a form
        with self.assertNumQueries(12):
            my_merchant = {
                'email': 'nina@scrunk.ly',
                'legal_name': 'Nina McLegal',
                'fan_name': 'nina',
                'phone_number': 'nina',
                
                'helper_legal_name': '',
                'helper_fan_name': '',
                
                'table_size': 'FULL', # pk of Table
                'business_name': 'Example Business',
                'wares_description': 'I sell items.',
                
                'special_requests': '',
            }
            r = self.client.post(reverse("merchants:new"), data=my_merchant)
            self.assertRedirects(r, reverse('merchants:confirm'))
            
        # redirected to the confirmation page
        with self.assertNumQueries(1): # Event only
            r = self.client.get(r['Location'])
            self.assertEquals(r.status_code, 200)
            
        # one merchant is created
        [created] = Merchant.objects.all()
        self.assertEqual(created.email, my_merchant['email'])
        self.assertEqual(str(created), 'Nina McLegal (Example Business)')
        
        # the merchant gets the acknowledgement email
        self.assertEqual(mail.outbox[0].to, [my_merchant['email']])
        self.assertEqual(mail.outbox[0].subject, 'PAWCon Merchant Application')

        
        # submitting the same merchant again is considered invalid
        with self.assertNumQueries(11):
            r = self.client.post(reverse("merchants:new"), data=my_merchant)
            self.assert_(r.context["form"] is not None)
            self.assertNotEquals(r.status_code, 302)
            
        # there is still only one merchant
        [_] = Merchant.objects.all()
        
        # in all, at most one email was sent
        [_] = mail.outbox
        
        # rest of merchants apply (artificially)
        for i in range(1, Event.objects.get().max_merchants+10):
            Merchant.objects.create(
                event = Event.objects.get(),
                email = F'merchant.{i}@example.com',
                legal_name = F'Merchant #{i}',
                fan_name = F'Merchanty the {i}th',
                phone_number = F'111-111-00{i:02}',
                table_size = Table.objects.get(key='FULL'),
                business_name = F'Another Business #{i}',
                wares_description = '',
                helper_legal_name = '',
                helper_fan_name = '',
                special_requests = '',
                table_number = None,
                merchant_state = 'STATE_NEW',
                state_changed = dt.datetime.now(dt.timezone.utc),
            )
        
        # potential applicants are informed of the limit
        r = self.client.get(reverse("merchants:index"))
        self.assertContains(r, 'alert')
        self.assertContains(r, 'is currently full')
        
        r = self.client.get(reverse("merchants:apply"))
        self.assertRedirects(r, reverse('merchants:index'))
        
        r = self.client.get(reverse("merchants:new"))
        self.assertRedirects(r, reverse('merchants:index'))