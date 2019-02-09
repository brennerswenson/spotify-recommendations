import os
import sys

import spotipy.oauth2
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from django.contrib.auth.models import User
from spotify_app.models import RecProfile
from hdbscan import HDBSCAN
import hdbscan

from DSfunctions import *


def get_recommendations(username, playlist_id, sp, token, df_features, hdbs, pca_obj):
    """
    :param username: spotify username
    :param playlist_id: selected playlist id
    :param sp: connected spotipy object to get api data
    :param token: token used to verify user info with spotify
    :param df_features: df of features for comparison with recs
    :param hdbs: saved hsbscan object saved from training
    :return: recs - df of recommendations
    """
    print("=> getting playlist tracks for selected playlist \n")
    # get all songs from selected playlist
    playlist_results, playlist_df = get_playlist_tracks(username, playlist_id, sp)

    print("=> getting deep info for selected playlist \n")
    # get deep song info from playlist songs
    playlist_results, playlist_df = get_deep_song_info(playlist_results, playlist_df, username, token, sp)

    print("=> getting album info for selected playlist \n")
    # get album info for all songs in that playlist
    playlist_results, playlist_df = get_album_info(playlist_df, username, token, sp)

    print("=> getting artist info for selected playlist \n")
    # get artist info for all songs in that playlist
    playlist_results, playlist_df = get_artist_info(playlist_df, username, token, sp)

    print("=> cleaning selected playlist data\n")
    df_playlist_features = clean_data(playlist_df)  # return a cleaned df with more features

    df_playlist_features = make_dfs_comparable(df_features,
                                               df_playlist_features)  # make df playlist columns match training data

    # create a dataframe from the scaled data
    playlist_scaled = MinMaxScaler().fit_transform(df_playlist_features)
    playlist_scaled = pd.DataFrame(
        playlist_scaled,
        columns=df_playlist_features.columns,
        index=df_playlist_features.index)  # create df from scaled test data

    playlist_pca_obj = pca_obj.transform(playlist_scaled)

    playlist_pca_df = pd.DataFrame(playlist_pca_obj)

    playlist_labels = hdbscan.approximate_predict(hdbs, playlist_pca_df)  # classify on playlist songs

    df_playlist_features['CENTROID'] = playlist_labels[0]  # add centroid to original features df
    df_playlist_features['PROBABILITY'] = playlist_labels[1]  # add cluster probabilities

    res = df_playlist_features[(~df_playlist_features.index.isin(df_features.index)) & (
            df_playlist_features['CENTROID'] != -1)]  # SONGS THAT MATCH THE CLASSIFIER

    res = res.sort_values(by=['PROBABILITY', 'popularity'], ascending=False)  # sort results by probability, then by pop

    return res


def main(playlist_id, username, token):
    current_user = User.objects.get(username=username)
    sp = spotipy.Spotify(auth=token)  # create spotify object

    try:
        prof_obj = RecProfile.objects.get(user=current_user)
    except RecProfile.DoesNotExist:
        prof = RecProfile()
        prof.user = current_user
        prof.save()
        prof_obj = RecProfile.objects.get(user=current_user)

    if prof_obj.user_has_objects is not True:
        print("=> USING NEW DATA TO MAKE RECOMMENDATIONS \n")
        all_results = dict()

        print('=> getting playlists\n')

        all_results = get_user_owned_playlist_contents(username, token, all_results, sp)[0]  # get playlist contents

        print('=> getting user saved songs\n')
        all_results, df_master = get_user_saved_songs(username, token, all_results, sp)  # get user saved songs

        print('=> getting deep features for songs\n')
        all_results, df_master = get_deep_song_info(all_results, df_master, username, token,
                                                    sp)  # get deep song info from combined songs

        print('=> getting album info\n')
        albums_df, df_master = get_album_info(df_master, username, token,
                                              sp)  # get album info for all unique albums from df_master

        print('=> getting artist info\n')
        artists_df, df_master = get_artist_info(df_master, username, token,
                                                sp)  # get artist info for all unique artists from df_master
        df_features = clean_data(df_master)  # clean data and return df with more features

        # initial train test split, need to incorporate into a pipeline
        X_train = df_features

        # need to regularise data, scale and normalise. not sure the best way to do it
        X_train_scaled = MinMaxScaler().fit_transform(X_train)

        # create a dataframe from the scaled data
        X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)

        print('=> df shape is {}\n'.format(X_train_scaled.shape))

        print('=> fitting PCA obj\n')
        pca_obj = PCA(n_components=0.70).fit(X_train_scaled)

        if pca_obj.n_components_ > 30:
            pca_obj = PCA(n_components=25).fit(X_train_scaled)
            print('=> too many components! re-fitting pca object\n')
        else:
            pass

        print('=> PCA obj has {} components\n'.format(pca_obj.n_components_))

        print("=> variance explained by {}'s pca components {}\n".format(username,
                                                                         sum(pca_obj.explained_variance_ratio_)))

        print("=> fitting data to PCA Object\n")
        PCA_df = pd.DataFrame(pca_obj.fit_transform(X_train_scaled))  # create df of scaled PCA data

        print(X_train_scaled.head())

        print("=> fitting HDBSCAN object\n")
        hdbs = HDBSCAN(prediction_data=True,
                       core_dist_n_jobs=3,
                       min_cluster_size=2).fit(PCA_df)  # create hdbscan classifier fit on the PCA_df

        prof_obj.user_hdbscan = hdbs
        prof_obj.user_pca_obj = pca_obj
        prof_obj.user_df_features_obj = df_features
        prof_obj.user_df_scaled_obj = X_train_scaled
        prof_obj.user_has_objects = True
        prof_obj.user_has_objects = True
        prof_obj.save()

        recs = get_recommendations(username, playlist_id=playlist_id, sp=sp, token=token, df_features=df_features,
                                   hdbs=hdbs, pca_obj=pca_obj)


    else:
        print("=> USING STORED DATA TO MAKE RECOMMENDATIONS\n")
        recs = get_recommendations(username, playlist_id=playlist_id, sp=sp, token=token,
                                   df_features=prof_obj.user_df_features_obj, hdbs=prof_obj.user_hdbscan,
                                   pca_obj=prof_obj.user_pca_obj)

    return recs


if __name__ == '__main__':
    main(playlist_id=sys.argv[1], username=sys.argv[2])
