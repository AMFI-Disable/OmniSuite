import os
from omnidebate.core.config import load_config, save_config


def test_config():
    # Set a temp config file
    import omnidebate.core.config as config

    original_file = config.CONFIG_FILE
    config.CONFIG_FILE = "test_config.yaml"

    cfg = load_config()
    cfg["test_key"] = "test_value"
    save_config(cfg)

    cfg2 = load_config()
    assert cfg2["test_key"] == "test_value"

    # Cleanup
    os.remove("test_config.yaml")
    config.CONFIG_FILE = original_file
    print("Config test passed!")


if __name__ == "__main__":
    test_config()
