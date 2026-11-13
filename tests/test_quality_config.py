import copy
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

sdlc = SourceFileLoader(
    "sdlc", str(Path(__file__).resolve().parents[1] / "sdlc")
).load_module()


class QualityConfigTests(unittest.TestCase):

    def setUp(self):
        self.profile = sdlc.read_profile(
            Path(__file__).resolve().parents[1] / "profile.json"
        )

    def test_valid_configuration(self):
        sdlc.validate_quality(self.profile)

    def test_legacy_profile_without_quality(self):
        profile = copy.deepcopy(self.profile)
        profile.pop("quality", None)
        sdlc.validate_quality(profile)

    def test_quality_must_be_object(self):
        profile = copy.deepcopy(self.profile)
        profile["quality"] = "enabled"

        with self.assertRaises(ValueError):
            sdlc.validate_quality(profile)

    def test_spotless_enabled_must_be_boolean(self):
        profile = copy.deepcopy(self.profile)
        profile["quality"]["maven"]["spotless"]["enabled"] = "true"

        with self.assertRaises(ValueError):
            sdlc.validate_quality(profile)

    def test_java_enabled_must_be_boolean(self):
        profile = copy.deepcopy(self.profile)
        profile["quality"]["maven"]["spotless"]["java"]["enabled"] = 1

        with self.assertRaises(ValueError):
            sdlc.validate_quality(profile)

    def test_xml_configuration_must_be_object(self):
        profile = copy.deepcopy(self.profile)
        profile["quality"]["maven"]["spotless"]["xml"] = []

        with self.assertRaises(ValueError):
            sdlc.validate_quality(profile)

    def test_license_header_enabled_must_be_boolean(self):
        profile = copy.deepcopy(self.profile)
        profile["quality"]["maven"]["spotless"]["licenseHeader"]["enabled"] = "yes"

        with self.assertRaises(ValueError):
            sdlc.validate_quality(profile)

    def test_valid_spotless_version(self):
        profile = copy.deepcopy(self.profile)
        profile["quality"]["maven"]["spotless"]["version"] = "2.43.0"
        sdlc.validate_quality(profile)

    def test_invalid_spotless_version(self):
        profile = copy.deepcopy(self.profile)
        profile["quality"]["maven"]["spotless"]["version"] = "latest"

        with self.assertRaises(ValueError):
            sdlc.validate_quality(profile)


    def test_invalid_java_version(self):
        profile = copy.deepcopy(self.profile)
        profile["quality"]["maven"]["spotless"]["java"]["version"] = "latest"

        with self.assertRaises(ValueError):
            sdlc.validate_quality(profile)

    def test_invalid_java_style(self):
        profile = copy.deepcopy(self.profile)
        profile["quality"]["maven"]["spotless"]["java"]["style"] = "CUSTOM"

        with self.assertRaises(ValueError):
            sdlc.validate_quality(profile)

    def test_disabled_java_does_not_require_formatter_settings(self):
        profile = copy.deepcopy(self.profile)
        profile["quality"]["maven"]["spotless"]["java"] = {
            "enabled": False
        }

        sdlc.validate_quality(profile)

    def test_invalid_xml_includes(self):
        profile = copy.deepcopy(self.profile)
        profile["quality"]["maven"]["spotless"]["xml"]["includes"] = []

        with self.assertRaises(ValueError):
            sdlc.validate_quality(profile)

    def test_disabled_xml_does_not_require_includes(self):
        profile = copy.deepcopy(self.profile)
        profile["quality"]["maven"]["spotless"]["xml"] = {
            "enabled": False
        }

        sdlc.validate_quality(profile)


if __name__ == "__main__":
    unittest.main()
