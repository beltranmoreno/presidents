import asyncio
import websockets
import json

async def send_message(websocket, message):
    # print(f"Sending message: {message}")
    await websocket.send(json.dumps(message))

async def receive_message(websocket):
    message = await websocket.recv()
    # print(f"Received message: {message}")
    return json.loads(message)

async def main():
    async with websockets.connect("ws://localhost:6789", ping_interval=30, ping_timeout=60) as websocket:
        response = await receive_message(websocket)
        if response["count"] == 1:
            num_players = int(input("Enter the number of players: "))
            set_num_players_message = {
                "action": "set_num_players",
                "num_players": num_players
            }
            await send_message(websocket, set_num_players_message)
        
        name = input("Enter your name: ")
        join_message = {
            "action": "join",
            "name": name
        }
        await send_message(websocket, join_message)

        while True:
            try:
                response = await receive_message(websocket)
                if response["type"] == "players":
                    print(f"Number of players connected: {response['count']}")

                elif response["type"] == "game_state":
                    player_hands = {player['name']: player['hand'] for player in response['players']}
                    played_cards = response['played_cards']
                    current_player = response['current_player']

                    if name in player_hands:
                        print(player_hands[name])

                    print(f"Played cards: {played_cards}")
                    print(f"Current player: {current_player}")

                    if current_player == name:
                        indices = input("Enter card indices to play separated by space or type 'pass' to pass: ").strip().lower()
                        if indices == 'pass':
                            pass_message = {
                                "action": "pass",
                                "name": name
                            }
                            await send_message(websocket, pass_message)
                        else:
                            indices = list(map(int, indices.split()))
                            play_message = {
                                "action": "play",
                                "name": name,
                                "indices": indices
                            }
                            await send_message(websocket, play_message)
                elif response["type"] == "error":
                    print(f"Error: {response['message']}")
            except websockets.ConnectionClosed:
                print("Connection closed by server")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
  

asyncio.get_event_loop().run_until_complete(main())
