import socket
import json
import threading
import time
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

class MessageType(Enum):
    # Połączenie
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PLAYER_LIST = "player_list"

    # Stan gry
    GAME_STATE = "game_state"
    PHASE_CHANGE = "phase_change"
    PLAYER_ACTION = "player_action"

    # Akcje gracza
    PLAY_CARD = "play_card"
    HEX_PLACEMENT = "hex_placement"
    RESEARCH_START = "research_start"

    # Synchronizacja
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"
    HEARTBEAT = "heartbeat"

@dataclass
class NetworkMessage:
    type: MessageType
    data: Dict[str, Any]
    player_id: Optional[str] = None
    timestamp: float = 0.0

    def to_json(self) -> str:
        return json.dumps({
            'type': self.type.value,
            'data': self.data,
            'player_id': self.player_id,
            'timestamp': self.timestamp or time.time()
        })

    @classmethod
    def from_json(cls, json_str: str) -> 'NetworkMessage':
        data = json.loads(json_str)
        return cls(
            type=MessageType(data['type']),
            data=data['data'],
            player_id=data.get('player_id'),
            timestamp=data.get('timestamp', time.time())
        )

class GameServer:
    """Serwer gry dla sesji wieloosobowej"""

    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.clients = {}  # client_socket -> player_info
        self.running = False
        self.game_instance = None

    def start(self, game_instance):
        """Uruchamia serwer gry"""
        self.game_instance = game_instance
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True

            print(f"🎮 Serwer gry uruchomiony na {self.host}:{self.port}")

            # Uruchom wątek nasłuchujący połączeń
            accept_thread = threading.Thread(target=self._accept_connections)
            accept_thread.daemon = True
            accept_thread.start()

            return True

        except Exception as e:
            print(f"❌ Błąd uruchamiania serwera: {e}")
            return False

    def _accept_connections(self):
        """Nasłuchuje nowych połączeń"""
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                print(f"🔗 Nowe połączenie: {address}")

                # Uruchom wątek obsługi klienta
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()

            except Exception as e:
                if self.running:
                    print(f"❌ Błąd przyjmowania połączenia: {e}")

    def _handle_client(self, client_socket, address):
        """Obsługuje komunikację z pojedynczym klientem"""
        try:
            while self.running:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break

                try:
                    message = NetworkMessage.from_json(data)
                    self._process_message(client_socket, message)
                except json.JSONDecodeError:
                    print(f"⚠️ Nieprawidłowa wiadomość od {address}")

        except Exception as e:
            print(f"❌ Błąd obsługi klienta {address}: {e}")
        finally:
            self._disconnect_client(client_socket)

    def _process_message(self, client_socket, message: NetworkMessage):
        """Przetwarza wiadomość od klienta"""
        if message.type == MessageType.CONNECT:
            self._handle_connect(client_socket, message)
        elif message.type == MessageType.PLAYER_ACTION:
            self._handle_player_action(client_socket, message)
        elif message.type == MessageType.SYNC_REQUEST:
            self._handle_sync_request(client_socket)
        elif message.type == MessageType.HEARTBEAT:
            self._handle_heartbeat(client_socket)

    def _handle_connect(self, client_socket, message):
        """Obsługuje połączenie nowego gracza"""
        player_name = message.data.get('player_name', f'Gracz_{len(self.clients)+1}')
        player_id = f"player_{len(self.clients)+1}"

        self.clients[client_socket] = {
            'player_id': player_id,
            'player_name': player_name,
            'connected_at': time.time()
        }

        print(f"✅ Gracz {player_name} dołączył do gry")

        # Pošlij potwierdzenie
        response = NetworkMessage(
            type=MessageType.CONNECT,
            data={'status': 'connected', 'player_id': player_id}
        )
        self._send_to_client(client_socket, response)

        # Wyślij aktualny stan gry
        self._send_game_state(client_socket)

        # Powiadom innych graczy
        self._broadcast_player_list()

    def _handle_player_action(self, client_socket, message):
        """Obsługuje akcję gracza"""
        if client_socket not in self.clients:
            return

        # Przekaż akcję do głównej instancji gry
        if self.game_instance:
            # TODO: Implementować przekazywanie akcji do gry
            pass

        # Rozgłoś akcję do innych graczy
        self._broadcast_message(message, exclude=client_socket)

    def _handle_sync_request(self, client_socket):
        """Obsługuje żądanie synchronizacji stanu gry"""
        self._send_game_state(client_socket)

    def _handle_heartbeat(self, client_socket):
        """Obsługuje ping od klienta"""
        response = NetworkMessage(
            type=MessageType.HEARTBEAT,
            data={'timestamp': time.time()}
        )
        self._send_to_client(client_socket, response)

    def _send_game_state(self, client_socket):
        """Wysyła aktualny stan gry do klienta"""
        if not self.game_instance:
            return

        # TODO: Serializować stan gry
        game_state = {
            'current_phase': self.game_instance.current_phase.value,
            'current_player': self.game_instance.current_player_idx,
            'round': self.game_instance.current_round,
            'players': [
                {
                    'name': p.name,
                    'color': p.color,
                    'credits': p.credits,
                    'prestige_points': p.prestige_points,
                    'reputation': p.reputation
                } for p in self.game_instance.players
            ]
        }

        message = NetworkMessage(
            type=MessageType.GAME_STATE,
            data=game_state
        )
        self._send_to_client(client_socket, message)

    def _broadcast_player_list(self):
        """Rozgłasza listę graczy do wszystkich klientów"""
        players = [
            {
                'player_id': info['player_id'],
                'player_name': info['player_name']
            } for info in self.clients.values()
        ]

        message = NetworkMessage(
            type=MessageType.PLAYER_LIST,
            data={'players': players}
        )
        self._broadcast_message(message)

    def _broadcast_message(self, message: NetworkMessage, exclude=None):
        """Rozgłasza wiadomość do wszystkich klientów"""
        for client_socket in list(self.clients.keys()):
            if client_socket != exclude:
                self._send_to_client(client_socket, message)

    def _send_to_client(self, client_socket, message: NetworkMessage):
        """Wysyła wiadomość do konkretnego klienta"""
        try:
            client_socket.send(message.to_json().encode('utf-8'))
        except Exception as e:
            print(f"❌ Błąd wysyłania do klienta: {e}")
            self._disconnect_client(client_socket)

    def _disconnect_client(self, client_socket):
        """Rozłącza klienta"""
        if client_socket in self.clients:
            player_info = self.clients[client_socket]
            print(f"👋 Gracz {player_info['player_name']} rozłączył się")
            del self.clients[client_socket]

            # Powiadom innych graczy
            self._broadcast_player_list()

        try:
            client_socket.close()
        except:
            pass

    def stop(self):
        """Zatrzymuje serwer"""
        self.running = False

        # Rozłącz wszystkich klientów
        for client_socket in list(self.clients.keys()):
            self._disconnect_client(client_socket)

        # Zamknij serwer
        if self.socket:
            self.socket.close()

        print("🛑 Serwer gry zatrzymany")

