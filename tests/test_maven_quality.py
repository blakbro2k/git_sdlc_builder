
import tempfile
import unittest
from pathlib import Path

from maven_quality import has_spotless_plugin


class MavenQualityTests(unittest.TestCase):

    def test_detects_existing_spotless(self):
        pom = """
        <project xmlns="http://maven.apache.org/POM/4.0.0">
          <build>
            <plugins>
              <plugin>
                <groupId>com.diffplug.spotless</groupId>
                <artifactId>spotless-maven-plugin</artifactId>
              </plugin>
            </plugins>
          </build>
        </project>
        """

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pom.xml"
            path.write_text(pom)
            self.assertTrue(has_spotless_plugin(path))

    def test_missing_spotless(self):
        pom = """
        <project xmlns="http://maven.apache.org/POM/4.0.0">
          <build>
            <plugins>
              <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
              </plugin>
            </plugins>
          </build>
        </project>
        """

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pom.xml"
            path.write_text(pom)
            self.assertFalse(has_spotless_plugin(path))

    def test_plugin_management_does_not_activate_spotless(self):
        pom = """
        <project xmlns="http://maven.apache.org/POM/4.0.0">
          <build>
            <pluginManagement>
              <plugins>
                <plugin>
                  <groupId>com.diffplug.spotless</groupId>
                  <artifactId>spotless-maven-plugin</artifactId>
                </plugin>
              </plugins>
            </pluginManagement>
          </build>
        </project>
        """

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "pom.xml"
            path.write_text(pom)
            self.assertFalse(has_spotless_plugin(path))


    def test_generates_java_aosp_formatter(self):
        from maven_quality import build_spotless_plugin

        config = {
            "version": "2.43.0",
            "java": {
                "enabled": True,
                "version": "1.25.2",
                "style": "AOSP",
            },
        }

        plugin = build_spotless_plugin(config)

        self.assertEqual(
            plugin.findtext("./configuration/java/googleJavaFormat/version"),
            "1.25.2",
        )
        self.assertEqual(
            plugin.findtext("./configuration/java/googleJavaFormat/style"),
            "AOSP",
        )

    def test_generates_spotless_check_execution(self):
        from maven_quality import build_spotless_plugin

        plugin = build_spotless_plugin({"version": "2.43.0"})
        self.assertEqual(
            plugin.findtext("groupId"),
            "com.diffplug.spotless",
        )
        self.assertEqual(
            plugin.findtext("artifactId"),
            "spotless-maven-plugin",
        )
        self.assertEqual(
            plugin.findtext("version"),
            "2.43.0",
        )
        self.assertEqual(
            plugin.findtext("./executions/execution/goals/goal"),
            "check",
        )

    def test_generates_xml_formatter(self):
        from maven_quality import build_spotless_plugin

        config = {
            "version": "2.43.0",
            "xml": {
                "enabled": True,
                "includes": ["pom.xml"],
            },
        }

        plugin = build_spotless_plugin(config)

        self.assertEqual(
            plugin.findtext(
                "./configuration/formats/format/includes/include"
            ),
            "pom.xml",
        )

        self.assertEqual(
            plugin.findtext(
              "./configuration/formats/format/eclipseWtp/type"
            ),
            "XML",
        )

    def test_java_and_xml_share_configuration(self):
        from maven_quality import build_spotless_plugin

        config = {
            "version": "2.43.0",
            "java": {
                "enabled": True,
                "version": "1.25.2",
                "style": "AOSP",
            },
            "xml": {
                "enabled": True,
                "includes": ["pom.xml"],
            },
        }

        plugin = build_spotless_plugin(config)

        self.assertEqual(len(plugin.findall("configuration")), 1)
        self.assertIsNotNone(
            plugin.find("./configuration/java/googleJavaFormat")
        )
        self.assertIsNotNone(
            plugin.find("./configuration/formats/format/eclipseWtp")
        )

if __name__ == "__main__":
        unittest.main()
