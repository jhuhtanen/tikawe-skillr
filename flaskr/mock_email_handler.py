from sys import stderr

from flaskr.email_interface import EmailInterface


# pylint: disable=R0903
class MockEmailInterface(EmailInterface):
    def send_email(self, to_email: str, reset_link: str):
        print(f"email would be sent to: {to_email} with reset link {reset_link}", file=stderr)
