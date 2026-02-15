#!/bin/bash

user_ids=("user-101" "user-202" "user-303" "user-404")
amounts=(1000 5000 9000 1500)

for i in $(seq 1 1000000); do
  uid=${user_ids[$RANDOM % ${#user_ids[@]}]}
  amt=${amounts[$RANDOM % ${#amounts[@]}]}

  curl -s -w "\nTotal time: %{time_total}\n" \
    -X POST http://:172.19.30.208:30081/transaction \
    -H "Content-Type: application/json" \
    -d "{
          \"user_id\": \"$uid\",
          \"amount\": $amt,
          \"country\": \"IN\",
          \"merchant\": \"amazon\"
        }"

  echo "---- Request $i completed ----"
done
