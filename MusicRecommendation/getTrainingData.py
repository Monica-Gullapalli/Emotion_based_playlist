import pandas
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import csv

def searchForTracks(sp):
    try:
        dataset = pandas.read_csv("tagMoods.csv")
        tracksForData = []
        for i, row in dataset.iterrows():
            results = sp.search(q=f"track:{row['title']} artist:{row['artist']}", type='track', limit=1)
            time.sleep(1)  # Delay calls to API to avoid rate limits
            items = results['tracks']['items']
            if items:
                if items[0]['artists'][0]['name'].lower() == row['artist'].lower():
                    tracksForData.append([items[0]['id'], row['mood']])
                    print(f"Found: {items[0]['name']} by {items[0]['artists'][0]['name']}")
            else:
                print("No results found.")
        
        with open('tracksInSpotify.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            for data in tracksForData:
                writer.writerow(data)
        print("File tracksInSpotify.csv written successfully.")
    except Exception as e:
        print(f"Error in searchForTracks: {e}")

def getAudioFeatures(sp):
    try:
        dataset = pandas.read_csv("tracksInSpotify.csv")
        tracks = [item[0] for item in dataset.values]
        featuresTotal = []
        max_calls = 100  # Spotify limits batches of track features to 100

        for i in range(0, len(tracks), max_calls):
            audioFeatures = sp.audio_features(tracks[i:i + max_calls])
            time.sleep(1)  # Delay calls to avoid rate limits
            for feature in audioFeatures:
                if feature:
                    features = [feature['danceability'], feature['energy'], feature['valence']]
                    featuresTotal.append(features)
                else:
                    featuresTotal.append([None, None, None])  # Handle tracks with no audio features

        return dataset.values.tolist(), featuresTotal
    except Exception as e:
        print(f"Error in getAudioFeatures: {e}")
        return [], []
    
def mergeDatasets():
    try:
        # Load the first dataset
        dataset1 = pandas.read_csv("songMoods.csv")

        # Load the second dataset
        dataset2 = pandas.read_csv("data_moods.csv")



        # Select only the relevant columns from the second dataset
        relevant_columns = ['id', 'danceability', 'energy', 'valence', 'mood']
        dataset2 = dataset2[relevant_columns]

        # Append the second dataset to the first
        combined_dataset = pandas.concat([dataset1, dataset2], ignore_index=True)

        # Save the combined dataset to a new CSV file
        combined_dataset.to_csv("combinedDataset.csv", index=False)
        print("Combined dataset saved successfully.")
    except Exception as e:
        print(f"Error in mergeDatasets: {e}")

def writeToCSV(data, features):
    try:
        header = ["id", "danceability", "energy", "valence", "mood"] 
        with open('songMoods.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header) 
            for i, feature in enumerate(features):
                line = [data[i][0]] + feature + [data[i][1]]
                writer.writerow(line)
        print("File songMoods.csv written successfully.")
    except Exception as e:
        print(f"Error in writeToCSV: {e}")

def main():
    scopes = ' '.join([
    "user-read-recently-played",
    "user-top-read",
    "user-library-modify",
    "user-library-read",
    "user-read-private",
    "playlist-read-private",
    "playlist-modify-public",
    "playlist-modify-private",
    "user-read-email",
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
    "app-remote-control",
    "streaming",
    "user-follow-read",
    "user-follow-modify"
])
    
    # Replace with your actual details from the Spotify Developer Dashboard
    client_id = '9b4fa44db96848d7bc756454a2bd90d3'
    client_secret = '7f951b5f31e04f399b80d131e1689f3f'
    redirect_uri = 'https://www.google.com/'
    
    # Setting up the Spotify OAuth object
    sp_oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scopes
    )
    
    # Getting the authorization URL
    auth_url = sp_oauth.get_authorize_url()
    print("Please go to this URL and authorize access:", auth_url)
    
    # This is the part that's going to be manual in Colab
    response_url = input("Paste the full redirect URL here: ")
    
    # Extracting the code from the response URL
    code = sp_oauth.parse_response_code(response_url)
    
    # Exchange the code for a token
    token_info = sp_oauth.get_access_token(code, as_dict=True)
    
    # Creating a Spotify client with the access token
    sp = spotipy.Spotify(auth=token_info['access_token'], )
    
    # Now we can proceed with the rest of the script
    searchForTracks(sp)
    data, features = getAudioFeatures(sp)
    writeToCSV(data, features)
    mergeDatasets()

if __name__ == '__main__':
    main()
