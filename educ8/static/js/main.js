$(function() {

  $('#search-form').on('submit', function(e){
    e.preventDefault();
    var search_term = $.trim($('#search-term').val())
    $('#results').empty();
    var statusMessage = $('<p>Searching for ' + search_term + '...</p>').addClass('status-message');
    $('#status').empty().append(statusMessage);
    $('.status-message').fadeIn(1000);
    search()
    var progress = setInterval(function(){
        $('.status-message').animate({
            opacity: 0.40
        }, 1000, function(){
            $('.status-message').animate({
                opacity: 1
            }, 1000)
        })
    }, 2200);
  });  
});

function search() {
    var search_term = $.trim($('#search-term').val())
    $.ajax({
      url: "search/",
      data: { search_term: search_term},
      success: function(json) {
        $('#search-term').val('');
        if (json.hasError) {
            var errorMessage = $('<p>' + json.message + '</p>').addClass('error-message');
            $('#status').empty().append(errorMessage);
            $('.error-message').fadeIn(1000);
        } else {
            showResults(json, search_term);
        }
      },
      error: function(xhr, errmsg, err) {
        console.log(err);
        console.log(xhr);
        console.log(errmsg);
        $('.status-message').fadeOut();
        var errorMessage = $('<p> Sorry, something went wrong. Please try again. </p>').addClass('error-message');
        $('#status').empty().append(errmsg);
        $('.error-message').fadeIn(1000);
      }
    });
};

function showResults(results, search_term) {
    var tweets = [];
    var instagrams = [];

    var statusMessage = $('<p>Latest posts from ' + search_term + ':</p>').addClass('result-message');
    $("#results").empty();
    $('#status').empty().append(statusMessage);
    $('.result-message').fadeIn(1000);
    results.forEach(function (result){
        var resultsListItem = $('<div class="social-post"></div>');
        if (result.source == "Instagram") {
            resultsListItem.attr("id", result.ig_shortcode);
            $("#results").append(resultsListItem);
            instagrams.push(result.ig_shortcode);
        } else if (result.source == "Twitter") {
            resultsListItem.attr("id", result.post_id);
            $("#results").append(resultsListItem);
            tweets.push(result.post_id);
        };
    });

    instagrams.forEach(function(instagram){
        addIGOembed(instagram, instagrams);
    });

    tweets.forEach(function(tweet){
        displayTweet(tweet);
    });
};

var addIGOembed = function(instagram, instagram_ids) {
    $.ajax({
        url: 'http://api.instagram.com/oembed?url=http://instagr.am/p/' + instagram + '/&omitscript=true',
        type: 'GET',
        cache: false,
        dataType: 'jsonp',
        success: function(data){
        $('#'+ instagram).append(data.html);
        instgrm.Embeds.process();
        },
        error: function(){
          console.log('error');
        }
    });
};

var displayTweet = function(tweet_id) {
    twttr.widgets.createTweet(
      tweet_id,
      document.getElementById(tweet_id),
      {
        conversation: 'none'
      }
      );
  };

// Form post security script. Source: https://gist.github.com/broinjc/db6e0ac214c355c887e5
// This function gets cookie with a given name
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

/*
The functions below will create a header with csrftoken
*/

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
