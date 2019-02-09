import matplotlib

matplotlib.use('TkAGG')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from funcy import chunks


def get_user_owned_playlist_contents(username, token, all_results, sp):
    """
    Function to get all songs from spotify playlists created by user

    Args:
        username (str): Spotify username
        token (str): Spotify api session token
        all_results (dict): empty dictionary
        sp: (Spotify object): Spotify API session object

    Returns:
        all_results (dictionary): dictionary with songs as keys and metadata as values
        df_master (Pandas DataFrame): DataFrame of all_results dictionary
    """

    # GET USER'S PLAYLISTS' CONTENTS

    if token:
        # get all user's created playlists
        playlists = sp.user_playlists(username)
        # iterate through all of the playlists
        for playlist in playlists['items']:

            # filter only for playlists where the user is the owner, and filtering out some non-applicable playlists
            if (playlist['owner']['id'] == username) & (
                    'Archive' not in playlist['name']):
                tracks = sp.user_playlist(
                    username, playlist['id'], fields="tracks,next")['tracks']

                tracks_total = tracks['items']

                while tracks['next']:
                    tracks = sp.next(tracks)  # get next page of tracks
                    tracks_total.extend(tracks['items'])  # extend master list

                for i in range(len(tracks_total)):
                    # pdb.set_trace()
                    # get features/attributes of worth
                    song_id = tracks_total[i]['track']['id']

                    all_results[song_id] = {
                        'song_name':
                            tracks_total[i]['track']['name'],
                        'duration_ms':
                            tracks_total[i]['track']['duration_ms'],
                        'artist_name':
                            tracks_total[i]['track']['artists'][0]['name'],
                        'artist_id':
                            tracks_total[i]['track']['artists'][0]['id'],
                        'album_id':
                            tracks_total[i]['track']['album']['id'],
                        'album_name':
                            tracks_total[i]['track']['album']['name'],
                        'release_date':
                            tracks_total[i]['track']['album']['release_date'],
                        'popularity':
                            tracks_total[i]['track']['popularity'],
                        'explicit':
                            tracks_total[i]['track']['explicit']
                    }

        df_master = pd.DataFrame(all_results).T

        df_master = df_master.dropna()

        return all_results, df_master

    else:
        print("Can't get saved songs for", username)


def get_user_saved_songs(username, token, all_results, sp):
    """
    Function to get all songs saved by a user

    Args:
        username (str): Spotify username
        token (str): Spotify api session token
        all_results (dict): dictionary with songs from get_user_owned_playlist_contents()
        sp: (Spotify object): Spotify API session object

    Returns:
        all_results (dictionary): dictionary with songs as keys and metadata as values, updated with saved songs
        df_master (Pandas DataFrame): DataFrame of all_results dictionary
    """

    if token:

        # GET USER'S SAVED SONGS

        saved_songs = sp.current_user_saved_tracks()  # get user's saved tracks
        saved_songs_total = saved_songs['items']  # strip out the items

        while saved_songs['next']:
            saved_songs = sp.next(saved_songs)  # get next page of tracks
            saved_songs_total.extend(
                saved_songs['items'])  # extend master list

        for i in range(len(saved_songs_total)):
            song_id = saved_songs_total[i]['track']['id']  # get song id
            # pdb.set_trace()
            if song_id not in all_results.keys(
            ):  # only get info for songs that aren't already in the list

                all_results[song_id] = {
                    'song_name':
                        saved_songs_total[i]['track']['name'],
                    'duration_ms':
                        saved_songs_total[i]['track']['duration_ms'],
                    'artist_name':
                        saved_songs_total[i]['track']['artists'][0]['name'],
                    'artist_id':
                        saved_songs_total[i]['track']['artists'][0]['id'],
                    'album_id':
                        saved_songs_total[i]['track']['album']['id'],
                    'album_name':
                        saved_songs_total[i]['track']['album']['name'],
                    'release_date':
                        saved_songs_total[i]['track']['album']['release_date'],
                    'popularity':
                        saved_songs_total[i]['track']['popularity'],
                    'explicit':
                        saved_songs_total[i]['track']['explicit']
                }

        # create dataframe from song data
        df_master = pd.DataFrame(all_results).T

        df_master = df_master.dropna()

        return all_results, df_master

    else:
        print("Can't get token for", username)


