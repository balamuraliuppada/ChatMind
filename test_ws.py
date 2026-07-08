import asyncio
import socketio

sio = socketio.AsyncClient()

@sio.event
async def connect():
    print("Connected!")
    
@sio.event
async def connect_error(data):
    print("Failed to connect:", data)
    
@sio.event
async def disconnect():
    print("Disconnected!")

@sio.on('new_message')
async def on_message(data):
    print("Received new_message:", data)

async def main():
    try:
        await sio.connect('https://chatminds-backend.onrender.com', socketio_path='/socket.io/', transports=['websocket'])
        print("Waiting for messages...")
        await asyncio.sleep(5)
        await sio.disconnect()
    except Exception as e:
        print("Exception:", e)

if __name__ == '__main__':
    asyncio.run(main())
