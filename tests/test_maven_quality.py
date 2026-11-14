
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

    def test_generates_license_header_when_template_exists(self):
        from maven_quality import build_spotless_plugin

        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            template = project_root / "resources" / "license-header.txt"
            template.parent.mkdir(parents=True)
            template.write_text("Copyright 2026 See AUTHORS file.\n")

            config = {
                "version": "2.43.0",
                "java": {
                    "enabled": True,
                    "version": "1.25.2",
                    "style": "AOSP",
                },
                "licenseHeader": {
                    "enabled": True,
                    "template": "resources/license-header.txt",
                    "year": 2026,
                },
            }

            plugin = build_spotless_plugin(
                config,
                project_root=project_root,
            )

            self.assertEqual(
                plugin.findtext(
                    "./configuration/java/licenseHeader/file"
                ),
                "resources/license-header.txt",
            )

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

    def test_skips_license_header_when_template_missing(self):
        from maven_quality import build_spotless_plugin

        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)

            config = {
                "version": "2.43.0",
                "java": {
                    "enabled": True,
                    "version": "1.25.2",
                    "style": "AOSP",
                },
                "licenseHeader": {
                    "enabled": True,
                    "template": "resources/license-header.txt",
                    "year": 2026,
                },
            }

            plugin = build_spotless_plugin(
                config,
                project_root=project_root,
            )

            self.assertIsNone(
                plugin.find("./configuration/java/licenseHeader")
            )

            self.assertIsNotNone(
                plugin.find("./configuration/java/googleJavaFormat")
            )

    def test_skips_license_header_when_template_empty(self):
        from maven_quality import build_spotless_plugin

        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            template = project_root / "resources" / "license-header.txt"
            template.parent.mkdir(parents=True)
            template.write_text("")

            config = {
                "version": "2.43.0",
                "java": {
                    "enabled": True,
                    "version": "1.25.2",
                    "style": "AOSP",
                },
                "licenseHeader": {
                    "enabled": True,
                    "template": "resources/license-header.txt",
                    "year": 2026,
                },
            }

            plugin = build_spotless_plugin(
                config,
                project_root=project_root,
            )

            self.assertIsNone(
                plugin.find("./configuration/java/licenseHeader")
            )

            self.assertIsNotNone(
                plugin.find("./configuration/java/googleJavaFormat")
            )

    def test_skips_license_header_when_template_whitespace_only(self):
        from maven_quality import build_spotless_plugin

        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            template = project_root / "resources" / "license-header.txt"
            template.parent.mkdir(parents=True)
            template.write_text("   \n\t\n")

            config = {
                "version": "2.43.0",
                "java": {
                    "enabled": True,
                    "version": "1.25.2",
                    "style": "AOSP",
                },
                "licenseHeader": {
                    "enabled": True,
                    "template": "resources/license-header.txt",
                    "year": 2026,
                },
            }

            plugin = build_spotless_plugin(
                config,
                project_root=project_root,
            )

            self.assertIsNone(
                plugin.find("./configuration/java/licenseHeader")
            )


    def test_warns_when_license_template_missing(self):
        from maven_quality import build_spotless_plugin

        with tempfile.TemporaryDirectory() as directory:
            config = {
                "version": "2.43.0",
                "java": {
                    "enabled": True,
                    "version": "1.25.2",
                    "style": "AOSP",
                },
                "licenseHeader": {
                    "enabled": True,
                    "template": "resources/license-header.txt",
                    "year": 2026,
                },
            }

            with self.assertWarnsRegex(
                UserWarning,
                "Skipping Spotless license header",
            ):
                plugin = build_spotless_plugin(
                    config,
                    project_root=Path(directory),
                )

            self.assertIsNone(
                plugin.find("./configuration/java/licenseHeader")
            )


    def test_skips_license_header_when_template_unreadable(self):
        from maven_quality import build_spotless_plugin

        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            template = project_root / "resources" / "license-header.txt"
            template.parent.mkdir(parents=True)
            template.write_bytes(b"\xff\xfe\xfa")

            config = {
                "version": "2.43.0",
                "java": {
                    "enabled": True,
                    "version": "1.25.2",
                    "style": "AOSP",
                },
                "licenseHeader": {
                    "enabled": True,
                    "template": "resources/license-header.txt",
                    "year": 2026,
                },
            }

            with self.assertWarnsRegex(
                UserWarning,
                "Skipping Spotless license header",
            ):
                plugin = build_spotless_plugin(
                    config,
                    project_root=project_root,
                )

            self.assertIsNone(
                plugin.find("./configuration/java/licenseHeader")
            )
            self.assertIsNotNone(
                plugin.find("./configuration/java/googleJavaFormat")
            )

    def test_skips_license_header_outside_project(self):
        from maven_quality import build_spotless_plugin

        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            project_root = workspace / "project"
            project_root.mkdir()

            external_template = workspace / "license-header.txt"
            external_template.write_text("Copyright 2026 See AUTHORS file.\n")

            config = {
                "version": "2.43.0",
                "java": {
                    "enabled": True,
                    "version": "1.25.2",
                    "style": "AOSP",
                },
                "licenseHeader": {
                    "enabled": True,
                    "template": "../license-header.txt",
                    "year": 2026,
                },
            }

            with self.assertWarnsRegex(
                UserWarning,
                "Skipping Spotless license header",
            ):
                plugin = build_spotless_plugin(
                    config,
                    project_root=project_root,
                )

            self.assertIsNone(
                plugin.find("./configuration/java/licenseHeader")
            )
            self.assertIsNotNone(
                plugin.find("./configuration/java/googleJavaFormat")
            )

    def test_skips_absolute_license_template_path(self):
        from maven_quality import build_spotless_plugin

        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory) / "project"
            project_root.mkdir()

            template = project_root / "license-header.txt"
            template.write_text("Copyright 2026\n")

            config = {
                "version": "2.43.0",
                "java": {
                    "enabled": True,
                    "version": "1.25.2",
                    "style": "AOSP",
                },
                "licenseHeader": {
                    "enabled": True,
                    "template": str(template.resolve()),
                },
            }

            with self.assertWarnsRegex(
                UserWarning, "Skipping Spotless license header"
            ):
                plugin = build_spotless_plugin(
                    config, project_root=project_root
                )

            self.assertIsNone(
                plugin.find("./configuration/java/licenseHeader")
            )

    def test_skips_license_template_symlink_outside_project(self):
        from maven_quality import build_spotless_plugin

        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            project_root = workspace / "project"
            project_root.mkdir()

            external = workspace / "external-license.txt"
            external.write_text("Copyright 2026\n")

            link = project_root / "license-header.txt"
            link.symlink_to(external)

            config = {
                "version": "2.43.0",
                "java": {
                    "enabled": True,
                    "version": "1.25.2",
                    "style": "AOSP",
                },
                "licenseHeader": {
                    "enabled": True,
                    "template": "license-header.txt",
                },
            }

            with self.assertWarnsRegex(
                UserWarning, "Skipping Spotless license header"
            ):
                plugin = build_spotless_plugin(
                    config, project_root=project_root
                )

            self.assertIsNone(
                plugin.find("./configuration/java/licenseHeader")
            )

    def test_warns_when_project_root_missing(self):
        from maven_quality import build_spotless_plugin

        config = {
            "version": "2.43.0",
            "java": {
                "enabled": True,
                "version": "1.25.2",
                "style": "AOSP",
            },
            "licenseHeader": {
                "enabled": True,
                "template": "resources/license-header.txt",
            },
        }

        with self.assertWarnsRegex(
            UserWarning,
            "project root not provided",
        ):
            plugin = build_spotless_plugin(config)

        self.assertIsNone(
            plugin.find("./configuration/java/licenseHeader")
        )
        self.assertIsNotNone(
            plugin.find("./configuration/java/googleJavaFormat")
        )


if __name__ == "__main__":
        unittest.main()
