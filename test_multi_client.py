import asyncio
import socketio
import httpx
import uuid

API_URL = "http://127.0.0.1:8000/api/v1"
SOCKET_URL = "http://127.0.0.1:8000"

client_a = socketio.AsyncClient()
client_b = socketio.AsyncClient()

received_by_a = False
received_by_b = False

@client_a.on('new_message')
async def on_message_a(data):
    global received_by_a
    print("\n[CLIENT A] Received new_message:", data)
    received_by_a = True

@client_b.on('new_message')
async def on_message_b(data):
    global received_by_b
    print("\n[CLIENT B] Received new_message:", data)
    received_by_b = True

@client_a.on('user_joined')
async def on_joined_a(data):
    print("\n[CLIENT A] Received user_joined:", data)

@client_b.on('user_joined')
async def on_joined_b(data):
    print("\n[CLIENT B] Received user_joined:", data)

async def main():
    async with httpx.AsyncClient() as http:
        # Create Room (Client A)
        res_a = await http.post(f"{API_URL}/rooms", json={"display_name": "Alice"})
        data_a = res_a.json()
        token_a = data_a['token']
        room_code = data_a['room']['room_code']
        room_id = data_a['room']['id']
        print(f"Alice created room {room_code} (ID: {room_id})")

        # Join Room (Client B)
        res_b = await http.post(f"{API_URL}/rooms/join", json={"room_code": room_code, "display_name": "Bob"})
        data_b = res_b.json()
        token_b = data_b['token']
        print(f"Bob joined room {room_code}")

        # Connect WebSocket for A
        await client_a.connect(SOCKET_URL, socketio_path='/socket.io/', transports=['websocket'], auth={"token": token_a})
        print("Client A connected")

        # Connect WebSocket for B
        await client_b.connect(SOCKET_URL, socketio_path='/socket.io/', transports=['websocket'], auth={"token": token_b})
        print("Client B connected")

        # Wait a second for connections to settle
        await asyncio.sleep(1)

        # Alice sends a message
        msg_id = str(uuid.uuid4())
        print(f"Client A sending message with ID: {msg_id}")
        response = await client_a.call('message', {'id': msg_id, 'message': 'Hello from Alice!'})
        print("ACK from Server:", response)

        # Wait for broadcast
        print("Waiting for broadcasts...")
        await asyncio.sleep(5)

        if received_by_a:
            print("SUCCESS: Client A received the broadcast (Sender received it)")
        else:
            print("FAILURE: Client A did NOT receive the broadcast")

        if received_by_b:
            print("SUCCESS: Client B received the broadcast (Receiver received it)")
        else:
            print("FAILURE: Client B did NOT receive the broadcast")

        await client_a.disconnect()
        await client_b.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
