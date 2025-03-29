from sys import stderr

from flaskr.email import EmailInterface


class MockEmailInterface(EmailInterface):
    def send_email(self, to_email: str, reset_link: str):
        print(f"email would be sent to: {to_email} with reset link {reset_link}", file=stderr)
