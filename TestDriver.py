from tests.t_HelloAPI import t_HelloAPI
from tests.t_config import EnabledTests


if EnabledTests.get('HELLO', False):
    test_Hello = t_HelloAPI()
    print("***\nRunning test_Hello:")
    test_Hello.RunAll()
    print("Done\n***")