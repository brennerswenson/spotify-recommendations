import os
import sys
from json.decoder import JSONDecodeError

import spotipy.oauth2
import spotipy.util as util
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from DSfunctions import *


def main(playlist_id, username):
    all_results = dict()
    scope = 'user-library-read'
    client_id = os.environ['SPOTIPY_CLIENT_ID']
    client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
    redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']

    try:
        token = util.prompt_for_user_token(username, scope, client_id,
                                           client_secret, redirect_uri)
    except (AttributeError, JSONDecodeError):
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username, scope, client_id,
                                           client_secret, redirect_uri)

    sp = spotipy.Spotify(auth=token)  # create spotify object

    all_results = get_user_owned_playlist_contents(username, token, all_results, sp)[0]  # get playlist contents

    all_results, df_master = get_user_saved_songs(username, token, all_results, sp)  # get user saved songs

    all_results, df_master = get_deep_song_info(all_results, df_master, username, token,
                                                sp)  # get deep song info from combined songs

    albums_df, df_master = get_album_info(df_master, username, token,
                                          sp)  # get album info for all unique albums from df_master

    artists_df, df_master = get_artist_info(df_master, username, token,
                                            sp)  # get artist info for all unique artists from df_master
    df_features = clean_data(df_master)  # clean data and return df with more features

    # initial train test split, need to incorporate into a pipeline
    X_train, X_test = train_test_split(df_features, test_size=0.01)

    # need to regularise data, scale and normalise. not sure the best way to do it
    X_train_scaled = StandardScaler().fit_transform(X_train)

    # create a dataframe from the scaled data
    X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)

    # EXPLORE ALGORITHM OPTIONS!

    pca_obj = PCA(n_components=50).fit(X_train_scaled)  # create trained PCA object

    PCA_df = pd.DataFrame(pca_obj.fit_transform(X_train_scaled))  # create df of scaled PCA data

    km = KMeans(n_clusters=500).fit(PCA_df)  # create KMeans classifier fit on the PCA_df

    # need to regularise data, scale and normalise. not sure the best way to do it
    X_test_scaled = StandardScaler().fit_transform(X_test)

    # create a dataframe from the scaled data
    X_test_scaled = pd.DataFrame(
        X_test_scaled, columns=X_test.columns, index=X_test.index)

    # training dataset

    train_labels = km.labels_  # classifications from the training data

    test_pca_obj = pca_obj.transform(X_test_scaled)  # create test pca object

    test_labels = km.predict(test_pca_obj)  # predict and get labels

    test_pca_df = pd.DataFrame(test_pca_obj)  # create df of test data

    test_pca_df['CENTROID'] = test_labels  # add new column to the test df with the centroid the KMeans predicted

    PCA_df['CENTROID'] = train_labels  # add new column to the test df with the centroid the KMeans predicted

    train_centr_freq = label_comparison(train_labels)
    test_centr_freq = label_comparison(test_labels)

    test_freq_df = pd.DataFrame(test_centr_freq)  # create df of the frequency data

    train_freq_df = pd.DataFrame(train_centr_freq)  # create df of the frequency data

    top_clusters = train_freq_df.sort_values(
        2, ascending=False)[1].values  # top ten clusters

    X_test['CENTROID'] = test_labels  # assign centroid labels to the test data df

    import pdb
    pdb.set_trace()

    # get all songs from selected playlist
    playlist_results, playlist_df = get_playlist_tracks(username, playlist_id, sp)

    # get deep song info from playlist songs
    playlist_results, playlist_df = get_deep_song_info(playlist_results, playlist_df, username, token, sp)

    # get album info for all songs in that playlist
    playlist_results, playlist_df = get_album_info(playlist_df, username, token, sp)

    # get artist info for all songs in that playlist
    playlist_results, playlist_df = get_artist_info(playlist_df, username, token, sp)

    df_playlist_features = clean_data(playlist_df)  # return a cleaned df with more features

    df_playlist_features = make_dfs_comparable(df_features,
                                               df_playlist_features)  # make df playlist columns match training data

    # create a dataframe from the scaled data
    playlist_scaled = StandardScaler().fit_transform(df_playlist_features)
    playlist_scaled = pd.DataFrame(
        playlist_scaled,
        columns=df_playlist_features.columns,
        index=df_playlist_features.index)  # create df from scaled test data

    playlist_pca_obj = pca_obj.transform(playlist_scaled)  # create pca object from playlist data

    playlist_labels = km.predict(playlist_pca_obj)  # classify on playlist songs

    playlist_pca_df = pd.DataFrame(playlist_pca_obj)  # convert predictions into a df

    playlist_pca_df['CENTROID'] = playlist_labels  # assign centroid number to pca df

    df_playlist_features['CENTROID'] = playlist_labels  # add centroid to original features df

    res = df_playlist_features[(df_playlist_features['CENTROID'].isin(top_clusters)) & (
        ~df_playlist_features.index.isin(df_features.index))]  # SONGS THAT MATCH THE CLASSIFIER

    print(res)
    return res


if __name__ == '__main__':
    main(playlist_id=sys.argv[1], username=sys.argv[2])
