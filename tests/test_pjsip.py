"""test_pjsip"""

import unittest

from configparser import ConfigParser
from pathlib import Path


from intercom.libs.pjsip.useragent import UserAgent as UA
from intercom.libs.pjsip.account import Account as ACC
from intercom.libs.pjsip.call import Call as CAL


class TestPjsip(unittest.TestCase):
    def setUp(self):
        ini_file = str(Path().absolute()) + "/config/intercom.ini"
        self.config = ConfigParser()
        self.config.read(ini_file)
        return super().setUp()

    def test_useragent(self):
        self.ua = UA()
        self.ua.registryAccount(
            self.config["DEFAULT"]["AccountUri"],
            self.config["DEFAULT"]["SipServer"],
            self.config["DEFAULT"]["AccountName"],
            self.config["DEFAULT"]["AccountData"],
        )
        self.ua.registryBuddy(self.config["DEFAULT"]["BuddyUri"])


if __name__ == "__main__":
    unittest.main()
