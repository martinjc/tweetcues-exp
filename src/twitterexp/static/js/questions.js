var tweetsUrl = root_url + 'tweet_embed/';
var imageUrl = root_url + 'static/img/ajax-loader.gif';

// when the page is ready, hide the error bar
$(document).ready(function() {
    // hide the form elements as we work by clicking on a tweet
    $('.forms').hide();
    $('.loader').hide();
    // click on a tweet
    $('.tweet').on("click", tweetClicked);
});

// deal with a user clicking on the tweet information table
function tweetClicked(event) {
    $('.loader').show();
    $('.tweet').off("click", tweetClicked);
    $('.clickable').removeClass('clickable');
    // find out which tweet was clicked on by getting its ID
    var tweetId = event.delegateTarget.id;
    // check the radio button to mark that this tweet was clicked
    $('[name=answer]').filter("[value=" + tweetId + "]").prop("checked", true);
    // show the tweet to the user
    showInfo(tweetId);
}

// retrieve the html to show the tweet and make the 'next question' button visible
function showInfo(tweetId) {
    $.get(tweetsUrl + tweetId + '/', {}, function(data) {
        $('.actual_tweet').html(data);
        $.getScript('//platform.twitter.com/widgets.js', function() {
            // show the submit button so they can move on the next question
            $('.forms').filter('[type="submit"]').show();
            $('.loader').hide();
        });
    });
}

// validate that we have a tweet selected when the user tries to submit the form
function validate(document) {
    // if no button is selected, alert the user by showing the error bar
    if(getCheckedButton(tweetSelection.elements.answer) == null) {
        $('#selectionError').slideDown();
        return false;
    }
    // if the user has now selected a tweet, hide the error bar
    $('#selectionError').slideUp();
    return true;
}

// figures out which button in a form is checked
function getCheckedButton(group, form) {
    if( typeof group == 'string')
        group = form.elements[group];
    for(var i = 0, n = group.length; i < n; ++i)
    if(group[i].checked)
        return group[i];
    return null;
};
