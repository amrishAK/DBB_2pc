from dependency_injector import containers, providers
from Pipeline.Producer import Producer
from Handler.SocketHandler import SocketServer
from Manager.TwopcManager import TwoPhaseCommitManager
from Handler.LogHandler import LogHandler

class DependencyContainer (containers.DeclarativeContainer):
        loggingService = providers.Singleton(LogHandler)
        quequeService = providers.Singleton(Producer)
        twoPCService = providers.Singleton(TwoPhaseCommitManager,loggingService)
        socketService = providers.Singleton(SocketServer, quequeService, twoPCService,loggingService)