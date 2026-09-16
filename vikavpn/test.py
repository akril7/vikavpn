import manager

targets = list(manager.Target(item) for item in list(manager.Target))


def get_status():
    return manager.get_services_status(targets=targets)


def test():
    manager.uninstall_targets(targets=manager.installed_targets())
    status = get_status()
    assert ": установлен" not in status

    manager.install_targets(targets=targets, force=False)
    status = get_status()
    assert "не установлен" not in status

    manager.install_targets(targets=targets, force=True)
    status = get_status()
    assert "не установлен" not in status

    manager.apply_configuration(targets=targets)

    manager.stop_services(targets=targets)
    status = get_status()
    assert "не установлен" not in status
    assert "запущен" not in status

    manager.start_services(targets=targets)
    status = get_status()
    assert "не установлен" not in status
    assert "остановлен" not in status

    manager.restart_services(targets=targets)
    status = get_status()
    assert "не установлен" not in status
    assert "остановлен" not in status

    manager.uninstall_targets(targets=manager.installed_targets())
    status = get_status()
    assert "установлен" not in status


if __name__ == "__main__":
    test()
