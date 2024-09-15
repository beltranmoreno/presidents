import asyncio
import websockets
import json

async def send_message(websocket, message):
    print(f"[CLIENT LOG] Sending message: {message}")
    await websocket.send(json.dumps(message))

async def receive_message(websocket):
    message = await websocket.recv()
    print(f"[CLIENT LOG] Received message: {message}")
    return json.loads(message)

async def handle_game_state(response, websocket, name):
    print(f"[CLIENT LOG] Handling game state for {name}")
    player_hands = {player['name']: player['hand'] for player in response['players']}
    played_cards = response['played_cards']
    current_player = response['current_player']

    if name in player_hands:
        print(f"\n{name}'s hand:")
        hand = player_hands[name]
        for index, card in enumerate(hand):
            print(f"{index}. {card['rank']} of {card['suit']}")

    # Display played cards in a readable format
    print("\nPlayed cards:")
    if played_cards:
        for set_index, card_set in enumerate(played_cards):
            played_cards_formatted = ", ".join(f"{card['rank']} of {card['suit']}" for card in card_set)
            print(f"Set {set_index + 1}: {played_cards_formatted}")
    else:
        print("No cards have been played yet.")

    print(f"\nCurrent player: {current_player}")

    if current_player == name:
        await player_turn(websocket, name)

async def player_turn(websocket, name):
    print(f"[CLIENT LOG] {name} is taking their turn.")
    while True:
        indices = input("Enter card indices to play separated by space or type 'pass' to pass: ").strip().lower()
        if indices == 'pass':
            pass_message = {
                "action": "pass",
                "name": name
            }
            await send_message(websocket, pass_message)
            break
        else:
            try:
                indices = list(map(int, indices.split()))
                play_message = {
                    "action": "play",
                    "name": name,
                    "indices": indices
                }
                await send_message(websocket, play_message)
                
                # Wait for server response to check if the move was valid
                response = await receive_message(websocket)
                # print(f"[CLIENT LOG] Response after play: {response}")

                if response["type"] == "error":
                    print(f"[CLIENT LOG] Error: {response['message']} Please try again.")
                    continue

                else:
                    print(f"[CLIENT LOG] Valid move made by {name}.")
                    current_player = response['current_player']
                    print(f"\nCurrent player: {current_player}")
                    break  # Exit the loop if the move is valid
            except ValueError:
                print("Invalid input. Please enter valid card indices or 'pass'.")


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
                    print(f"[CLIENT LOG] Number of players connected: {response['count']}")
                
                elif response["type"] == "game_state":
                    print(f"[CLIENT LOG] Handling game state for {name}")
                    await handle_game_state(response, websocket, name)

                elif response["type"] == "error":
                    print(f"[CLIENT LOG] Error: {response['message']}")
                    # Await next game state update to continue
                    response = await receive_message(websocket)
                    print(f"[CLIENT LOG] Response after error: {response}")
                    if response["type"] == "game_state":
                        await handle_game_state(response, websocket, name)

                elif response["type"] == "trick_end":
                    print(f"[CLIENT LOG] {response['message']}")

            except websockets.ConnectionClosed:
                print("[CLIENT LOG] Connection closed by server")
                break
            except Exception as e:
                print(f"[CLIENT LOG] Unexpected error: {e}")
  

asyncio.get_event_loop().run_until_complete(main())
