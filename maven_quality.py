"""Inspect and manage Maven quality-gate configuration."""

from pathlib import Path
import xml.etree.ElementTree as ET


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

def build_spotless_plugin(spotless_config):
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

    return plugin
