from tests.t_CodingAPI import t_CodingAPI
from tests.t_HelloAPI import t_HelloAPI
from tests.t_GameStateAPI import t_GameStateAPI
from tests.t_DashboardAPI import t_DashboardAPI
from tests.t_PlayerIDAPI import t_PlayerIDAPI
from tests.t_config import EnabledTests


if EnabledTests.get('HELLO'):
    test_Hello = t_HelloAPI()
    print("***\nRunning test_Hello:")
    test_Hello.RunAll()
    print("Done\n***")
if EnabledTests.get('CODE'):
    test_Coding = t_CodingAPI()
    print("***\nRunning test_Coding:")
    test_Coding.RunAll()
    print("Done\n***")
if EnabledTests.get('DASHBOARD'):
    test_Dash = t_DashboardAPI()
    print("***\nRunning test_Dashboard:\n")
    test_Dash.RunAll()
    print("Done\n***")
if EnabledTests.get('PLAYER'):
    test_PlayerID = t_PlayerIDAPI()
    print("***\nRunning test_PlayerID:\n")
    test_PlayerID.RunAll()
    print("Done\n***")
if EnabledTests.get('GAME_STATE'):
    test_GameState = t_GameStateAPI()
    print("***\nRunning test_GameState:\n")
    test_GameState.RunAll()
    print("Done\n***")