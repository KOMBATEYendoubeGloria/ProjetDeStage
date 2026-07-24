"""Tests for StandardResponse helper."""

from django.test import SimpleTestCase

from devops.api.responses.standard import StandardResponse


class StandardResponseSuccessTests(SimpleTestCase):
    def test_success_default(self):
        response = StandardResponse.success()
        self.assertEqual(response.status_code, 200)
        body = response.data
        self.assertTrue(body['success'])
        self.assertEqual(body['message'], 'Success')
        self.assertEqual(body['data'], {})
        self.assertEqual(body['errors'], [])
        self.assertIn('timestamp', body)
        self.assertIn('request_id', body)

    def test_success_with_data(self):
        response = StandardResponse.success(data={'key': 'val'}, message='Done')
        body = response.data
        self.assertTrue(body['success'])
        self.assertEqual(body['message'], 'Done')
        self.assertEqual(body['data'], {'key': 'val'})

    def test_success_custom_status(self):
        response = StandardResponse.success(status_code=201)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.data['success'])

    def test_success_with_request_id(self):
        response = StandardResponse.success(request_id='req-123')
        self.assertEqual(response.data['request_id'], 'req-123')


class StandardResponseErrorTests(SimpleTestCase):
    def test_error_default(self):
        response = StandardResponse.error(errors=['bad input'])
        self.assertEqual(response.status_code, 400)
        body = response.data
        self.assertFalse(body['success'])
        self.assertEqual(body['message'], 'An error occurred')
        self.assertEqual(body['errors'], ['bad input'])
        self.assertEqual(body['data'], {})

    def test_error_custom_message(self):
        response = StandardResponse.error(
            errors=['not found'],
            message='Record missing',
            status_code=404,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['message'], 'Record missing')

    def test_error_with_request_id(self):
        response = StandardResponse.error(errors=['x'], request_id='err-1')
        self.assertEqual(response.data['request_id'], 'err-1')

    def test_error_multiple_messages(self):
        response = StandardResponse.error(errors=['e1', 'e2', 'e3'])
        self.assertEqual(len(response.data['errors']), 3)

    def test_error_timestamp_is_iso(self):
        response = StandardResponse.error(errors=['x'])
        ts = response.data['timestamp']
        self.assertIn('T', ts)
