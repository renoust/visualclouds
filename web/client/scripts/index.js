$(function() {

    $('#submitSearch').on('click', myVsearch.searchRequest);

    $('#kdInput').submit(function() {
        setTimeout(myVsearch.searchRequest, 20);
        return false;
    }).find('input').focus();

    let myFaceInput = $('#faceInput'); 
    myFaceInput.submit(function() {
        setTimeout(myVsearch.searchRequest, 20);
        return false;
    })

    $('.tl').on("click", function() {
        if (myVsearch.hasData) {
            $(this).siblings().removeClass('active');

            if (this.id !== 'hd') {
                $(this).addClass('active');
            }
        }
        try {
            windowControl.changeWindow(this.id);
        } catch (e) {
            console.log(e);
        }
    })
    
    let topEle = document.getElementById('searchResult');
    let isVpSticky = false;
    let myVideoPlayer = $('#vpBoard');
    const TOP_BOARD = 120;
    
    window.onscroll = function() {
       
        var ReTop = topEle.getBoundingClientRect().top;

        if (ReTop < TOP_BOARD && !isVpSticky) {
            isVpSticky = true;
            // myVideoPlayer.removeClass('moveVp').addClass('stickyVp');
            myVideoPlayer.addClass('stickyVp')
        } else if (ReTop > TOP_BOARD && isVpSticky) {
            isVpSticky = false;
            // myVideoPlayer.removeClass('stickyVp').addClass('moveVp');
            myVideoPlayer.removeClass('stickyVp')
        }
    }

    utilObj.addEvent("pf1", "click", pageBar.previousPage);
    utilObj.addEvent("pf2", "click", pageBar.nextPage);
    
    pageBar.initPageNum();

    myTimeline = myTimeline.initial();

    searchBox.initial();

    reOrderList.initial();

    sidebarPane.initial();

    popModal.initial();

    clickedTermsBox.initial();

    utilObj.requestData('/face', {}, function(data) {
        let tempArr = [];
        myVsearch.faceData = data;
        for (let oneFace in data) {
            tempArr.push({
                'title': oneFace,
                'image': 'server/data/sface/' + oneFace + '.jpg',
                // "description": "Optional Description"
            });
        };
        myFaceInput.search({
            source: tempArr,
            maxResults: 50
        });
    }, true);
});
