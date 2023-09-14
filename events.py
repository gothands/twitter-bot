import web3
from web3 import Web3
import os
import time
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv('RPC_URL')

session_contract_address = "0xF326D135BaC6464846CA824e190da033e079b814"
session_contract_abi = '[ { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "user", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "sessionId", "type": "uint256" } ], "name": "OnSession", "type": "event" }, { "inputs": [ { "internalType": "uint256", "name": "sessionId", "type": "uint256" } ], "name": "set", "outputs": [], "stateMutability": "nonpayable", "type": "function" } ]'

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