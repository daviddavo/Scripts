#/bin/bash/sh
for playlist in ~/MovilMusica/Playlists/*.m3u; do
   beet mod -y playlist:"$playlist" onplaylist=true
done 
