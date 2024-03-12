function checkPlaying(og_trackname, og_artist) {
    fetch('/check')
        .then(response => response.json())
        .then(data => {
            if (data.trackname != og_trackname || data.artist != og_artist){
                window.location.reload();
            }
        });
}