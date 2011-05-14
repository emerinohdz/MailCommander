#coding: utf-8

from unittest import TestCase, main

from notifications import EmailNotifier, Notification

class TestNotifications(TestCase):
    
    def __init__(self, name):
        TestCase.__init__(self, name)

        self.notifier = EmailNotifier("10.2.1.2", 25)
        
    def test_notification(self):
        notification = Notification()
        notification.title = "Test"
        notification.sender = "test@example.com"
        notification.recipients.append("emerino@etesa.com.mx")
        notification.body["text"] = "JOJOJOJO"
           
        self.notifier.send(notification)

if __name__ == "__main__":
    main()