def get_deep_song_info(all_results, df_master, username, token, sp):
    """
    Get deep audio features for every song

    Args:
        all_results (dict): dictionary with songs from get_user_owned_playlist_contents()
        df_master (DataFrame): DF of all_results
        username (str): string of spotify username
        token (str): Spotify api session token
        sp: (Spotify object): Spotify API session object

    Returns:
        all_audio_features (dictionary): dictionary with songs as keys and deep song features as values
        df_master (Pandas DataFrame): df_master merged with deep audio features
    """
    if token:

        all_audio_features = dict()  # results dict for deep features

        # iterate through song ids in batches of 45
        for id_batch in chunks(45, all_results.keys()):
            # get audio features for batch
            try:
                batch_audio_features = sp.audio_features(id_batch)

                # create dictionary of song ids and features
                temp_dict = dict(zip(id_batch, batch_audio_features))

                # update main dictionary with results
                all_audio_features.update(temp_dict)
            except AttributeError:
                print('ERROR AT {}'.format(id_batch))
                continue

        # columns to drop
        drop_columns = [
            'duration_ms', 'type', 'analysis_url', 'track_href', 'uri', 'id'
        ]

        # create df from deep features and drop columns
        audio_features_df = pd.DataFrame(all_audio_features).T.drop(
            drop_columns, axis=1)

        # merge main df with deep df
        df_master = df_master.join(audio_features_df, on=df_master.index)
        return all_audio_features, df_master
    else:
        print("Can't get token for", username)


def get_album_info(df_master, username, token, sp):
    """
    Get album info for every song in df_master

    Args:
        df_master (DataFrame): DF returned from get_deep_song_info()
        username (str): string of spotify username
        token (str): Spotify api session token
        sp: (Spotify object): Spotify API session object

    Returns:
        albums_df (Pandas DataFrame): df with all album metadata/features
        df_master (Pandas DataFrame): df_master merged with albums_df/features
    """
    if token:

        all_albums = dict()  # results dict for album features

        # iterate in batches
        for album_id_batch in chunks(20, df_master['album_id']):
            try:
                batch_albums = sp.albums(album_id_batch)  # get albums
                batch_albums = batch_albums['albums']  # only pull out album info
                # iterate thorugh album ids
                for i, album_id in enumerate(album_id_batch):
                    # get only attributes of desire
                    all_albums[album_id] = {
                        'record_label': batch_albums[i]['label'],
                        'album_popularity': batch_albums[i]['popularity']
                    }
            except AttributeError:
                print('ERROR AT {}'.format(album_id_batch))
                continue

        # create df of albums data
        albums_df = pd.DataFrame(all_albums).T

        # merge master df with album df
        df_master = df_master.join(albums_df, on='album_id')

        return albums_df, df_master
    else:
        print("Can't get token for", username)


def get_artist_info(df_master, username, token, sp):
    """
    Get artist info for every song in df_master

    Args:
        df_master (DataFrame): DF returned from get_album_info()
        username (str): string of spotify username
        token (str): Spotify api session token
        sp: (Spotify object): Spotify API session object

    Returns:
        artists_df (Pandas DataFrame): df with all artist metadata/features
        df_master (Pandas DataFrame): df_master merged with artists_df/features
    """
    if token:

        all_artists = dict()

        # iterate in batches

        for artist_id_batch in chunks(20, df_master['artist_id'].unique()):
            try:
                batch_artists = sp.artists(artist_id_batch)
                batch_artists = batch_artists['artists']
                for i, artist_id in enumerate(artist_id_batch):
                    # get only attributes that are needed
                    all_artists[artist_id] = {
                        'artist_followers': batch_artists[i]['followers']['total'],
                        'artist_genres': batch_artists[i]['genres'],
                        'artist_popularity': batch_artists[i]['popularity']
                    }
            except AttributeError:
                print('ERROR AT {}'.format(artist_id_batch))

        # create df of artists data
        artists_df = pd.DataFrame(all_artists).T
        artists_df['artist_genres'] = artists_df.artist_genres.apply(
            lambda x: [i.replace(' ', '_') for i in x])

        #######################################################################################################

        # merge master df with artists df
        df_master = df_master.join(artists_df, on='artist_id')

        return artists_df, df_master

    else:
        print("Can't get token for", username)


def get_playlist_tracks(username, playlist_id, sp):
    """
    Return tracks and metadata from Spotify playlist by playlist ID

    Args:
        username (str): string of spotify username
        playlist_id (str): string identifying Spotify playlist e.g. '37i9dQZF1DXcBWIGoYBM5M'
        sp: (Spotify object): Spotify API session object

    Returns:
        playlist_results (dictionary): dict with keys as songs and values as metadata
        playlist_df (Pandas DataFrame): df with all songs from playlist
    """
    playlist_results = dict()

    tracks = sp.user_playlist(
        username, playlist_id, fields="tracks,next")['tracks']

    tracks_total = tracks['items']

    while tracks['next']:
        tracks = sp.next(tracks)  # get next page of tracks
        tracks_total.extend(tracks['items'])  # extend master list

    for i in range(len(tracks_total)):
        try:
            # get features/attributes of worth
            song_id = tracks_total[i]['track']['id']

            playlist_results[song_id] = {
                'song_name': tracks_total[i]['track']['name'],
                'duration_ms': tracks_total[i]['track']['duration_ms'],
                'artist_name': tracks_total[i]['track']['artists'][0]['name'],
                'artist_id': tracks_total[i]['track']['artists'][0]['id'],
                'album_id': tracks_total[i]['track']['album']['id'],
                'album_name': tracks_total[i]['track']['album']['name'],
                'release_date': tracks_total[i]['track']['album']['release_date'],
                'popularity': tracks_total[i]['track']['popularity'],
                'explicit': tracks_total[i]['track']['explicit']
            }
            playlist_df = pd.DataFrame(playlist_results).T
        except TypeError:
            print('=> THERE WAS A TYPE ERROR!\n')
            continue
    return playlist_results, playlist_df


