function coord(x, y){
    this.x = x;
    this.y = y;
}
var center = new coord(300, 300); //center of the swirl
var npround = 100.5; //number of tweets per round
var inner_r = 3 * npround; //inner radius of the swirl
var ddist = 1/12;  //radius increase per tweet
var basetwtr = 2; //minimum radius of tweet node
var l = 3210; //total number of tweets
var inctwtr = 3.5/l; //node radius increase per tweet
var minalpha = 0.05;
var maxalpha = 0.5;
var def_color = "rgba(100,100,100,0.1)"; //default color
var select_color = "rgba(254, 54, 20, 1)"; //selected node color
var rt_color = "rgba(104, 79, 248, 1)"; //retweet color on search
var hit_color = "rgba(0, 255, 0, 1)"; //orignals tweet color on search
var highlight_color = "red"; //keyword highlight color in tweet text

var canvas, ctx;
var width, height;
var wordset = [];  //word index, for searching
var twtlist = [];  //list of all tweets
var modlist = [];  //list of tweets with different color than default
var unitang = 2*Math.PI/npround;
var twt_select;    //selected tweet, index in twtlist
var wordsp ='[`!@#$%\\^&*()\\[\\]\\\\\';.,<>? ~:{}"]'; //regex split words
var wordnsp ='[^`!@#$%\\^&*()\\[\\]\\\\\';.,<>? ~:{}"]';
var wordspc = new RegExp(wordsp, "g");
var searchterm;
var is_whole_word;

//tweet class
function tweet(x, y, r, data, color){
    this.coord = new coord(x, y);
    this.x = this.coord.x;
    this.y = this.coord.y;
    this.r = r;
    this.data = data;
    this.color = color;
}


function init(){
    canvas = document.getElementById("swirl");
    width = canvas.width;
    height = canvas.height;
    ctx = canvas.getContext('2d');
}


function getdefcolor(i){
        alpha = minalpha + i / l * (maxalpha - minalpha);
        return def_color.replace(/,[0-9. ]+\)/, ","+alpha.toFixed(2)+")");
}

function drawtweet(twt){
    ctx.beginPath();
    ctx.arc(twt.x, twt.y, twt.r, 0, Math.PI*2, 0);
    ctx.fillStyle = twt.color;
    ctx.fill();
}

function addtweet(twtdata){
    var i = twtlist.length;

    var x = (i + inner_r) * Math.cos(i*unitang)*ddist+center.x;
    var y = (i+inner_r)*Math.sin(i*unitang)*ddist+center.y;
    var r = basetwtr + i * inctwtr;

    twtlist[i] = new tweet(x,y,r,twtdata,getdefcolor(i));

    //extract words for indexing
    var wl = twtdata.text.toLowerCase().split(wordspc);
    for (var j=0; j<wl.length; j++){
        if (wl[j] in wordset)
            wordset[wl[j]][wordset[wl[j]].length]=i;
        else{
            wordset[wl[j]] = new Array();
            wordset[wl[j]][0] = i;
        }
    }

    //select latest tweet
    twt_select = i;
    drawtweet(twtlist[i]);
}


function getdatestr(s){
    return s.replace(" +0000", "");
}

//format twt.data for display
function fmttwt(twt){
    if (is_whole_word)//if search for whole word, match whole word
        kwreg = new RegExp("("+wordsp+")(" + searchterm + ")(?="+wordsp+")", "gi");
    else //match word beginning
        kwreg = new RegExp("(" + wordsp + ")(" + searchterm + wordnsp +"*)", "gi");
    var twt = twt.data;
    return '<table><tr><td><a class="twtprofile"  title="'+twt.from_user+'" href="http://www.twitter.com/'+twt.from_user+'"><img class="profile" title="'+twt.from_user+'" width="48" height="48" src="'+twt.profile_image_url+'" ></a></td><td><div class="text"><p class="text">'+ (searchterm ? linkall((" "+twt.text+" ").replace(kwreg, "$1<font color="+highlight_color+">$2</font>")) : linkall(twt.text)) +'</p><b class="lastline"><a class="twtlink" href="http://www.twitter.com/'+twt.from_user+'" title="'+twt.from_user+'">'+twt.from_user+'</a></b>&nbsp;&nbsp;<a href="http://twitter.com/'+twt.from_user+'/status/'+twt.id+'" class="twtlink">'+getdatestr(twt.created_at)+'</a></div></td></tr></table>';
}

function linkall(twttext){
    return linkusers(linkhash(linkaddr(String(twttext))));
}

