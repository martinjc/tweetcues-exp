var tweetsUrl = root_url + "get_tweets/";

$(document).ready(function() {
    get_tweets();
});
// calls the analysis url to do analysis of user tweets
// then inserts instruction text into the start page and
// activates the "start quiz" button
function get_tweets() {
    // calls get on the url
    $.get(tweetsUrl, function(data) {
        // inserts data returned from analysis url into 'progress' div
        $("#progress").html(data);
        // activates the "start quiz" button
        document.getElementById("sb").disabled = false;
        $(".disabled").removeClass("disabled");
    });
}