class GameClient:
    """Klient do łączenia się z grą sieciową"""

    def __init__(self):
        self.socket = None
        self.connected = False
        self.player_id = None
        self.game_instance = None
        self.receive_thread = None

    def connect(self, host, port, player_name, game_instance):
        """Łączy się z serwerem gry"""
        self.game_instance = game_instance

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True

            print(f"🔗 Połączono z serwerem {host}:{port}")

            # Wyślij żądanie połączenia
            connect_message = NetworkMessage(
                type=MessageType.CONNECT,
                data={'player_name': player_name}
            )
            self._send_message(connect_message)

            # Uruchom wątek nasłuchujący
            self.receive_thread = threading.Thread(target=self._receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()

            return True

        except Exception as e:
            print(f"❌ Błąd połączenia z serwerem: {e}")
            return False

    def _receive_messages(self):
        """Nasłuchuje wiadomości od serwera"""
        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break

                message = NetworkMessage.from_json(data)
                self._process_server_message(message)

            except Exception as e:
                if self.connected:
                    print(f"❌ Błąd odbioru wiadomości: {e}")
                break

        self.connected = False

    def _process_server_message(self, message: NetworkMessage):
        """Przetwarza wiadomość od serwera"""
        if message.type == MessageType.CONNECT:
            self.player_id = message.data.get('player_id')
            print(f"✅ Połączono jako {self.player_id}")

        elif message.type == MessageType.GAME_STATE:
            self._handle_game_state_update(message.data)

        elif message.type == MessageType.PLAYER_ACTION:
            self._handle_player_action(message)

        elif message.type == MessageType.PLAYER_LIST:
            print(f"👥 Gracze online: {len(message.data['players'])}")

    def _handle_game_state_update(self, game_state):
        """Obsługuje aktualizację stanu gry"""
        if self.game_instance:
            # TODO: Zaktualizować UI na podstawie stanu gry
            pass

    def _handle_player_action(self, message):
        """Obsługuje akcję innego gracza"""
        if self.game_instance:
            # TODO: Przekazać akcję do głównej instancji gry
            pass

    def send_action(self, action_type, action_data):
        """Wysyła akcję gracza do serwera"""
        message = NetworkMessage(
            type=MessageType.PLAYER_ACTION,
            data={
                'action_type': action_type,
                'action_data': action_data
            },
            player_id=self.player_id
        )
        self._send_message(message)

    def _send_message(self, message: NetworkMessage):
        """Wysyła wiadomość do serwera"""
        try:
            self.socket.send(message.to_json().encode('utf-8'))
        except Exception as e:
            print(f"❌ Błąd wysyłania wiadomości: {e}")
            self.disconnect()

    def disconnect(self):
        """Rozłącza się z serwerem"""
        self.connected = False

        if self.socket:
            try:
                disconnect_message = NetworkMessage(
                    type=MessageType.DISCONNECT,
                    data={},
                    player_id=self.player_id
                )
                self._send_message(disconnect_message)
                self.socket.close()
            except:
                pass

        print("👋 Rozłączono z serwerem")