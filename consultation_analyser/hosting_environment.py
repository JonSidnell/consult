import environ

env = environ.Env()


class HostingEnvironment:
    @staticmethod
    def is_local():
        return env.str("ENVIRONMENT", "").upper() == "LOCAL"

    @staticmethod
    def is_test() -> bool:
        return env.str("ENVIRONMENT", "").upper() == "TEST"

    @staticmethod
    def is_deployed() -> bool:
        environment = env.str("ENVIRONMENT", "").upper()
        deployed_envs = ["DEV", "DEVELOPMENT", "PREPROD", "PROD", "PRODUCTION"]
        return environment in deployed_envs

    @staticmethod
    def is_dev() -> bool:
        environment = env.str("ENVIRONMENT", "").upper()
        return environment in ["DEV", "DEVELOP"]
