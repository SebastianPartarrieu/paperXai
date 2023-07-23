# utils to load data and configs
import yaml
import paperxai.constants as constants


def load_config(path_config: str = constants.ROOT_DIR + "/config.yml") -> dict:
    """Load config file."""
    with open(path_config) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config
