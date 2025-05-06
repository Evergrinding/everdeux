curl --request POST \
    --url http://localhost:8080/completion \
    --header "Content-Type: application/json" \
    --data '{
        "prompt": "Imagine two significant, near-future advancements occur simultaneously by 2040:\n\n    Mature Level 5 Autonomous Vehicles: Fully autonomous cars requiring no human oversight are widely deployed in major cities globally.\n\n    Personalized Predictive Health Monitors: Widely adopted wearable or implantable devices constantly monitor biomarkers and use AI to predict potential serious health issues (like specific cancers or heart attacks) with 85% accuracy several months in advance.\n\nAnalyze the complex interplay and potential second-order consequences of these two technologies co-existing. Focus specifically on:\n\na)  How might urban planning and city infrastructure need to radically adapt beyond just changes to roads? Consider land use, emergency services routing/response, and the design of public/pedestrian spaces.\nb)  What new ethical dilemmas or societal tensions might arise specifically from the combination of these two technologies (not just each one individually)? Consider data privacy intersections, insurance models, impacts on individual autonomy/behavior, and potential inequalities exacerbated by the combination.\nc)  Propose one novel service or business model that could only exist effectively due to the synergistic interaction of both widespread autonomous vehicles and pervasive predictive health monitoring.\n\nResponse:",
        "n_predict": 1024,
        "temperature": 0.7,
        "speculative_mode": true,
        "top_k": 40,
        "top_p": 0.9
    }'