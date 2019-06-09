from django.test import TestCase

# Create your tests here.

class RegistrationViewTests(TestCase):
    def test_registration_post_should_include_username_and_password(self):
        post = {}
        post["username"] = "myt_no_use" # no password post
        response = self.client.post('/registration/', post)
        self.assertEqual(response.status_code, 400)
    
    def test_registration_success_and_used_username_in_seq(self):
        # Create a pair of username and password
        post = {}
        post["username"] = "myt"
        post["password"] = "123456"

        # Registration this pair 1st time should success
        response = self.client.post('/registration/', post)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "Success.")

        # Login this pair 1st time should success
        response = self.client.post('/login/', post)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "Success.")

        # Registration this pair 2nd time should failed
        response = self.client.post('/registration/', post)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "Username has been used.")

        # Login this pair 2nd time should still success
        response = self.client.post('/login/', post)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "Success.")

class LoginViewTests(TestCase):
    def test_login_post_should_include_username_and_password(self):
        post = {}
        post["username"] = "myt" # no password post
        response = self.client.post('/login/', post)
        self.assertEqual(response.status_code, 400)

    def test_login_wrong_username_or_password(self):
        post = {}
        post["username"] = "myt"
        post["password"] = "wrong" # this is a wrong password
        response = self.client.post('/login/', post)
        self.assertEqual(response.status_code, 401)

    def test_login_success(self):
        self.assertEqual(True, True) # See test_registration_success_and_used_username_in_seq for this test
        # post = {}
        # post["username"] = "myt"
        # post["password"] = "123456" # username and password ok
        # response = self.client.post('/login/', post)
        # self.assertEqual(response.status_code, 200)
        # self.assertEqual(response.content.decode("utf-8"), "Success.")

class JSONViewTests(TestCase):
    def test_json_post_should_post_a_json(self):
        dict = "Not a JSON"
        response = self.client.post('/json/', dict, content_type="application/json")
        self.assertEqual(response.status_code, 400)
    
    def test_json_post_should_post_a_json_with_method_key(self):
        import json
        dict = {}
        dict["not_method"] = "TestMethod"
        json_str = json.dumps(dict)
        response = self.client.post('/json/', json_str, content_type="application/json")
        self.assertEqual(response.status_code, 400)
    
    def test_json_post_should_post_a_json_with_true_method_value(self):
        import json
        dict = {}
        dict["method"] = "MethodNotInView"
        json_str = json.dumps(dict)
        response = self.client.post('/json/', json_str, content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_json_post_should_post_a_json_with_method_and_right_parameter(self):
        import json
        dict = {}
        dict["method"] = "test_bool_function"
        json_str = json.dumps(dict)
        response = self.client.post('/json/', json_str, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "Failed.")

        dict["test_bool"] = True
        json_str = json.dumps(dict)
        response = self.client.post('/json/', json_str, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode("utf-8"), "Success.")