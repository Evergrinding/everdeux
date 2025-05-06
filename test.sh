curl --request POST \
    --url http://localhost:8080/completion \
    --header "Content-Type: application/json" \
    --data '{
        "prompt": "Building a website can be done in 10 simple steps:",
        "n_predict": 128,
        "temperature": 0.7,
        "speculative_mode": true
    }'