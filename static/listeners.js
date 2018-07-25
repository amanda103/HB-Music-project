"use strict";

function displayRelatedArtists(evt) {
    $.get('/account'), {}, function(data) {
        $('#form').on('click', function(evt) {
            let target = $(evt.target);
        })
    }
}


let form = $('form');

function getRelatedArtists(evt) {
    let target = $(evt.target);
    console.log(target.data('artist-id'));
    if (target.is(".main-artist") ) { // and target does not have class clicked
        // add class to target to indicate that it has been clicked
        let artistId = target.data('artist-id');
        $.get('/related-artists', {'artist_id': artistId}, function(data) {
            let parent = target.parent();
            parent.append(data);
        });
    }

}


form.on('click', getRelatedArtists);