def clean_data(df_master):
    '''
    Return cleaned and trimmed dataframe, removing columns
    and creating features in addition to setting consistent datatypes

    Args:
        df_master (pandas DataFrame): df returned from any of functions above

    Returns:
        df_features (pandas DataFrame): df with removed unimportant columns, new features, and dummy variables
    '''
    df_features = df_master.copy(deep=True)  # copy dataframe

    df_features['release_year'] = df_features['release_date'].apply(
        lambda x: x[:4])  # create feature for release year

    df_features = pd.concat(
        [
            df_features,
            pd.get_dummies(df_features['time_signature'], prefix='time_signature')
        ],
        axis=1)  # create dummies for time_signature column

    df_features = pd.concat(
        [
            df_features,
            pd.get_dummies(df_features['artist_name'], prefix='artist_name')
        ],
        axis=1)  # create dummies for artist_name column

    df_features = pd.concat(
        [
            df_features,
            pd.get_dummies(df_features['record_label'], prefix='record_label')
        ],
        axis=1)  # create dummies for artist_name column

    df_features = pd.concat(
        [
            df_features,
            df_master.artist_genres.str.join('|').str.get_dummies().add_prefix(
                'artist_genre_')  # create dummies for all genres
        ],
        sort=False,
        axis=1)

    df_features = pd.concat(
        [df_features,
         pd.get_dummies(df_features['key'], prefix='key')],
        sort=False,
        axis=1)  # create dummies for time signature

    df_features = df_features.drop(
        [
            'release_date', 'song_name', 'time_signature', 'album_name',
            'key', 'record_label', 'album_id', 'artist_id',
            'artist_genres', 'artist_name'
        ],
        axis=1)  # drop all un-needed columns

    df_features = df_features.dropna()  # drop all rows that have at least one null value

    for col in [
        'duration_ms', 'explicit', 'popularity', 'acousticness',
        'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness',
        'mode', 'speechiness', 'tempo', 'valence', 'album_popularity',
        'release_year'
    ]:
        df_features[col] = df_features[col].apply(float)  # ensure that all columns have consistent datatypes

    return df_features


def scree(pca):
    """
    Creates scree plot for pca object

    Args:
        pca (sklearn fit PCA object): fit PCA object with df_features dataframe

    Returns:
        None
    """
    n_comps = len(pca.components_)  # number of components
    x_axis = np.arange(n_comps)  # axis for graph
    comp_vars = pca.explained_variance_ratio_  # variance values per component

    fig, ax = plt.subplots(figsize=(40, 20))
    ax.set_title(
        'Variance Explained by Each Principal Component',
        fontdict={'fontsize': 20})
    ax.set_ylabel('Variance %')
    ax.set_xlabel('Component')
    sns.barplot(
        x_axis,
        comp_vars,
        palette=sns.cubehelix_palette(8, start=.5, rot=-.75),
        ax=ax)
    ax.plot(np.cumsum(comp_vars), marker='o', ms=1, c='black')
    total_var = np.cumsum(comp_vars[:n_comps])


def map_weight_feats(pca_obj, df, component):
    """
    INPUT:
        pca_obj - Fit PCA object
        df - DataFrame with full data
        component - integer (starting at 0) of component
    OUTPUT:
        positive_comp - pandas series with positive weights
        negative_comp - pandas series with negative weights
    """
    w = pd.DataFrame(np.round(pca_obj.components_, 6), columns=df.keys())
    comp = w.iloc[component, :]
    positive_comp = comp[comp > 0].sort_values(ascending=False)
    negative_comp = comp[comp < 0].sort_values(ascending=True)

    return positive_comp, negative_comp


def print_component_weights(pca_obj, df, n_components):
    """
    INPUT:
        pca_obj - Fit PCA object
        df - DataFrame with full data
        n_components - integer number of components to print
    OUTPUT:
        None - function prints out negative and positive component weights
    """

    for i in range(n_components):
        pos_comp_0, neg_comp_0 = map_weight_feats(pca_obj, df, i)

        print('*' * 40)
        print('Positive weights for component {}'.format(i))
        print('*' * 40)
        print(pos_comp_0.head(10))
        print('*' * 40)
        print('Negative weights for component {}'.format(i))
        print('*' * 40)
        print(neg_comp_0.head(10))


