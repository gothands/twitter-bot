import web3
from web3 import Web3
import os
import time
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv('RPC_URL')

game_contract_address = "0x0F7Fb8b0Bb8eA6EeC1BcFf7b1E3e3E3e3E3e3E3e"
session_contract_address = "0xF326D135BaC6464846CA824e190da033e079b814"
session_contract_abi = '[ { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "user", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "sessionId", "type": "uint256" } ], "name": "OnSession", "type": "event" }, { "inputs": [ { "internalType": "uint256", "name": "sessionId", "type": "uint256" } ], "name": "set", "outputs": [], "stateMutability": "nonpayable", "type": "function" } ]'
game_contract_abi = '[{"inputs":[{"internalType":"address","name":"_bankContractAddress","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"gameId","type":"uint256"},{"indexed":false,"internalType":"enumHands.Outcomes","name":"outcome","type":"uint8"}],"name":"GameOutcome","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"gameId","type":"uint256"},{"indexed":true,"internalType":"address","name":"playerAddress","type":"address"},{"indexed":false,"internalType":"uint256","name":"round","type":"uint256"}],"name":"MoveCommitted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"gameId","type":"uint256"},{"indexed":true,"internalType":"address","name":"playerAddress","type":"address"},{"indexed":false,"internalType":"enumHands.Moves","name":"move","type":"uint8"},{"indexed":false,"internalType":"uint256","name":"round","type":"uint256"}],"name":"MoveRevealed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"gameId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"round","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"pointsA","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"pointsB","type":"uint256"}],"name":"NewRound","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"gameId","type":"uint256"},{"indexed":true,"internalType":"address","name":"playerAddress","type":"address"}],"name":"PlayerCancelled","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"gameId","type":"uint256"},{"indexed":true,"internalType":"address","name":"playerAddress","type":"address"}],"name":"PlayerLeft","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"gameId","type":"uint256"},{"indexed":true,"internalType":"address","name":"playerAddress","type":"address"},{"indexed":false,"internalType":"bytes32","name":"name","type":"bytes32"}],"name":"PlayerRegistered","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"gameId","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"bet","type":"uint256"},{"indexed":true,"internalType":"address","name":"playerAddress","type":"address"},{"indexed":false,"internalType":"bool","name":"first","type":"bool"}],"name":"PlayerWaiting","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"gameId","type":"uint256"},{"indexed":true,"internalType":"address","name":"playerA","type":"address"},{"indexed":true,"internalType":"address","name":"playerB","type":"address"}],"name":"PlayersMatched","type":"event"},{"inputs":[],"name":"BET_MIN","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"FEE_PERCENTAGE","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MAX_POINTS_PER_ROUND","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"MOVE_TIMEOUT","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"TIMEOUT_MARGIN","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"gameId","type":"uint256"}],"name":"cancel","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"gameId","type":"uint256"},{"internalType":"bytes32","name":"encrMove","type":"bytes32"}],"name":"commit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"passwordHash","type":"bytes32"}],"name":"createPasswordMatch","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"burner","type":"address"},{"internalType":"uint256","name":"betAmount","type":"uint256"},{"internalType":"bytes32","name":"passwordHash","type":"bytes32"}],"name":"createPasswordMatchWithBurner","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_value","type":"uint256"}],"name":"fundBurner","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"_owner","type":"address"}],"name":"getBurner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_burner","type":"address"}],"name":"getOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"password","type":"string"}],"name":"joinPasswordMatch","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"burner","type":"address"},{"internalType":"uint256","name":"betAmount","type":"uint256"},{"internalType":"string","name":"password","type":"string"}],"name":"joinPasswordMatchWithBurner","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"gameId","type":"uint256"}],"name":"leave","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"playerGame","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"register","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"burner","type":"address"},{"internalType":"uint256","name":"betAmount","type":"uint256"}],"name":"registerWithBurner","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"gameId","type":"uint256"},{"internalType":"string","name":"clearMove","type":"string"}],"name":"reveal","outputs":[{"internalType":"enumHands.Moves","name":"","type":"uint8"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_burner","type":"address"}],"name":"setBurner","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"waitingPlayers","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'


class SessionEventListener:
    def __init__(self):
        # Connect to Ethereum node (e.g., Infura)
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        
        # ABI of the smart contract (replace with your actual ABI)
        self.contract_abi = session_contract_abi 
        
        # Address of the deployed smart contract (replace with your actual address)
        self.contract_address = session_contract_address
        
        # Create contract object
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)

        # Create event filter to listen for specific event
        self.event_filter = self.contract.events.OnSession.createFilter(fromBlock='latest')

    def fetch_recent_events(self):
        return self.event_filter.get_new_entries()

    def handle_event(self, event, callback):
        # Extract data from the event
        session_id = event.args.sessionId
        user_address = event.args.user
        
        # Pass the event data to the callback function
        callback(session_id, user_address)

class GameEventListener:
    def __init__(self):
        # Connect to Ethereum node (e.g., Infura)
        self.w3 = Web3(Web3.HTTPProvider(RPC_URL))
        
        # ABI of the smart contract (replace with your actual ABI)
        self.contract_abi = game_contract_abi 
        
        # Address of the deployed smart contract (replace with your actual address)
        self.contract_address = game_contract_address
        
        # Create contract object
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.contract_abi)

        # Create event filter to listen for two specific events (OnGameStart and OnGameEnd)
        self.game_start_filter = self.contract.events.PlayersMatched.createFilter(fromBlock='latest')
        self.game_end_filter = self.contract.events.GameOutcome.createFilter(fromBlock='latest')


    def fetch_recent_game_start_events(self):
        return self.game_start_filter.get_new_entries()
    
    def fetch_recent_game_end_events(self):
        return self.game_end_filter.get_new_entries()

    def handle_game_start_event(self, event, callback):
        # Extract data from the event
        game_id = event.args.gameId
        player_a = event.args.playerA
        player_b = event.args.playerB

        # Pass the event data to the callback function
        callback(game_id, player_a, player_b)

    def handle_game_end_event(self, event, callback):
        # Extract data from the event
        game_id = event.args.gameId
        player_a = event.args.playerA
        player_b = event.args.playerB
        outcome = event.args.outcome
        
        #calculate winner based on outcome enum Outcomes {None,PlayerA,PlayerB,Draw,PlayerALeft,PlayerBLeft,PlayerATimeout,PlayerBTimeout,BothTimeout}
        winner = None
        if outcome == 1:
            winner = player_a
        elif outcome == 2:
            winner = player_b
        elif outcome == 3:
            winner = "Draw"
        elif outcome == 4:
            winner = player_b
        elif outcome == 5:
            winner = player_a
        elif outcome == 6:
            winner = player_b
        elif outcome == 7:
            winner = player_a
        elif outcome == 8:
            winner = "Draw"

        # Pass the event data to the callback function
        callback(game_id, player_a, player_b, winner)            
