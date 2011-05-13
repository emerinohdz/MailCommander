# coding: utf-8

from unittest import TestCase, main

from auth import AuthManager, AuthKey, PUBLIC_KEY

class TestAuth(TestCase):
    
    def __init__(self, name):
        TestCase.__init__(self, name)
        
        self.auth = AuthManager("test/etc/users.auth")
        
    def test_manager(self):
        cmd = "test"

        valid_key = AuthKey("testuser", "my.pass")
        invalid_key = AuthKey(None, "invalid")
        garbage_key = AuthKey("garbage", "you")

        self.assertTrue(self.auth.authorized(cmd, valid_key))

        self.assertFalse(self.auth.authorized(cmd, PUBLIC_KEY))
        self.assertFalse(self.auth.authorized(cmd, invalid_key))
        self.assertFalse(self.auth.authorized(cmd, garbage_key))

if __name__ == "__main__":
    main()