def label_comparison(labels):
    """
    INPUT:
        kmeans - sklearn KMeans object (trained and fit)
        labels - array of each data point's assigned cluster
    OUTPUT:
        centr_freq - list of labels, counts, and proportions for each label
    """
    # value counts for each centroid/cluster
    labels_value_counts = np.unique(labels, return_counts=True)
    labels_value_counts = np.array(
        [[x, y]
         for x, y in zip(labels_value_counts[0], labels_value_counts[1])])

    # proportion of data associated with each cluster
    centr_prop = labels_value_counts[:, 1] / labels_value_counts[:, 1].sum()

    # combine the value counts and the proportion of each cluster
    centr_freq = (np.array([[x, y, z] for x, y, z in zip(
        labels_value_counts[:, 0], labels_value_counts[:, 1], centr_prop)]))

    return centr_freq


# adapt earlier function to work with kmeans object
def map_weight_feats_kmeans(kmeans, df, centr):
    """
    INPUT:
        kmeans - Fit KMeans object
        df - DataFrame with full data
        centr - integer of centroid/cluster index
    OUTPUT:
        positive_comp - pandas series with positive weights
        negative_comp - pandas series with negative weights
    """
    # dataframe with cluster weights
    w = pd.DataFrame(np.round(kmeans.cluster_centers_, 6), columns=df.keys())
    # grab cluster of interest by index
    clust = w.iloc[centr, :]
    # sort weights into neg/pos dataframes
    positive_clust = clust[clust > 0].sort_values(ascending=False)
    negative_clust = clust[clust < 0].sort_values(ascending=True)

    return positive_clust, negative_clust


def print_cluster_weights(kmeans, pca_df):
    """
    INPUT:
        kmeans - Fit kmeans object
        pca_df - DataFrame of principal components
        n_components - integer number of clusters to print
    OUTPUT:
        None - function prints out negative and positive cluster weights
    """

    for i in pca_df['CENTROID'].sort_values().unique():
        pos_clust_over, neg_clust_over = map_weight_feats_kmeans(
            kmeans, pca_df.drop('CENTROID', axis=1), i)

        print('*' * 40)
        print('Positive component weights for cluster {}'.format(i))
        print('*' * 40)
        print(pos_clust_over.head(10))
        print('*' * 40)
        print('Negative component weights for cluster {}'.format(i))
        print('*' * 40)
        print(neg_clust_over.head(10))


def feat_distribution_plot(train_centr_freq, test_centr_freq):
    """
    Plot distributions of features across two datasets

    Args:
        train_centr_freq (list): list of labels, counts, and proportions for each label from training set
        test_centr_freq (list): list of labels, counts, and proportions for each label from test set

    Returns:
        None
    """
    fig, axes = plt.subplots(2, 1, figsize=(7, 14))
    sns.barplot(
        x=train_centr_freq[:, 0],
        y=train_centr_freq[:, 2],
        color='blue',
        ax=axes[0])
    sns.barplot(
        x=test_centr_freq[:, 0], y=test_centr_freq[:, 2], color='g', ax=axes[1])
    axes[0].set_title('Train', fontdict={'fontsize': 20})
    axes[1].set_title('Test', fontdict={'fontsize': 20})
    fig.tight_layout()


def make_dfs_comparable(df_features, df_playlist_features):
    """
    Returns dataframe with same columns as the training dataframe

    Args:
        df_features (pandas DataFrame): features df used for training the classifier
        df_playlist_features (pandas DataFrame): playlist features df - from one playlist


    Returns:
        df_playlist_features (pandas DataFrame): df with columns added/removed to match the df_features df
    """

    # need to make sure that the playlist df has the same columns as the training df

    # create dummy columns to match training df, set all values to zero
    for col in np.setdiff1d(df_features.columns, df_playlist_features.columns):
        df_playlist_features[col] = 0

    # compare the other way around, create columns and set their values to zero
    for col in np.setdiff1d(df_playlist_features.columns, df_features.columns):
        df_playlist_features[col] = 0

    # drop columns that appear in the playlist df but not in the training df
    for col in np.setdiff1d(df_playlist_features.columns, df_features.columns):
        df_playlist_features = df_playlist_features.drop(col, axis=1)

    # drop columns that appear in the playlist df but not in the training df
    for col in np.setdiff1d(df_features.columns, df_playlist_features.columns):
        df_playlist_features = df_playlist_features.drop(col, axis=1)

    return df_playlist_features
