
var search_intvl = 12000;
var disp_intvl = 1000;
var search_term = "#fail";
var twtblock = "twtblock";
var maxtwt = 7;
var maxq = 1000;
var baseurl = "http://search.twitter.com/search.json?callback=enqarr&result_type=recent&q=";
var ubase;

var q = new Array(maxq);
var qhead = 0;
var qtail = 0;

var tempScrpt;
var sinceid = 0;
var srchid;
var checkid;
var is_pause = true;

function cntupdate(){
    var cntblock = document.getElementById("counter");
    cntblock.innerHTML = lenq();
}

function toggle_pause(){
    if (is_pause) {
        is_pause = false;
        start();
        document.getElementById("pausebutton").value = "Pause";
    } else {
        is_pause = true;
        pauseme();
        document.getElementById("pausebutton").value = "Start";
    }
}

function pauseme(){
    clearInterval(srchid);
    clearInterval(checkid);
}
function start(){
    var term = document.getElementById("searchterm").value;
    if (search_term != term){
        cleartwts();
        search_term = term;
        clearq();   
        sinceid = 0; 
    }
    ubase = baseurl + escape(search_term);
    getJSON(ubase);
    checkid = setInterval(function(){ addtweet(twtblock); }, disp_intvl);
    searchid = setInterval(function(){ getJSON(ubase) }, search_intvl);
}
function cleartwts(){
    twtb = document.getElementById(twtblock);
    while (twtb.childNodes.length > 0)
        twtb.removeChild(twtb.firstChild);

}

function addtweet(id){
    if (lenq() > 0){
        var twtblock = document.getElementById(id);
        var twt = deq();
        var src = twt.source.replace(/&quot;/gi, "\"").replace(/&gt;/gi,'>').replace(/&lt;/gi,'<').replace('href="','class="twtlink" target="_blank" href="');
        cntupdate();
        var locstr = " via ";
        var divstr = '<div id="tw'+twt.id+'" class="twt"><a class="twtprofile"  title="'+twt.from_user+'" href="http://www.twitter.com/'+twt.from_user+'"><img class="profile" title="'+twt.from_user+'" width="48" height="48" src="'+twt.profile_image_url+'" ></a><div class="twttext"><p class="twttext">'+linkall(twt.text)+'</p><b class="twtlastline"><a class="twtprofile" title="'+twt.from_user+'">'+twt.from_user+'</a></b>&nbsp;&nbsp;<a href="http://twitter.com/'+twt.from_user+'/status/'+twt.id+'" class="twtlink">'+getdatestr(twt.created_at)+'</a>'+locstr+'<span class="src">'+src+'</span></div></div>';
        twtblock.innerHTML = divstr + twtblock.innerHTML;
            swirladdtweet(twt);
        if (maxtwt > 0 && twtblock.childNodes.length > maxtwt){
            twtblock.removeChild(twtblock.lastChild);
        }
    }
}


function getdatestr(strtwtdate){
    var twtdate = new Date(Date.parse(strtwtdate));
    var hr = twtdate.getHours();
    var datestr = padtime(twtdate.getHours()) + ":" + padtime(twtdate.getMinutes()) + ":" + padtime(twtdate.getSeconds());
    /*
    var now = new Date();
    var t;
    if ((t=now.getFullYear() - twtdate.getFullYear()) > 0)
        datestr = "about " + t + " year" + ((t - 1 > 0) ? "s" : "") +" ago";
    else if ((t=now.getMonth() - twtdate.getMonth()) > 0)
        datestr = "about " + t + " month" + ((t - 1 > 0) ? "s" : "") +" ago";
    else if ((t=now.getDate() - twtdate.getDate()) > 0)
        datestr = "about " + t + " day" + ((t - 1 > 0) ? "s" : "") +" ago";
    else if ((t=now.getHours() - twtdate.getHours()) > 0)
        datestr = "about " + t + " hour" + ((t - 1 > 0) ? "s" : "") +" ago";
    else if ((t=now.getMinutes() - twtdate.getMinutes()) > 0)
        datestr = "about " + t + " minute" + ((t - 1 > 0) ? "s" : "") +" ago";
    else if ((t=now.getSeconds() - twtdate.getSeconds()) > 0)
        datestr = "about " + t + " second" + ((t - 1 > 0) ? "s" : "") +" ago";
    else
        datestr = "less than a second ago";
    */
    return datestr;
}

function padtime(s){
    return (s < 10) ? "0"+s : s;
}

function getJSON(url){
    url += "&since_id=" + sinceid;
    url += "&cache-ctl=" + (new Date()).getTime();
    tempScrpt = document.createElement("script");
    tempScrpt.setAttribute("type", "text/javascript");
    tempScrpt.setAttribute("language", "JavaScript");
    tempScrpt.setAttribute("id", "twt-temp");
    tempScrpt.setAttribute("src", url);
    document.getElementsByTagName("head")[0].appendChild(tempScrpt);
}

function enqarr(arrjson){
    sinceid = arrjson.max_id + 1;
    arrjson.results.sort(sorttweet);
    for (var i=0; i<arrjson.results.length; i++){
        if (arrjson.results[i] != "undefined"){
            enq(arrjson.results[i]);
            
            cntupdate();
        }
    }
    document.getElementsByTagName("head")[0].removeChild(tempScrpt);
}

function sorttweet(a, b){
    return  parseInt(a.id) - parseInt(b.id);
}

function enq(json){
    q[qtail] = json;
    qtail ++;
    if (qtail >= maxq) qtail -= maxq;
}

function deq(){
    json = q[qhead];
    qhead ++;
    if (qhead >= maxq) qhead -= maxq;
    return json;
}

function lenq(){
    return (qtail - qhead) < 0 ? qtail - qhead + maxq : qtail - qhead;
}

function clearq(){
    q = new Array(maxq);
    qhead = 0;
    qtail = 0;
}
