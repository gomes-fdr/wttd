from django.core import mail
from django.test import TestCase
from eventex.subscriptions.forms import SubscriptionForm

class SubscribeTest(TestCase):
    def setUp(self):
        self.resp = self.client.get('/inscricao/')
    def test_get(self):
        """Get /inscricao/ must return status code 200"""
        self.assertEqual(200, self.resp.status_code)
    def test_template(self):
        """Must use subscriptions/subscription_form.html """
        self.assertTemplateUsed(self.resp, 'subscriptions/subscription_form.html')

    def test_html(self):
        """Html must contain input tags"""
        self.assertContains(self.resp, '<form')
        self.assertContains(self.resp, '<input', 6)
        self.assertContains(self.resp, 'type="text"')
        self.assertContains(self.resp, 'type="email"')
        self.assertContains(self.resp, 'type="submit"')

    def test_csrf(self):
        """Html must contain CSRF tag """
        self.assertContains(self.resp, 'csrfmiddlewaretoken')

    def test_has_form(self):
        """Context must have subscription form"""
        form = self.resp.context['form']
        self.assertIsInstance(form, SubscriptionForm)

    def test_form_has_fields(self):
        """Form must have 4 fields."""
        form = self.resp.context['form']
        self.assertSequenceEqual(['name', 'cpf', 'email', 'phone'], list(form.fields))

class SubscribePostTest(TestCase):
    def setUp(self):
        data = dict(name='Fabiano Gomes', cpf='12345678901', 
                email='gomes.fdr@gmail.com', phone='51-99543-2916')
        self.resp = self.client.post('/inscricao/', data)

    def test_post(self):
        """Valid POST should redirect to /incricao/"""
        self.assertEqual(302, self.resp.status_code)

    def test_subscribe_email(self):
        self.assertEqual(1, len(mail.outbox))

    def test_subscription_email_subject(self):
        email = mail.outbox[0]
        expect = 'Confirmação de inscrição'
        self.assertEqual(expect, email.subject)

    def test_subscription_emal_from(self):
        email = mail.outbox[0]
        expect = 'contato@eventex.com'
        self.assertEqual(expect, email.from_email)

    def test_subscription_emal_to(self):
        email = mail.outbox[0]
        expect = ['contato@eventex.com', 'gomes.fdr@gmail.com']
        self.assertEqual(expect, email.to)

    def test_subscriptio_email_body(self):
        email = mail.outbox[0]
        self.assertIn('Fabiano Gomes', email.body)
        self.assertIn('12345678901', email.body)
        self.assertIn('gomes.fdr@gmail.com', email.body)
        self.assertIn('51-99543-2916', email.body)

class SubscribeInvalidPost(TestCase):
    def setUp(self):
        self.resp =  self.client.post('/inscricao/', {})
    def test_post(self):
        """Invalid POST should not redirect"""
        self.assertEqual(200, self.resp.status_code)

    def test_template(self):
        self.assertTemplateUsed(self.resp, 'subscriptions/subscription_form.html')

    def test_has_form(self):
        form = self.resp.context['form']
        self.assertIsInstance(form, SubscriptionForm)

    def test_form_has_errors(self):
        form = self.resp.context['form']
        self.assertTrue(form.errors)

class SubscribeSuccessMessage(TestCase):
    def test_message(self):
        data = dict(name='Fabiano Gomes', cpf='12345678901', email='gomes.fdr@gmail.com', phone='51-99543-2916')
        response = self.client.post('/inscricao/', data, follow=True)
        self.assertContains(response, 'Inscricação realizada com sucesso!')