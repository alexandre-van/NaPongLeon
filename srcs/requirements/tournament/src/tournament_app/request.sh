curl -X POST http://localhost:8000/api/game_manager/create_game_api/ \
-H "Content-Type: application/json" \
-d '{
  "gameMode": "PONG_CLASSIC",
  "modifiers": "",
  "playersList": ["player1", "player2"],
  "teamsList": [["player1"], ["player2"]],
  "ia_authorizes": false
}'