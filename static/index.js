$(document).ready(function () {
    $('#keyword').keyup(function (event) {
        if (event.which === 13) {
            showResult()
        }
    });
});

function reload() {
    window.location.reload()
}
function logout(){
    document.cookie='token_give=None'
    reload()
}

function showReview(uid,reviewId, reviewListId) {
    $('#' + reviewListId).empty()

    $.ajax({
        type: "GET",
        url: "/reviews",
        data: {
            'reviewId': reviewId,
        },
        success: function (response) {
            lists = response['reviewList']
            for (let i = 0; i < lists.length; i++) {
                let list = lists[i]
                let content = list['content']
                let time=list['last_modified']
                let reviewuid=list['reviewuid']
                let user=list['usernickname']
                if(user===document.cookie.split(';')[0].split('=')[1]) {
                    let temp = `
                            <li style="white-space:pre;" class="list-group-item">${content} 
                            <div class="timestamp">${time}</div>   
                            <div class="deletereview" onclick="deleteReview(${uid},${reviewuid})">삭제</div></li>                  
                        `
                                    $('#' + reviewListId).append(temp)

                }
                else{
                    let temp = `
                            <li style="white-space:pre;" class="list-group-item">${content} 
                            <div class="timestamp">${time}</div> 
                            `
                                    $('#' + reviewListId).append(temp)

                }
            }
        }
    })
    if ($('#' + reviewId).css("display") == "flex") {
        $('#' + reviewId).hide()
    } else {
        $('#' + reviewId).show()

    }


}
function deleteReview(uid,reviewuid){

    $.ajax({
        type: "DELETE",
        url: "/deleteReview",
        data: {
            'uid':uid,
            'reviewuid': reviewuid,
        },
        success: function (response){
            reload()
            alert('댓글이 삭제되었습니다')
        }
    })

}

function postReview(uid, reviewId, reviewBoxId) {

    if ($('#' + reviewBoxId).css('display') == 'block') {
        $('#' + reviewBoxId).hide()

    } else {
        $('#' + reviewBoxId).show()


    }

}

function createReview(uid, reviewId, storyId, countId, reviewBoxId) {
    if ($('#' + storyId).val().replace(/^\s+|\s+$/g, "").length === 0) {
        alert('내용을 입력해주세요')
        $('#' + storyId).focus()
        return
    }
    $.ajax({
        type: "POST",
        url: "/review",
        data: {
            'uid': uid,
            'reviewId': reviewId,
            'content': $('#' + storyId).val(),
            'user':document.cookie.split(';')[0].split('=')[1]
        },
        success: function (response) {
            alert('등록되었습니다')
            let count = response['count']['review']
            $('#' + storyId).val('')
            $('#' + reviewBoxId).hide()
            $('#' + reviewId).hide()
            $('#' + countId).text("댓글수: " + count)

        }

    })
}

function showResult() {
    $('#nodata').show()
    $('#landresult').empty()


    let opt = $('#order-count').val()
    let keyword = $('#keyword').val()
    $.ajax({
            type: "POST",
            url: "/land",
            data: {
                'opt': opt,
                'keyword': keyword
            },
            success: function (response) {
                let datas
                let gus = response['gu']
                let dongs = response['dong']
                let names = response['name']
                let mode = response['mode']


                if (mode == 0) {
                    datas = gus
                } else if (mode == 1) {
                    datas = dongs
                } else {
                    datas = names
                }

                for (let i = 0; i < datas.length; i++) {
                    let data = datas[i]
                    let count = data['review']
                    let uid = data['uid']
                    let reviewId = 'review' + uid
                    let reviewBoxId = 'reviewBox' + uid
                    let reviewListId = 'reviewList' + uid
                    let countId = 'count' + uid
                    let storyId = reviewId + 'story'
                    let address = data['address']
                    let name = data['name']
                    let tel = data['tel']
                    let status = data['status']
                    let temp = `
                                <div class="card" id="${uid}" >
                                  <h3 class="card-header" onclick=" showReview('${uid}','${reviewId}', '${reviewListId}')">${name}</h3>
                                  <div class="card-body">
                                    <p class="card-title"><strong>주소</strong>: ${address}</p>
                                    <p class="card-text"><strong>연락처</strong>: ${tel}</p>
                                    <p class="card-text"><strong>상태</strong>: ${status}</p>
                                    <p class="card-text reviewcount" id="${countId}">댓글수: ${count}</p>

                                    </div>
                                </div>
                                `
                    let temp2 = `
                                  <div class="card" id="${reviewId}">
                                  <div id="${reviewBoxId}"></div>
                                  <div class="card-header">
                                    <div class="reviewintroduce">${name}에 달린 리뷰</div>
                                    <button class="btn btn-outline-success my-2 my-sm-0" type='button' onclick="postReview('${uid}','${reviewId}','${reviewBoxId}')">댓글등록</button>

                                  </div>
                                  <div id="${reviewListId}">

                                  </div>
                                  </div>

                                `
                    let temp3 =
                        `
                                <div class="reviewBox form-group">
                                <label for="${storyId}">후기를 등록해보세요:</label>
                                <textarea class="form-control" id="${storyId}" rows="3"></textarea>
                                <button class="btn btn-outline-success my-2 my-sm-0" id="postbutton" type='button' onclick="createReview('${uid}','${reviewId}','${storyId}', '${countId}','${reviewBoxId}')">등록</button>
                                </div>
                                `

                    $('#landresult').append(temp)
                    $('#' + uid).append(temp2)
                    $('#' + reviewBoxId).prepend(temp3)
                    $('#' + reviewId).hide()
                    $('#' + reviewBoxId).hide()
                    if (data != null)
                        $('#nodata').hide()

                }
                return

            }
        }
    )

}


