from tests.HelloAPI.t_HelloAPI import t_HelloAPI
from tests.config.t_config import EnabledTests


if EnabledTests.get('HELLO', False):
    test_Hello = t_HelloAPI()
    print("***\nRunning test_Hello:")
    test_Hello.RunAll()
    print("Done\n***")