"""test_libpulse"""

import unittest
from intercom.libs.pulseaudio.libpulse import VolumePulseaudio as VPA


class TestLibpulse(unittest.TestCase):

    def test_type_speaker(self):
        speaker = VPA(type="SINK", name="VolumeSpeaker")
        self.assertEqual(speaker.facility_type, "SINK")

    def test_type_mic(self):
        mic = VPA(type="SOURCE", name="VolumeMic")
        self.assertEqual(mic.facility_type, "SOURCE")

    def test_type_any(self):
        with self.assertRaises(KeyError):
            any = VPA(type="ANY", name="VolumeAny")

    def test_value(self):
        speaker = VPA(type="SINK", name="VolmeSpeaker")
        speaker.value = 4000
        self.assertEqual(speaker.value, 4000)


if __name__ == "__main__":
    unittest.main()
