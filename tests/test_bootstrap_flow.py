from pathlib import Path

from orangehrm.bootstrap import installer_flow


class FakeInstallerPage:
    def __init__(self, driver, base_url=None):
        self.driver = driver
        self.base_url = base_url
        self.calls = []

    def open(self):
        self.calls.append("open")
        return self

    def click_next(self):
        self.calls.append("click_next")
        return self

    def accept_welcome(self):
        self.calls.append("accept_welcome")
        return self

    def accept_license(self):
        self.calls.append("accept_license")
        return self

    def configure_database(self, **kwargs):
        self.calls.append(("configure_database", kwargs))
        return self

    def complete_instance_creation(self):
        self.calls.append("complete_instance_creation")
        return self

    def complete_admin_creation(self):
        self.calls.append("complete_admin_creation")
        return self

    def wait_for_installation_and_click_next(self):
        self.calls.append("wait_for_installation_and_click_next")
        return self


def test_installer_flow_runs_expected_steps(monkeypatch):
    monkeypatch.setattr(installer_flow, "InstallerPage", FakeInstallerPage)

    flow = installer_flow.InstallerFlow(
        driver=object(), base_url="http://localhost", screenshots_dir=Path("/tmp")
    )

    flow.run()

    assert flow.installer_page.calls == [
        "open",
        "accept_welcome",
        "click_next",
        "accept_license",
        "click_next",
        (
            "configure_database",
            {
                "host": "mysql",
                "port": "3306",
                "database_name": "orangehrm",
                "username": "root",
                "password": "root",
            },
        ),
        "click_next",
        "click_next",
        "complete_instance_creation",
        "click_next",
        "complete_admin_creation",
        "click_next",
        "wait_for_installation_and_click_next",
    ]
