import pjsua2 as pj
import time


# Subclass to extend the Account and get notifications etc.
class Account(pj.Account):
    def onRegState(self, prm):
        print("***OnRegState: " + prm.reason)


# pjsua2 test function
def pjsua2_demo():
    # Create and initialize the library
    ep_cfg = pj.EpConfig()
    ep = pj.Endpoint()
    ep.libCreate()
    ep.libInit(ep_cfg)

    # Create SIP transport. Error handling sample is shown
    sipTpConfig = pj.TransportConfig()
    # comment out
    # sipTpConfig.port = 5060;
    ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, sipTpConfig)
    # Start the library
    ep.libStart()

    acfg = pj.AccountConfig()
    acfg.idUri = ACCOUNT_URI
    acfg.regConfig.registrarUri = SIP_SERVER
    cred = pj.AuthCredInfo("digest", "*", ACCOUNT_NAME, 0, ACCOUNT_DATA)
    acfg.sipConfig.authCreds.append(cred)
    # Create the account
    acc = Account()
    acc.create(acfg)
    # Here we don't have anything else to do..
    time.sleep(10)

    # Destroy the library
    ep.libDestroy()


#
# main()
#
if __name__ == "__main__":
    SIP_SERVER = input("Sip Server ?: [sip:sipserver]")
    ACCOUNT_URI = input("Account Uri ?: [sip:name@sipserver]")
    ACCOUNT_NAME = input("Account Name ?: [name]")
    ACCOUNT_DATA = input("Account Password ?: [password]")

    pjsua2_demo()
