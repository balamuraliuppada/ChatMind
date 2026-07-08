import asyncio
import socketio
import httpx
import sys

# Replace with your actual backend URL
API_URL = "https://chatminds-backend.onrender.com/api/v1"
SOCKET_URL = "https://chatminds-backend.onrender.com"

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print("Connected to WebSocket successfully!")

@sio.event
async def connect_error(data):
    print("Failed to connect:", data)

@sio.event
async def disconnect():
    print("Disconnected from WebSocket")

@sio.on('new_message')
async def on_message(data):
    print("\n>>> RECEIVED NEW MESSAGE EVENT <<<")
    print(data)
    print("==================================\n")

@sio.on('user_joined')
async def on_joined(data):
    print("\n>>> USER JOINED ROOM <<<")
    print(data)
    print("========================\n")

async def main():
    async with httpx.AsyncClient() as client:
        # Create a room
        print("Creating room...")
        res = await client.post(f"{API_URL}/rooms", json={"display_name": "TestBot"})
        if res.status_code != 201:
            print("Failed to create room", res.text)
            return
            
        data = res.json()
        token = data['token']
        room_id = data['room']['id']
        room_code = data['room']['room_code']
        print(f"Created room: {room_code} | ID: {room_id}")

        print("Connecting to Socket.IO...")
        await sio.connect(
            SOCKET_URL, 
            socketio_path='/socket.io/', 
            transports=['websocket'],
            auth={"token": token}
        )
        
        # Send a message
        print("Sending message...")
        response = await sio.call('message', {'message': 'Hello from Python Test Script!', 'id': '00000000-0000-0000-0000-000000000000'})
        print("ACK RECEIVED:", response)
        
        print("Waiting 10 seconds for broadcast...")
        await asyncio.sleep(10)
        await sio.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