function linkusers(twttext){
    return twttext.replace(/[@]+[A-Za-z0-9-_]+/g, function(us) 
            {
                var username = us.replace("@","");
                us = us.link("http://twitter.com/"+username);
                us = us.replace('href="','class="twtlink"  title="'+username+'"  href="');
                return us;
            });
};

function linkhash(twttext){
    return twttext.replace(/[#]+[A-Za-z0-9-_]+/g, function(t) 
            {
                var tag = t.replace("#","%23");
                t = t.link("http://search.twitter.com/search?q="+tag);
                t = t.replace('href="','class="twtlink" href="');
                return t;
            });
}; 

function linkaddr(twttext){ 
    return twttext.replace(/[A-Za-z]+:\/\/[A-Za-z0-9-_]+\.[A-Za-z0-9-_:%&\?\/.=]+/g, function(m) 
            {
                m = m.link(m);
                m = m.replace('href="','class="twtlink" href="');
                return m;
            });
};


//draw all the tweets
function draw(){
    for (i=0; i<twtlist.length; i++){
        if (i == twt_select){
            orig_color = twtlist[i].color;
            twtlist[i].color = select_color;
            drawtweet(twtlist[i]);
            twtlist[i].color = orig_color;
        } else 
            drawtweet(twtlist[i]);
    }
}

//clean canvas, reset modlist
function clear(){
    for (i=0; i<modlist.length; i++)
        twtlist[modlist[i]].color = getdefcolor(modlist[i]);
    modlist = [];
    ctx.clearRect(0, 0, width, height);
}

//grab cursor coordination in coord of canvas
function getmscoord(e){
    var x;
    var y;
    //handle scroll offset
    if (e.pageX || e.pageY) {
        x = e.pageX;
        y = e.pageY;
    }
    else {
        x = e.clientX + document.body.scrollLeft +
            document.documentElement.scrollLeft;
        y = e.clientY + document.body.scrollTop +
            document.documentElement.scrollTop;
    }

    //handle canvas offset and all parents offset
    x -= canvas.offsetLeft;
    y -= canvas.offsetTop;
    var element = canvas.offsetParent;
    while (element !== null) {
        x = parseInt (x) - parseInt (element.offsetLeft);
        y = parseInt (y) - parseInt (element.offsetTop);

        element = element.offsetParent;
    }
    return new coord(x, y);
}

function sqdist(c1, c2){
    return (c1.x - c2.x)*(c1.x-c2.x)+(c1.y-c2.y)*(c1.y-c2.y);
}

//get the tweet node closest to a given coord
function getneartwt(mscrd){
    neartwt = -1;
    mindist = 99999999;
    for (var i=0; i<twtlist.length; i++){
        d = sqdist(twtlist[i].coord, mscrd);
        if (d < mindist){
            neartwt = i;
            mindist = d;
        }
    }
    return neartwt;
}

//display selected tweet
function show_selected_twt(){
    document.getElementById("twt-display").innerHTML = fmttwt(twtlist[twt_select]);
}

//select tweets near cursor position when clicked
function cclick(e){
    select(getneartwt(getmscoord(e)));
}

//select tweet by index in twtlist
function select(ntwt){
    twt_select = ntwt; 
    ctx.clearRect(0, 0, width, height);
    draw();
    show_selected_twt();
}

function is_rt(twt){
    return twt.data.text.substring(0,3).toLowerCase() == "rt "
}

//search tweet, called when search input field changed (onkeyup)
function searchtwt(e){
    var keynum, twt;
    var searchbar = document.getElementById("twtsearchinput");
    if (window.event)
        keynum = e.keyCode;
    else if (e.which)
        keynum = e.which;
    is_whole_word = (keynum == 32);
    searchterm = searchbar.value;

    clear();
    latest_search = 0;


    function searchwordterm(term){    
        for (var i=0; i<wordset[term].length; i++){
            twt = twtlist[wordset[term][i]];
            //find latest tweet in search results
            if (wordset[term][i] > latest_search)
                latest_search = wordset[term][i]
                    twt.color = is_rt(twt) ? rt_color : hit_color;
            modlist[modlist.length] = wordset[term][i];
        }
    }
    if (is_whole_word){ //search for whole word
        searchterm = searchterm.replace(/\s+$/g, '');
        if (searchterm in wordset)
            searchwordterm(searchterm);
    } else {
        //search for words start with search term
        for (term in wordset)
            if (term && searchterm && term.length >= searchterm.length && 
                    term.substring(0, searchterm.length) == searchterm){
                searchwordterm(term);
            }
    }
    //if return pressed, clear search field
    if (keynum == 13)
        searchbar.value = "";
    //select latest tweet in search results
    if (latest_search)
        twt_select = latest_search;
    draw();
    if (twt_select)
        show_selected_twt();
}

