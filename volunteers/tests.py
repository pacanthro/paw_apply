from django.test import TestCase
from django.urls import reverse
from console.templatetags.console_extras import pretty_delta
from merchants.models import Table
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
        
        Table.objects.create(key="FULL", name="Full")
        Table.objects.create(key="DOUB", name="Double")
        
        self.admin = get_user_model().objects.create_superuser(
            "testadmin"
        )
        
    def assert_ok_with_link(self, r, view_name, view_kwargs=None, attr='href'):
        self.assertContains(
            r, F'{attr}="{reverse(view_name, kwargs=view_kwargs)}"',
            status_code=200
        )
    def assert_ok_without_link(self, r, view_name, view_kwargs=None, attr='href'):
        self.assertNotContains(
            r, F'{attr}="{reverse(view_name, kwargs=view_kwargs)}"',
            status_code=200
        )
        
    # the requests a volunteer is expected to made as they sign up
    def test_typical(self):
        
        # navigates to the volunteers home page
        with self.assertNumQueries(2): # once each for the current Event
            r = self.client.get(reverse("core:index"))
            self.assert_ok_with_link(r, "volunteers:index")
            
            r = self.client.get(reverse("volunteers:index"))
            self.assert_ok_with_link(r, "volunteers:apply")
        
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
        self.assertEqual([dept.pk for dept in created.department_interest.all()], [my_volunteer['department_interest']])
        
        # submitting the same volunteer again is considered invalid
        with self.assertNumQueries(9):
            r = self.client.post(reverse("volunteers:new"), data=my_volunteer)
            self.assert_(r.context["form"] is not None)
            self.assertNotEquals(r.status_code, 302)
            
        # there is still only one volunteer
        [the_volunteer] = Volunteer.objects.all()
        
        # in all, at most one email was sent
        self.assertEqual(len(mail.outbox), 1)
        
        
        # admins act on the new volunteer
        
        self.client.force_login(self.admin)
        
        # basic navigation
        r = self.client.get(reverse("console:index"))
        self.assert_ok_with_link(r, "console:volunteers")
        
        r = self.client.get(reverse("console:volunteers"))
        self.assert_ok_with_link(r, "console:volunteer-download")
        self.assert_ok_with_link(r, "console:volunteer-dashboard")
        self.assert_ok_with_link(r, "console:volunteer-detail", {"volunteer_id": 1})
        
        r = self.client.get(reverse(
            "console:volunteer-detail", kwargs={"volunteer_id": 1}
        ))
        self.assert_ok_with_link(r, "console:volunteer-accept", {"volunteer_id": 1})
        self.assert_ok_with_link(r, "console:volunteer-decline", {"volunteer_id": 1})
        self.assert_ok_with_link(r, "console:volunteer-delete", {"volunteer_id": 1})
        self.assert_ok_without_link(r, "console:volunteer-add-task", {"volunteer_id": 1})
        
        # accept the volunteer
        r = self.client.post(reverse("console:volunteer-accept", kwargs={"volunteer_id": 1}))
        self.assertEquals(Volunteer.objects.get().volunteer_state, ApplicationState.STATE_ACCEPTED)
        self.assertRedirects(r, reverse(
            "console:volunteer-detail", kwargs={"volunteer_id": 1}
        ))
        
        self.assertEqual(mail.outbox[1].to, [my_volunteer['email']])
        self.assertEqual(mail.outbox[1].subject, 'PAWCon Volunteer Application')
        self.assertEqual(len(mail.outbox), 2)
        
        # deny another volunteer
        deny_volunteer = {
            'email': 'fail@example.com',
            'legal_name': 'Doe S.',
            'fan_name': 'd',
            'phone_number': 'd',
            'twitter_handle': 'd',
            'telegram_handle': 'd',
            'department_interest': 1, # str|int, database index of deparment
            'volunteer_history': 'd',
            'special_skills': 'd',
            'days_available': ['MON', 'TUE'],
            'time_availble': ['MORN'],
            'avail_setup': True,
            'avail_teardown': False,
        }
        r = self.client.post(reverse("volunteers:new"), data=deny_volunteer)
        self.assertRedirects(r, reverse('volunteers:confirm'))
        [deny_volunteer] = Volunteer.objects.filter(email='fail@example.com').all()
        
        r = self.client.post(reverse("console:volunteer-decline", kwargs={"volunteer_id": deny_volunteer.pk}))
        self.assertRedirects(r, reverse("console:volunteers"))
        deny_volunteer.refresh_from_db()
        self.assertEquals(deny_volunteer.volunteer_state, ApplicationState.STATE_DENIED)
        
        r = self.client.post(reverse("console:volunteer-delete", kwargs={"volunteer_id": deny_volunteer.pk}))
        self.assertRedirects(r, reverse("console:volunteers"))
        
        self.assertEqual(len(mail.outbox), 4) # interest, accept, interest, deny
        
        
        
        # actions available are now different to reflect the new state
        r = self.client.get(reverse(
            "console:volunteer-detail", kwargs={"volunteer_id": 1}
        ))
        self.assert_ok_with_link(r, "console:volunteer-add-task", {"volunteer_id": 1})
        self.assert_ok_with_link(r, "console:volunteer-delete", {"volunteer_id": 1})
        self.assert_ok_without_link(r, "console:volunteer-accept", {"volunteer_id": 1})
        self.assert_ok_without_link(r, "console:volunteer-decline", {"volunteer_id": 1})
        
        # the dashboard shows the volunteer as idle and an action to start a task
        r = self.client.get(reverse("console:volunteer-dashboard"))
        self.assert_ok_with_link(r, "console:volunteer-task-start", {"volunteer_id": 1}, attr="action")
        
        # record a volunteer beginning their task
        r = self.client.get(reverse(
            "console:volunteer-add-task", kwargs={"volunteer_id": 1}
        ))
        self.assertEquals(r.status_code, 200)
        
        task_start_time = dt.datetime.now(dt.timezone.utc)
        task_start_info = {
            'event': Event.objects.get().pk,
            'volunteer': the_volunteer.pk,
            'recorded_by': self.admin.pk,
            'task_name': 'Example task',
            'task_notes': '',
            'task_multiplier': 1.0,
            'task_start': task_start_time + dt.timedelta(days=1),
            'task_end': '',
        }
        # fails: task_start in future
        r = self.client.post(reverse(
            "console:volunteer-add-task", kwargs={"volunteer_id": the_volunteer.pk}
        ), data = task_start_info)
        [] = VolunteerTask.objects.all()
        
        task_start_info['task_start'] = task_start_time
        # success
        r = self.client.post(reverse(
            "console:volunteer-add-task", kwargs={"volunteer_id": the_volunteer.pk}
        ), data = task_start_info)
        self.assertRedirects(r, reverse(
            "console:volunteer-detail", kwargs={"volunteer_id": the_volunteer.pk}
        ))
        [the_task] = VolunteerTask.objects.all()
        
        # the dashboard shows the volunteer with the task and an action to end it
        r = self.client.get(reverse("console:volunteer-dashboard"))
        self.assert_ok_with_link(r, "console:volunteer-task-end",
                                 {"task_id": the_task.pk}, attr="action")
        
        # the volunteer detail page has a link to edit the task
        r = self.client.get(reverse(
            "console:volunteer-detail", kwargs={"volunteer_id": the_volunteer.pk}
        ))
        self.assert_ok_with_link(r, "console:volunteer-edit-task", {
            "volunteer_id": the_volunteer.pk, "task_id": the_task.pk
        })
        
        # marking the end of the task
        task_end_time = dt.datetime.now(dt.timezone.utc)
        task_end_info = {
            'task_end': task_end_time,
        }
        r = self.client.post(reverse(
            "console:volunteer-task-end", kwargs={"task_id": the_task.pk}
        ), data = {'task_end': 'wrong'})
        self.assertEquals(VolunteerTask.objects.get().task_end, None)
        
        r = self.client.post(reverse(
            "console:volunteer-task-end", kwargs={"task_id": the_task.pk}
        ), data = task_end_info)
        self.assertRedirects(r, reverse("console:volunteer-dashboard"))
        self.assertNotEquals(VolunteerTask.objects.get().task_end, None)
        
        # volunteer total hours is the same as the task hours, and is listed
        r = self.client.get(reverse(
            "console:volunteer-detail", kwargs={"volunteer_id": the_volunteer.pk}
        ))
        self.assertContains(r, pretty_delta(task_end_time - task_start_time))
        
        # alternative page for starting a task
        task_start_info2 = {
            'event': Event.objects.get().pk,
            'volunteer': the_volunteer.pk,
            'recorded_by': self.admin.pk,
            'task_name': 'task 2',
            'task_notes': '',
            'task_multiplier': 1.0,
            'task_start': dt.datetime.now(dt.timezone.utc),
        }
        # failure:
        r = self.client.post(reverse(
            "console:volunteer-task-start", kwargs={"volunteer_id": the_volunteer.pk}
        ), data = {})
        self.assertRedirects(r, reverse("console:volunteer-dashboard"))
        [_] = VolunteerTask.objects.all()
        
        # success: 
        r = self.client.post(reverse(
            "console:volunteer-task-start", kwargs={"volunteer_id": the_volunteer.pk}
        ), data = task_start_info2)
        self.assertRedirects(r, reverse("console:volunteer-dashboard"))
        [_, task2] = VolunteerTask.objects.all()
        
        # edit
        task_edit_info = {
            **task_start_info2,
            'task_multiplier': 2.0,
        }
        # failure, unchanged:
        r = self.client.post(reverse(
            "console:volunteer-edit-task", kwargs={"volunteer_id": the_volunteer.pk, "task_id": task2.pk}
        ), data = {})
        task2.refresh_from_db()
        self.assertEquals(task2.task_multiplier, 1.0)
        
        # success:
        r = self.client.post(reverse(
            "console:volunteer-edit-task", kwargs={"volunteer_id": the_volunteer.pk, "task_id": task2.pk}
        ), data = task_edit_info)
        self.assertRedirects(r, reverse(
            "console:volunteer-detail", kwargs={"volunteer_id": the_volunteer.pk}
        ))
        task2.refresh_from_db()
        self.assertEquals(task2.task_multiplier, 2.0)
        
        # deletion
        r = self.client.post(reverse(
            "console:volunteer-delete-task", kwargs={"volunteer_id": the_volunteer.pk, "task_id": task2.pk}
        ))
        self.assertRedirects(r, reverse(
            "console:volunteer-detail", kwargs={"volunteer_id": the_volunteer.pk}
        ))
        [_] = VolunteerTask.objects.all()
        
        
        # the volunteer csv is at least not empty
        r = self.client.get(reverse("console:volunteer-download"))
        self.assertContains(r, the_volunteer.email)