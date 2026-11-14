"""Inspect and manage Maven quality-gate configuration."""

from pathlib import Path
import xml.etree.ElementTree as ET
import warnings

SPOTLESS_GROUP = "com.diffplug.spotless"
SPOTLESS_ARTIFACT = "spotless-maven-plugin"


def has_spotless_plugin(pom_path: Path) -> bool:
    """Return whether Spotless is declared in the Maven build plugins."""
    root = ET.parse(pom_path).getroot()

    # Maven POMs normally use an XML namespace.
    namespace = ""
    if root.tag.startswith("{"):
        namespace = root.tag.split("}", 1)[0] + "}"

    plugins = root.findall(
        f"./{namespace}build/{namespace}plugins/{namespace}plugin"
    )

    for plugin in plugins:
        group = plugin.findtext(f"{namespace}groupId", default="").strip()
        artifact = plugin.findtext(f"{namespace}artifactId", default="").strip()

        if group == SPOTLESS_GROUP and artifact == SPOTLESS_ARTIFACT:
            return True

    return False

def build_spotless_plugin(spotless_config, project_root=None):
    """Build a Spotless Maven plugin from profile configuration."""
    version = spotless_config["version"]
    plugin = ET.Element("plugin")

    ET.SubElement(plugin, "groupId").text = SPOTLESS_GROUP
    ET.SubElement(plugin, "artifactId").text = SPOTLESS_ARTIFACT
    ET.SubElement(plugin, "version").text = version

    executions = ET.SubElement(plugin, "executions")
    execution = ET.SubElement(executions, "execution")

    ET.SubElement(execution, "id").text = "spotless-check"
    ET.SubElement(execution, "phase").text = "verify"

    goals = ET.SubElement(execution, "goals")
    ET.SubElement(goals, "goal").text = "check"

    xml_config = spotless_config.get("xml", {})

    if xml_config.get("enabled", False):
        configuration = plugin.find("configuration")
        if configuration is None:
            configuration = ET.SubElement(plugin, "configuration")

        formats = ET.SubElement(configuration, "formats")
        format_element = ET.SubElement(formats, "format")

        includes = ET.SubElement(format_element, "includes")
        for pattern in xml_config["includes"]:
            ET.SubElement(includes, "include").text = pattern

        eclipse_wtp = ET.SubElement(format_element, "eclipseWtp")
        ET.SubElement(eclipse_wtp, "type").text = "XML"

    java_config = spotless_config.get("java", {})

    if java_config.get("enabled", False):
        configuration = plugin.find("configuration")
        if configuration is None:
            configuration = ET.SubElement(plugin, "configuration")

        java = ET.SubElement(configuration, "java")
        formatter = ET.SubElement(java, "googleJavaFormat")


        ET.SubElement(formatter, "version").text = java_config["version"]
        ET.SubElement(formatter, "style").text = java_config["style"]

        license_config = spotless_config.get("licenseHeader", {})

        license_config = spotless_config.get("licenseHeader", {})

        if license_config.get("enabled", False) and project_root is None:
            warnings.warn(
                "Skipping Spotless license header: project root not provided",
                UserWarning,
                stacklevel=2,
            )

        if license_config.get("enabled", False) and project_root is not None:
            template_name = license_config.get("template", "")

            try:
                project_path = Path(project_root).resolve()
                relative_path = Path(template_name)

                if relative_path.is_absolute():
                    valid_template = False
                else:
                    template_path = (project_path / relative_path).resolve()

                    valid_template = (
                        template_path.is_relative_to(project_path)
                        and template_path.is_file()
                        and bool(
                            template_path.read_text(encoding="utf-8").strip()
                        )
                    )

            except (OSError, UnicodeError, ValueError, TypeError):
                valid_template = False

            if valid_template:
                license_header = ET.SubElement(java, "licenseHeader")
                ET.SubElement(license_header, "file").text = template_name
            else:
                warnings.warn(
                    f"Skipping Spotless license header: "
                    f"missing, empty, unreadable, or unsafe template "
                    f"'{template_name}'",
                    UserWarning,
                    stacklevel=2,
                )

            if valid_template:
                license_header = ET.SubElement(java, "licenseHeader")
                ET.SubElement(license_header, "file").text = template_name
            else:
                warnings.warn(
                    f"Skipping Spotless license header: "
                    f"missing, empty, unreadable, or unsafe template "
                    f"'{template_name}'",
                    UserWarning,
                    stacklevel=2,
                )

    return plugin
