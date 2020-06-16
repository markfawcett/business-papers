
/* Portions Copyright (c) 2011 Kaldor Ltd */

  // Set it up  
  function TweetFetcher(options) {
			
	this.tweetList; 
	
	this.nextToFill = 0;
	this.nextIndex = 0;
	this.firstCycle = true;
	
	this.settings = {
	  query: null,
	  accessToken: null,
	  show: null,
	  onLoad: null,
	  onComplete: null,
	  slots: null,
	  offline_from_user: "NewsFlash",
	  offline_text: "Go online to get live tweets",
	  on_success: null
	};
	        
    options && $.extend(this.settings, options);

    this.settings.onLoad != null && typeof this.settings.onLoad == 'function' && this.settings.onLoad();
         
  };
  
  // Create HTML elements
  TweetFetcher.prototype.createTweetElement = function(tweet) {
      if (!tweet) return;
	  var t = $('<div>')
		.addClass('tweet-placeholder')
				
		.attr('id', 1234)
		.append(
		  $('<b>').append(tweet.from_user + " ")
		)
		.append(
		  tweet.text
		);
		t.append(" - " + timeAgo(tweet.created_at));
	  return t;	
  }
    
  // Show the current loaded set
  TweetFetcher.prototype.showAllTweets = function(element) {
  
  		var tweets = this.tweets();
  		if (!tweets) return;
  		
  		element.html("");
  		  
          for(var i = 0; i < tweets.results.length; i++) {

				var tweet = tweets.results[i];
				if (!tweet) return;

				var te = this.createTweetElement(tweet);
				element.append(te);
		}
}
  
  // Get the current list of tweets
  TweetFetcher.prototype.tweets = function() {
  	return this.tweetList;
  }

  // Fetch the next batch
  TweetFetcher.prototype.fetch = function() { 
  
  		var fetcher = this;	

	    if (navigator.onLine) {
		
			     $.ajax({
			               url: "http://search.twitter.com/search.json?q="+ this.settings.query +"&lang=en",
			               type: 'GET',
			               dataType: 'jsonp',
			               timeout: 1000,
			               success: function(json){
								fetcher.tweetList = json;
								
								if (fetcher.tweetList.results.length == 0) {
									fetcher.tweetList =
										{"results":[{
											"created_at": new Date() ,
											"from_user": fetcher.settings.offline_from_user,
											"text": "No tweets available"}]};						
								
								}
								
								if (fetcher.settings.on_success) fetcher.settings.on_success();
			               }
       			 });
		
		} else { if (!this.tweetList) { // Add one? 
		var datestring = new Date();
		this.tweetList =
			{"results":[{
				"created_at": datestring ,
				"from_user": this.settings.offline_from_user,
				"text": this.settings.offline_text}]};						
			}
			if (fetcher.settings.on_success) fetcher.settings.on_success();
	
		}
    }

	// Fill the next slot    
    TweetFetcher.prototype.fillSlot = function() {
    	
    	var tweets = this.tweets();
    	if (!tweets) return;
    	
    	var slotsToFill = this.settings.slots;
    	
    	if (!slotsToFill) return;

		if (this.nextIndex >= tweets.results.length) this.nextIndex = 0;

		var f = $('#' + slotsToFill[this.nextToFill]);
		if (!f) {
			alert('No item with ID ' + slotsToFill[this.nextToFill]);
			return;
		}

		var tweet = tweets.results[this.nextIndex];
		f.html(this.createTweetElement(tweet));

		this.nextToFill++;
		if (this.nextToFill >= slotsToFill.length) {
			this.nextToFill = 0;
			this.firstCycle = false;
		}
		this.nextToFill %= slotsToFill.length;
		this.nextIndex++;

		// If we're just starting, fill all of them			
		if (this.firstCycle) {
			this.fillSlot();
		}
		  
    
    }


/**
 * from twitter's own script:
 * relative time calculator
 * @param {string} twitter date string returned from Twitter API
 * @return {string} relative time like "2 minutes ago"
 */
function timeAgo(dateString) {
    var rightNow = new Date();
    var then = new Date(dateString);
    
    var diff = rightNow - then;
    
    var second = 1000,
    minute = second * 60,
    hour = minute * 60,
    day = hour * 24,
    week = day * 7;
    
    if (isNaN(diff) || diff < 0) {
        return ""; // return blank string if unknown
    }
    
    if (diff < second * 2) {
        // within 2 seconds
        return "right now";
    }
    
    if (diff < minute) {
        return Math.floor(diff / second) + " seconds ago";
    }
    
    if (diff < minute * 2) {
        return "about 1 minute ago";
    }
    
    if (diff < hour) {
        return Math.floor(diff / minute) + " minutes ago";
    }
    
    if (diff < hour * 2) {
        return "about 1 hour ago";
    }
    
    if (diff < day) {
        return  Math.floor(diff / hour) + " hours ago";
    }
    
    if (diff > day && diff < day * 2) {
        return "yesterday";
    }
    
    if (diff < day * 365) {
        return Math.floor(diff / day) + " days ago";
    }
    
    else {
        return "over a year ago";
    }
    
};
