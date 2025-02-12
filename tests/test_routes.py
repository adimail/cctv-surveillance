import unittest
import logging
from jinja2 import StrictUndefined
from app import create_app, db
from app.models import User

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class FlaskRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.jinja_env.undefined = StrictUndefined
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            test_user = User.query.filter_by(username='test').first()
            if not test_user:
                test_user = User(username='test', password='test', role='admin')
                db.session.add(test_user)
                db.session.commit()

        response = self.client.post('/auth/login', data={
            'username': 'test',
            'password': 'test'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200, "Login failed. Please check the /login route or credentials.")

    def test_all_routes(self):
        """
        Iterate over all URL rules (excluding those requiring parameters or static files)
        and verify that each route returns an acceptable response status code.
        Using follow_redirects=True allows testing of protected routes that would normally redirect to /login.
        """
        with self.app.test_request_context():
            for rule in self.app.url_map.iter_rules():
                if rule.endpoint == 'static' or rule.arguments:
                    continue

                url = rule.rule
                logging.info(f"\nTesting route: {url}")
                response = self.client.get(url, follow_redirects=True)
                status_code = response.status_code
                logging.info(f"Route {url} returned status code: {status_code}")
                self.assertIn(
                    status_code, [200, 301, 302, 405, 503],
                    f"Route {url} returned unexpected status code {status_code}"
                )
                logging.info(f"Route {url} passed!")

if __name__ == '__main__':
    unittest.main()
