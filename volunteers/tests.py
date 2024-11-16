from django.test import TestCase
from django.urls import reverse
from volunteers.models import *
import datetime as dt
from django.core import mail

class Test_Volunteers(TestCase):
    def setUp(self):
        # each of these tables has a relationship with Volunteer
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
        Department.objects.create(
            department_name="Department A", description="Test department", order=1
        )
        DaysAvailable.objects.create(
            key="MON", name="Day 1 / Monday", order=1,
            available_scheduling=True, available_party=True, party_only=False
        )
        DaysAvailable.objects.create(
            key="TUE", name="Day 2 / Tuesday", order=1,
            available_scheduling=True, available_party=True, party_only=False
        )
        TimesAvailable.objects.create(
            key="MORN", name="8AM ~ 11AM / Morning", order=1,
        )
        
    # the requests a volunteer is expected to made as they sign up
    def test_typical(self):
        
        # navigates to the volunteers home page
        with self.assertNumQueries(2): # once each for the current Event
            r = self.client.get(reverse("core:index"))
            self.assertContains(
                r, F'href="{reverse("volunteers:index")}"', status_code=200
            )
            
            r = self.client.get(reverse("volunteers:index"))
            self.assertContains(
                r, F'href="{reverse("volunteers:apply")}"', status_code=200
            )
        
        # visits the blank form
        with self.assertNumQueries(4): # Event, Department, Days, Times
            r = self.client.get(reverse("volunteers:apply"))
            self.assertEquals(r.status_code, 200)
            
        # submits an invalid form, given back same form
        with self.assertNumQueries(4):
            r = self.client.post(reverse("volunteers:new"), data={})
            self.assertTemplateUsed(r, 'volunteer-apply.html')
            self.assertEquals(r.status_code, 200)
            self.assertFormError(
                r.context['form'], "email", ['This field is required.']
            )
            self.assert_(len(r.context['form'].errors) > 0)
        # invalid volunteer should not have been created
        self.assertEquals(0, Volunteer.objects.count())
        
        # fills out and submits a form
        with self.assertNumQueries(14):
            my_volunteer = {
                'email': 'nina@scrunk.ly',
                'legal_name': 'Nina McLegal',
                'fan_name': 'nina',
                'phone_number': 'nina',
                'twitter_handle': 'nina',
                'telegram_handle': 'nina',
                'department_interest': 1, # str|int, database index of deparment
                'volunteer_history': 'nina',
                'special_skills': 'nina',
                'days_available': ['MON', 'TUE'],
                'time_availble': ['MORN'],
                'avail_setup': True,
                'avail_teardown': False,
            }
            r = self.client.post(reverse("volunteers:new"), data=my_volunteer)
            self.assertRedirects(r, reverse('volunteers:confirm'))
            
        # redirected to the confirmation page
        with self.assertNumQueries(1): # Event only
            r = self.client.get(r['Location'])
            self.assertEquals(r.status_code, 200)
            
        # one volunteer is created
        [created] = Volunteer.objects.all()
        self.assertEqual(created.email, my_volunteer['email'])
        self.assertEqual(str(created), 'nina (Nina McLegal)')
        
        # the volunteer gets the acknowledgement email
        self.assertEqual(mail.outbox[0].to, [my_volunteer['email']])
        self.assertEqual(mail.outbox[0].subject, 'PAWCon Volunteer Application')
        
        # volunteer's m2m relations are created
        self.assertEqual([day.key for day in created.days_available.all()], my_volunteer['days_available'])
        self.assertEqual([t.key for t in created.time_availble.all()], my_volunteer['time_availble'])
        self.assertEqual([dept.id for dept in created.department_interest.all()], [my_volunteer['department_interest']])
        
        # submitting the same volunteer again is considered invalid
        with self.assertNumQueries(9):
            r = self.client.post(reverse("volunteers:new"), data=my_volunteer)
            self.assert_(r.context["form"] is not None)
            self.assertNotEquals(r.status_code, 302)
            
        # there is still only one volunteer
        [_] = Volunteer.objects.all()
        
        # in all, at most one email was sent
        self.assertEqual(len(mail.outbox), 1)