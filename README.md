# Content-Suggesting-System-based-on-the-user-s-personality-and-current-mood-Leisure-Compass
Our project aims to improve content recommendation accuracy by integrating user personality and mood analysis. An advanced neural network model achieved 99.31% testing accuracy, initially focusing on movies and TV shows. User feedback confirmed the system's efficacy and provided insights for future improvements.


## Abstract
The development of digital media on the internet has transformed entertainment consumption, yet consumers still struggle to find content that aligns with their interests and personalities. Traditional recommendation systems, which prioritize popularity or genre, often fall short. This study introduces an innovative approach for more accurate recommendations by incorporating personality profiling and current mood assessment. Our advanced neural network model achieved impressive accuracy rates: 98.82% during training and 99.31% during testing. While currently focused on recommending movies and TV shows, we plan to expand to other media types. Feedback from approximately fifty users confirmed the system's efficacy and provided suggestions for future improvements.

## Introduction

- **Variety of Online Media:** Includes books, TV series, movies, music, articles, and photos.
- **Global Accessibility:** Digital platforms enable global access and sharing of media via the internet.
- **Ease of Access:** Users can access diverse content through social media, online retailers, and streaming services.
- **Personalization Challenge:** Despite the abundance of content, finding personalized material remains difficult.
- **Current Limitations:** Traditional recommendation systems often focus on narrow parameters like media genres or emotional states.
- **Research Question:** Can content recommendations be improved by considering both personality and mood?
- **Proposed Solution:** Our approach examines the user's personality and emotional state to provide personalized recommendations.

## Objectives

- **Identify User Personality:** Use personality questionnaires to gauge user preferences.
- **Detect Current Mood:** Employ AWS Rekognition for mood detection.
- **Content Matching:** Identify and recommend content based on both personality and mood.
- **Recommendation Delivery:** Provide digital content recommendations to users.
- **Data Management:** Store user personality and content data for continuous improvement.

## Research Method

- **System Diagram:** Illustrates the overall architecture of the recommendation system.

### Personality Detection Process:
1. Use a personality questionnaire to identify user personality.
2. Utilize AWS Rekognition for mood detection.
3. Combine mood and personality data as model input.
4. Generate personalized content recommendations via the model.
5. Retrieve recommended movies and TV shows from TMDB via API call.
6. Display recommended content to the user for seamless access.


#### Step 1: Identify user personality

#### Step 2: Detect user mood using AWS Rekognition

#### Step 3: Combine mood and personality data

#### Step 4: Generate personalized recommendations

#### Step 5: Retrieve recommended movies and TV shows from TMDB

#### Step 6: Display recommended content to user

![Screenshot 2024-07-29 121221](https://github.com/user-attachments/assets/3a763efb-e3bd-43fd-8d9f-18d587a537cd)
